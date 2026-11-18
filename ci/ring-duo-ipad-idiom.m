// Experimental app-local Ring iPad idiom shim.
// The dylib must be embedded only in a user-provided, re-signed test IPA.
// No system modifications, network activity, or background work.
#import <UIKit/UIKit.h>
#import <objc/runtime.h>

static UIUserInterfaceIdiom DuoRingPadIdiom(id receiver, SEL selector) {
    (void)receiver;
    (void)selector;
    return UIUserInterfaceIdiomPad;
}

__attribute__((constructor))
static void DuoRingInstallIdiom(void) {
    // Avoid UIKit lifecycle calls in a dyld constructor.
    // All frameworks are loaded, but app scene creation has not begun.
    Class deviceClass = objc_getClass("UIDevice");
    if (deviceClass == Nil) return;
    Method method = class_getInstanceMethod(deviceClass, @selector(userInterfaceIdiom));
    if (method == NULL) return;
    method_setImplementation(method, (IMP)DuoRingPadIdiom);
}
