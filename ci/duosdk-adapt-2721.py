#!/usr/bin/env python3
"""English DuoSDK/iOS 27.2.1 adaptation. Never suppress verification or rollback checks."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
src=root/'Sources'
def once(s,a,b):
    assert s.count(a)==1,(a[:100],s.count(a))
    return s.replace(a,b,1)
ui=src/'App.swift'
s=ui.read_text()
for a,b in {
'Leyendo la caché de flags…':'Reading cached settings…',
'Sin resultado':'No result',
'Revisar y aplicar SDK 27.2':'Review and apply SDK 27.2',
'Solo revisar':'Review only',
'Volver al último estado':'Restore previous changes',
'Revisa las apps instaladas y guarda una copia antes de aplicar cambios.':'Checks installed apps and creates a backup before applying changes. Experimental: back up your iPhone first.',
'Revisando el Duo…':'Checking your iPhone Duo…',
'Resultado':'Results',
'¿Revertir el último lote?':'Restore the last backup?',
'Revertir':'Restore backup',
'Se comprobará que la caché sigue siendo compatible con la copia guardada.':'The live cache must match the saved backup before a restore is allowed.'
}.items():
    assert a in s,a
    s=s.replace(a,b)
ui.write_text(s)

p=src/'LSStoreRead.m'
s=p.read_text()
s+="""
// Return only candidate cache directories. The maintenance code independently
// obtains access, requires one matching regular file, and validates its schema.
NSArray<NSString *> *DuoSDKCacheDirectories(void) {
    NSMutableOrderedSet<NSString *> *directories = [NSMutableOrderedSet orderedSet];
    for (NSNumber *kind in @[@10, @12]) {
        NSString *directory = lsdPath(kind.unsignedLongLongValue);
        if (directory) [directories addObject:directory];
    }
    for (NSString *path in mappedStorePaths([NSMutableString string])) {
        if (isStoreName(path.lastPathComponent))
            [directories addObject:path.stringByDeletingLastPathComponent];
    }
    if (directories.count == 0)
        [directories addObjectsFromArray:findStoreDirectoriesByInode([NSMutableSet set], [NSMutableString string])];
    return directories.array;
}
"""
p.write_text(s)

p=src/'XCacheTransaction.m'
s=p.read_text()
s=once(s,
'static NSString *const LSActiveStore = @"com.apple.LaunchServices-35651614-v2.csstore";\nstatic NSString *const LSExactDirectory = @"/private/var/mobile/Containers/Data/InternalDaemon/F8ED4A67-3CC3-4A7D-8748-3E090B6A3FBD/Library/Caches";',
'''static NSString *LSActiveStore = @"com.apple.LaunchServices-35651614-v2.csstore";
static NSString *LSExactDirectory = @"/private/var/mobile/Containers/Data/InternalDaemon/F8ED4A67-3CC3-4A7D-8748-3E090B6A3FBD/Library/Caches";''')
s=once(s,'NSString *DuoSDKMaintenance(NSInteger action) {',"""
NSArray<NSString *> *DuoSDKCacheDirectories(void);

