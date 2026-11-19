#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

// These functions operate only on the host application's own UIWindowScenes.
// No private APIs, LaunchServices writes, system rotation controls, or hooks.
FOUNDATION_EXPORT void DuoSceneRepairStart(void);
FOUNDATION_EXPORT void DuoSceneRepairStop(void);
FOUNDATION_EXPORT void DuoSceneRepairRefresh(void);
FOUNDATION_EXPORT void DuoSceneRepairSetFollowPhysicalOrientation(BOOL enabled);
FOUNDATION_EXPORT NSString *DuoSceneRepairStatus(void);

FOUNDATION_EXPORT NSNotificationName const DuoSceneRepairGeometryDidChange;
NS_ASSUME_NONNULL_END
