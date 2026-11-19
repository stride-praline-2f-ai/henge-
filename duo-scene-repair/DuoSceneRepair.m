#import "DuoSceneRepair.h"
#import <math.h>

NSNotificationName const DuoSceneRepairGeometryDidChange = @"DuoSceneRepairGeometryDidChange";

@interface DSCoordinator : NSObject
@property(nonatomic) BOOL started;
@property(nonatomic) BOOL followPhysicalOrientation;
@property(nonatomic) BOOL refreshPending;
@property(nonatomic, strong) NSMutableDictionary<NSString *, NSString *> *priorSizes;
@property(nonatomic, copy) NSString *lastStatus;
@property(nonatomic, strong) NSMutableArray<id> *observers;
- (void)start;
- (void)stop;
- (void)refresh;
- (void)queueRefresh;
@end

@implementation DSCoordinator
- (instancetype)init {
    if ((self = [super init])) {
        _priorSizes = [NSMutableDictionary dictionary];
        _lastStatus = @"Not started";
        _observers = [NSMutableArray array];
    }
    return self;
}
- (void)start {
    NSAssert(NSThread.isMainThread, @"Use on the main thread");
    if (self.started) return;
    self.started = YES;
    [UIDevice.currentDevice beginGeneratingDeviceOrientationNotifications];
    NSArray<NSNotificationName> *names = @[
        UIDeviceOrientationDidChangeNotification,
        UIApplicationDidBecomeActiveNotification,
        UIApplicationWillEnterForegroundNotification,
        UISceneDidActivateNotification,
        UISceneWillEnterForegroundNotification,
        UIWindowDidBecomeKeyNotification
    ];
    __weak typeof(self) weakSelf = self;
    for (NSNotificationName name in names) {
        id token = [NSNotificationCenter.defaultCenter
            addObserverForName:name object:nil queue:NSOperationQueue.mainQueue
            usingBlock:^(NSNotification *note) {
                (void)note;
                [weakSelf queueRefresh];
            }];
        if (token) [self.observers addObject:token];
    }
    [self queueRefresh];
}
- (void)stop {
    if (!self.started) return;
    self.started = NO;
    for (id token in self.observers)
        [NSNotificationCenter.defaultCenter removeObserver:token];
    [self.observers removeAllObjects];
    [self.priorSizes removeAllObjects];
    [UIDevice.currentDevice endGeneratingDeviceOrientationNotifications];
    self.lastStatus = @"Stopped";
}
- (void)queueRefresh {
    if (!self.started || self.refreshPending) return;
    self.refreshPending = YES;
    // Wait until UIKit has finished installing a scene/window or handling a fold.
    dispatch_async(dispatch_get_main_queue(), ^{
        self.refreshPending = NO;
        if (self.started) [self refresh];
    });
}
- (void)refresh {
    if (!self.started) return;
    NSMutableArray<NSString *> *states = [NSMutableArray array];
    for (UIScene *rawScene in UIApplication.sharedApplication.connectedScenes) {
        if (![rawScene isKindOfClass:UIWindowScene.class]) continue;
        if (rawScene.activationState != UISceneActivationStateForegroundActive &&
            rawScene.activationState != UISceneActivationStateForegroundInactive) continue;
        UIWindowScene *scene = (UIWindowScene *)rawScene;
        CGRect bounds = scene.coordinateSpace.bounds;
        NSString *key = scene.session.persistentIdentifier ?: @"unknown-session";
        NSString *size = [NSString stringWithFormat:@"%.1f x %.1f", bounds.size.width, bounds.size.height];
        BOOL changed = ![self.priorSizes[key] isEqualToString:size];
        [states addObject:[NSString stringWithFormat:@"%@ (%@)", size,
                           changed ? @"changed" : @"unchanged"]];
        if (changed) {
            self.priorSizes[key] = size;
            // Actual app-level layout refresh. UIKit owns the scene window size:
            // never expand it past coordinateSpace.bounds.
            for (UIWindow *window in scene.windows) {
                UIViewController *root = window.rootViewController;
                if (!root) continue;
                [root setNeedsUpdateOfSupportedInterfaceOrientations];
                [root.view setNeedsLayout];
                [root.view layoutIfNeeded];
            }
            [NSNotificationCenter.defaultCenter
                postNotificationName:DuoSceneRepairGeometryDidChange
                object:scene
                userInfo:@{@"width":@(bounds.size.width),
                           @"height":@(bounds.size.height),
                           @"isWide":@(bounds.size.width > bounds.size.height)}];
        }
        if (self.followPhysicalOrientation) {
            UIDeviceOrientation physical = UIDevice.currentDevice.orientation;
            UIInterfaceOrientationMask requested = 0;
            if (physical == UIDeviceOrientationLandscapeLeft ||
                physical == UIDeviceOrientationLandscapeRight)
                requested = UIInterfaceOrientationMaskLandscape;
            else if (physical == UIDeviceOrientationPortrait)
                requested = UIInterfaceOrientationMaskPortrait;
            // Do not request geometry repeatedly if UIKit already has the
            // desired family. Physical orientation != window aspect ratio.
            BOOL currentLandscape = UIInterfaceOrientationIsLandscape(scene.interfaceOrientation);
            if (requested && ((requested == UIInterfaceOrientationMaskLandscape && !currentLandscape) ||
                              (requested == UIInterfaceOrientationMaskPortrait && currentLandscape))) {
                UIWindowSceneGeometryPreferencesIOS *prefs =
                    [[UIWindowSceneGeometryPreferencesIOS alloc]
                     initWithInterfaceOrientations:requested];
                [scene requestGeometryUpdateWithPreferences:prefs errorHandler:^(NSError *error) {
                    NSLog(@"[DuoSceneRepair] Geometry request declined: %@", error);
                }];
            }
        }
    }
    self.lastStatus = states.count ? [states componentsJoinedByString:@"; "] : @"No active host-app scene";
}
@end

static DSCoordinator *DuoCoordinator(void) {
    static DSCoordinator *instance;
    static dispatch_once_t once;
    dispatch_once(&once, ^{ instance = [DSCoordinator new]; });
    return instance;
}
static void RunMain(dispatch_block_t block) {
    if (NSThread.isMainThread) block();
    else dispatch_async(dispatch_get_main_queue(), block);
}
void DuoSceneRepairStart(void) { RunMain(^{ [DuoCoordinator() start]; }); }
void DuoSceneRepairStop(void) { RunMain(^{ [DuoCoordinator() stop]; }); }
void DuoSceneRepairRefresh(void) { RunMain(^{ [DuoCoordinator() refresh]; }); }
void DuoSceneRepairSetFollowPhysicalOrientation(BOOL enabled) {
    RunMain(^{ DuoCoordinator().followPhysicalOrientation = enabled; });
}
NSString *DuoSceneRepairStatus(void) {
    if (!NSThread.isMainThread) return @"Read status on main thread";
    return DuoCoordinator().lastStatus ?: @"Unavailable";
}