// iOS installs/downgrades can change the private container UUID and the
// LaunchServices cache filename. Never reuse a cache path from another build.
static int64_t DuoSDKOpenCache(NSString *group, int *outFD) {
    *outFD = -1;
    for (NSString *directory in DuoSDKCacheDirectories()) {
        BOOL internal = [directory hasPrefix:@"/private/var/mobile/Containers/Data/InternalDaemon/"];
        BOOL system = [directory hasPrefix:@"/private/var/containers/Data/System/"];
        if (!internal && !system) continue;
        if (![directory.lastPathComponent isEqualToString:@"Caches"] ||
            ![directory.stringByDeletingLastPathComponent.lastPathComponent isEqualToString:@"Library"]) continue;
        int64_t token = worse_query(directory, group, false, true);
        if (token < 0) continue;
        int fd = open(directory.fileSystemRepresentation, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
        if (fd < 0) { worse_query_release(token); continue; }
        NSArray<NSString *> *names = [NSFileManager.defaultManager contentsOfDirectoryAtPath:directory error:nil];
        NSMutableArray<NSString *> *stores = [NSMutableArray array];
        for (NSString *name in names) {
            NSString *prefix = @"com.apple.LaunchServices-", *suffix = @"-v2.csstore";
            if (![name hasPrefix:prefix] || ![name hasSuffix:suffix] ||
                name.length <= prefix.length + suffix.length) continue;
            NSString *number = [name substringWithRange:NSMakeRange(prefix.length,
                name.length - prefix.length - suffix.length)];
            if ([number rangeOfCharacterFromSet:NSCharacterSet.decimalDigitCharacterSet.invertedSet].location != NSNotFound) continue;
            struct stat st;
            int handle = openRegularAtMost(fd, name, &st, LSMaximumSize);
            if (handle >= 0) { [stores addObject:name]; close(handle); }
        }
        if (stores.count == 1) {
            LSExactDirectory = directory;
            LSActiveStore = stores.firstObject;
            *outFD = fd;
            return token;
        }
        close(fd);
        worse_query_release(token);
    }
    return -1;
}

NSString *DuoSDKMaintenance(NSInteger action) {""")
s=once(s,'''if (os.majorVersion != 27 || os.minorVersion != 3 ||
        sysctlbyname("hw.machine", model, &modelSize, NULL, 0) != 0 || strcmp(model, "iPhone19,4") != 0) {
        return @"Esta versión de Duo SDK está preparada para el iPhone Duo con iOS 27.3.";
    }''','''if (os.majorVersion != 27 || os.minorVersion != 2 || os.patchVersion != 1 ||
        sysctlbyname("hw.machine", model, &modelSize, NULL, 0) != 0 || strcmp(model, "iPhone19,4") != 0) {
        return @"This build supports only iPhone Duo (iPhone19,4) running iOS 27.2.1. No changes made.";
    }''')
s=once(s,'''int64_t token = worse_query(LSExactDirectory, group, false, true);
    int dir = token >= 0 ? open(LSExactDirectory.fileSystemRepresentation, O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC) : -1;
    @try {
        if (dir < 0) return @"iOS no ha permitido acceder a la caché de apps. No se ha cambiado nada.";''',
'''int dir = -1;
    int64_t token = DuoSDKOpenCache(group, &dir);
    @try {
        if (dir < 0) return @"Could not locate an accessible, unambiguous LaunchServices v2 cache on iOS 27.2.1. No changes made. Check App Group signing and iOS permissions.";''')
# Translate all normal UI results, without altering internal success markers.
for a,b in {
'Todavía no hay una copia de esta app que restaurar.':'No previous backup is available.',
'No se pudo abrir la copia anterior.':'Could not open the previous backup.',
'Último lote revertido y verificado.':'Previous changes restored and verified.',
'La copia sigue guardada. iOS no permitió volver atrás.':'The backup is preserved. iOS did not allow a restore.',
'La caché actual no pasó la comprobación.':'The current cache failed validation. No changes made.',
'Falta la lista de ajustes anteriores.':'The tracked-app list is missing.',
'El formato de la caché no coincide con la versión probada.':'This cache layout could not be verified. No changes made.',
'Apps revisadas: %lu.':'Apps checked: %lu.',
'Todo al día. No hay ajustes pendientes.':'Everything is up to date. No adjustments needed.',
'%lu app tiene un ajuste pendiente.':'%lu app needs an SDK adjustment.',
'%lu apps tienen un ajuste pendiente.':'%lu apps need SDK adjustments.',
'No se pudo preparar una copia verificable. No se ha aplicado el ajuste.':'Could not prepare and verify a backup. No changes applied.',
'No se pudo abrir la copia preparada. No se ha aplicado el ajuste.':'Could not open the prepared backup. No changes applied.',
'Ajustes guardados y verificados. Si una app conserva el diseño anterior, reinicia el Duo para recargar la caché.':'Changes saved and verified. Restart the iPhone Duo to refresh layouts if needed.',
'Lote inválido. Sin escritura.':'Invalid change batch. Nothing was written.',
'La caché activa difiere de la copia verificada. Sin escritura.':'Live cache differs from the verified backup. Nothing was written.',
'La caché cambió durante la prueba. Sin escritura.':'The cache changed during validation. Nothing was written.',
'DUO_BATCH_RECUPERADO tras el fallo.':'DUO_BATCH_RECUPERADO: Original restored after verification failure.',
'Estado final sin verificar. Copia original conservada.':'Final state not verified. Original backup preserved.',
'Prueba de edición directa, protección %d: cambio %d, reversión %d, limpieza %d.':'Temporary file write test, protection %d: changed %d, restored %d, cleaned %d.',
'registros, %lu bytes distintos, inodo %llu, modo %04o, protección %d.':'records, %lu changed bytes, inode %llu, mode %04o, protection %d.'
}.items():
    assert a in s,a
    s=s.replace(a,b)
p.write_text(s)
p=src/'DuoSDKPlan.m'
s=p.read_text().replace('validated iOS 27.3','original iOS 27.3')
p.write_text(s)
print('English UI and strict iOS 27.2.1 compatibility adaptation applied.')
