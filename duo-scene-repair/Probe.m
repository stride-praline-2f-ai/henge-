#import <UIKit/UIKit.h>
#import "DuoSceneRepair.h"

@interface ProbeViewController : UIViewController
@property(nonatomic, strong) UILabel *status;
@property(nonatomic, strong) UISwitch *follow;
@end
@implementation ProbeViewController
- (void)viewDidLoad {
    [super viewDidLoad];
    self.view.backgroundColor = UIColor.systemBackgroundColor;
    UILabel *title = [UILabel new];
    title.text = @"Duo Scene Probe";
    title.font = [UIFont boldSystemFontOfSize:28];
    title.translatesAutoresizingMaskIntoConstraints = NO;

    UILabel *caption = [UILabel new];
    caption.text = @"Fold, unfold and rotate. This app can refresh ONLY its own scene.";
    caption.numberOfLines = 0;
    caption.font = [UIFont systemFontOfSize:15];
    caption.textColor = UIColor.secondaryLabelColor;
    caption.translatesAutoresizingMaskIntoConstraints = NO;

    _status = [UILabel new];
    _status.numberOfLines = 0;
    _status.font = [UIFont monospacedSystemFontOfSize:15 weight:UIFontWeightRegular];
    _status.translatesAutoresizingMaskIntoConstraints = NO;

    UILabel *switchText = [UILabel new];
    switchText.text = @"Request physical orientation";
    switchText.font = [UIFont systemFontOfSize:15];
    switchText.translatesAutoresizingMaskIntoConstraints = NO;
    _follow = [UISwitch new];
    _follow.translatesAutoresizingMaskIntoConstraints = NO;
    [_follow addTarget:self action:@selector(toggled:) forControlEvents:UIControlEventValueChanged];

    UIButton *refresh = [UIButton buttonWithType:UIButtonTypeSystem];
    [refresh setTitle:@"Refresh this scene" forState:UIControlStateNormal];
    [refresh addTarget:self action:@selector(refresh:) forControlEvents:UIControlEventTouchUpInside];
    refresh.translatesAutoresizingMaskIntoConstraints = NO;

    for (UIView *v in @[title, caption, _status, switchText, _follow, refresh]) {
        [self.view addSubview:v];
    }
    UILayoutGuide *safe = self.view.safeAreaLayoutGuide;
    [NSLayoutConstraint activateConstraints:@[
        [title.topAnchor constraintEqualToAnchor:safe.topAnchor constant:25],
        [title.leadingAnchor constraintEqualToAnchor:safe.leadingAnchor constant:24],
        [caption.topAnchor constraintEqualToAnchor:title.bottomAnchor constant:12],
        [caption.leadingAnchor constraintEqualToAnchor:title.leadingAnchor],
        [caption.trailingAnchor constraintEqualToAnchor:safe.trailingAnchor constant:-24],
        [_status.topAnchor constraintEqualToAnchor:caption.bottomAnchor constant:28],
        [_status.leadingAnchor constraintEqualToAnchor:title.leadingAnchor],
        [_status.trailingAnchor constraintEqualToAnchor:caption.trailingAnchor],
        [switchText.topAnchor constraintEqualToAnchor:_status.bottomAnchor constant:25],
        [switchText.leadingAnchor constraintEqualToAnchor:title.leadingAnchor],
        [_follow.centerYAnchor constraintEqualToAnchor:switchText.centerYAnchor],
        [_follow.leadingAnchor constraintEqualToAnchor:switchText.trailingAnchor constant:14],
        [refresh.topAnchor constraintEqualToAnchor:switchText.bottomAnchor constant:26],
        [refresh.leadingAnchor constraintEqualToAnchor:title.leadingAnchor]
    ]];
    [NSNotificationCenter.defaultCenter addObserver:self
       selector:@selector(geometryChanged:) name:DuoSceneRepairGeometryDidChange object:nil];
    [NSNotificationCenter.defaultCenter addObserver:self
       selector:@selector(geometryChanged:) name:UIDeviceOrientationDidChangeNotification object:nil];
    DuoSceneRepairStart();
    [self updateStatus];
}
- (void)viewDidLayoutSubviews {
    [super viewDidLayoutSubviews];
    [self updateStatus];
}
- (void)geometryChanged:(NSNotification *)note {
    (void)note;
    [self updateStatus];
}
- (void)toggled:(UISwitch *)sender {
    DuoSceneRepairSetFollowPhysicalOrientation(sender.isOn);
    DuoSceneRepairRefresh();
    [self updateStatus];
}
- (void)refresh:(UIButton *)sender {
    (void)sender;
    DuoSceneRepairRefresh();
    [self updateStatus];
}
- (void)updateStatus {
    UIWindowScene *scene = self.view.window.windowScene;
    CGRect available = scene ? scene.coordinateSpace.bounds : CGRectZero;
    CGSize viewSize = self.view.bounds.size;
    UIDeviceOrientation sensor = UIDevice.currentDevice.orientation;
    self.status.text = [NSString stringWithFormat:
        @"Host scene: %.0f × %.0f pt\nView: %.0f × %.0f pt\nInterface rotation: %ld\n"
         "Physical sensor: %ld\nModule: %@",
         available.size.width, available.size.height,
         viewSize.width, viewSize.height,
         (long)scene.interfaceOrientation, (long)sensor, DuoSceneRepairStatus()];
}
@end

@interface ProbeSceneDelegate : UIResponder <UIWindowSceneDelegate>
@property(nonatomic, strong) UIWindow *window;
@end
@implementation ProbeSceneDelegate
- (void)scene:(UIScene *)scene willConnectToSession:(UISceneSession *)session
    options:(UISceneConnectionOptions *)options {
    (void)session; (void)options;
    if (![scene isKindOfClass:UIWindowScene.class]) return;
    self.window = [[UIWindow alloc] initWithWindowScene:(UIWindowScene *)scene];
    self.window.rootViewController = [ProbeViewController new];
    [self.window makeKeyAndVisible];
}
@end

@interface ProbeAppDelegate : UIResponder <UIApplicationDelegate>
@end
@implementation ProbeAppDelegate
- (UISceneConfiguration *)application:(UIApplication *)application
    configurationForConnectingSceneSession:(UISceneSession *)connectingSceneSession
    options:(UISceneConnectionOptions *)options {
    (void)application; (void)options;
    return [UISceneConfiguration configurationWithName:@"Default"
                                            sessionRole:connectingSceneSession.role];
}
@end

int main(int argc, char *argv[]) {
    @autoreleasepool {
        return UIApplicationMain(argc, argv, nil, NSStringFromClass(ProbeAppDelegate.class));
    }
}
