/* Retained verbatim from Leviidev/Henge source commit 9aa4b6dbe10f23fb937941050b6934f695d20f3d.
   Instant Resume GPU quiesce and cursor/screen restoration. GPL-2.0-or-later.
   Included only after custom multi-display reconciliation. */
@interface HvReplay (Resume)
- (void)page:(HvObject *)o toGuest:(BOOL)down task:(uint32_t)task blit:(id<MTLBlitCommandEncoder> *)blit commandBuffer:(id<MTLCommandBuffer>)cb;
@end

/* Instant resume: the CPUs are stopped. Finish what the guest handed over, then copy what only the GPU holds (it drew
   into private memory and the guest has not asked for it back) into guest memory, where a replay made after a restore
   reads it from. A texture in a heap goes with its heap's bytes, as the heap is what is made again from guest memory. */
void hv_pvg_metal_quiesce(HvPvgMetal *m) {
    if (!m) return;
    HvReplay *r = (__bridge HvReplay *)m;
    @autoreleasepool {
        dispatch_sync(r->worker, ^{});
        dispatch_group_wait(r->completions, DISPATCH_TIME_FOREVER);
        dispatch_sync(r->worker, ^{
            id<MTLCommandBuffer> cb = nil;
            id<MTLBlitCommandEncoder> blit = nil;
            unsigned copied = 0;
            for (NSNumber *task in r->tasks) {
                NSMutableDictionary<NSNumber *, HvObject *> *objs = r->tasks[task];
                for (NSNumber *ref in objs) {
                    HvObject *o = objs[ref];
                    if (!o->guest_backed || !o->host_valid || !o->guest_stale) continue;
                    if (o->parent && o->parent->heap_whole) continue;
                    if (!cb) cb = [r->queue commandBuffer];
                    [r page:o toGuest:YES task:task.unsignedIntValue blit:&blit commandBuffer:cb];
                    o->guest_stale = NO;
                    copied++;
                }
            }
            [blit endEncoding];
            if (cb) {
                [cb commit];
                [cb waitUntilCompleted];
            }
            fprintf(stderr, "hengevm: pvg-metal: quiesced, %u GPU-only objects copied to guest memory\n", copied);
        });
        dispatch_group_wait(r->completions, DISPATCH_TIME_FOREVER);
    }
}

typedef struct DisplayState {
    uint64_t on_screen;
    uint32_t cursor_w, cursor_h, cursor_stride, cursor_shown;
    int32_t hot_x, hot_y;
} DisplayState;

size_t hv_pvg_metal_display_state(HvPvgMetal *m, void *out, size_t cap) {
    HvReplay *r = (__bridge HvReplay *)m;
    __block size_t need = 0;
    dispatch_sync(r->worker, ^{
        os_unfair_lock_lock(&r->screen_lock);
        size_t bits = r->cursor ? (size_t)r->cursor_stride * r->cursor_h : 0;
        need = sizeof(DisplayState) + bits;
        if (out && cap >= need) {
            DisplayState d = {.on_screen = r->on_screen, .cursor_w = bits ? r->cursor_w : 0, .cursor_h = bits ? r->cursor_h : 0,
                              .cursor_stride = bits ? r->cursor_stride : 0, .cursor_shown = r->cursor_shown,
                              .hot_x = r->cursor_hot_x, .hot_y = r->cursor_hot_y};
            memcpy(out, &d, sizeof d);
            if (bits) memcpy((uint8_t *)out + sizeof d, r->cursor, bits);
        }
        os_unfair_lock_unlock(&r->screen_lock);
    });
    return need;
}

void hv_pvg_metal_set_display_state(HvPvgMetal *m, const void *in, size_t len) {
    if (!m || len < sizeof(DisplayState)) return;
    HvReplay *r = (__bridge HvReplay *)m;
    DisplayState d;
    memcpy(&d, in, sizeof d);
    size_t bits = (size_t)d.cursor_stride * d.cursor_h;
    if (len < sizeof d + bits || d.cursor_w > 512 || d.cursor_h > 512 || (bits && d.cursor_stride < d.cursor_w * 4)) bits = 0;
    uint8_t *copy = bits ? malloc(bits) : NULL;
    if (copy) memcpy(copy, (const uint8_t *)in + sizeof d, bits);
    dispatch_sync(r->worker, ^{
        @autoreleasepool {
            id<MTLTexture> glyph = nil;
            if (copy) {
                MTLTextureDescriptor *ct = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatBGRA8Unorm
                                                                                              width:d.cursor_w height:d.cursor_h mipmapped:NO];
                ct.storageMode = MTLStorageModeShared;
                glyph = [r->device newTextureWithDescriptor:ct];
                [glyph replaceRegion:MTLRegionMake2D(0, 0, d.cursor_w, d.cursor_h) mipmapLevel:0 withBytes:copy bytesPerRow:d.cursor_stride];
            }
            os_unfair_lock_lock(&r->screen_lock);
            if (copy) {
                free(r->cursor);
                r->cursor = copy, r->cursor_w = d.cursor_w, r->cursor_h = d.cursor_h, r->cursor_stride = d.cursor_stride;
                r->cursor_hot_x = d.hot_x, r->cursor_hot_y = d.hot_y;
                r->cursor_tex = glyph;
            }
            r->cursor_shown = d.cursor_shown != 0;
            os_unfair_lock_unlock(&r->screen_lock);
            r->on_screen = d.on_screen;
            if (d.on_screen) [r present:d.on_screen];
            [r drawCursor];
        }
    });
    fprintf(stderr, "hengevm: pvg-metal: screen %llu and a %ux%u pointer restored\n", (unsigned long long)d.on_screen, d.cursor_w, d.cursor_h);
}
