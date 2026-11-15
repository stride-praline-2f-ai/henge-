/* Read-only ABI probe on the cloud Mac's real paravirtual Metal device.
   No swizzles, guest patches, large allocations or arbitrary heap reads. */
#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <objc/runtime.h>
#import <IOKit/IOKitLib.h>
#include <dlfcn.h>
#include <mach/mach.h>
#include <mach/mach_vm.h>
#include <ptrauth.h>
#include <stdio.h>
#include <string.h>
static BOOL memoryKey(NSString *key) {
    NSString *lower=key.lowercaseString;
    return [lower containsString:@"memory"]||[lower containsString:@"vram"]||[lower containsString:@"budget"]||[lower containsString:@"working"]||[lower containsString:@"metalplugin"];
}
static id scalar(id value) {
    if([value isKindOfClass:NSNumber.class]||[value isKindOfClass:NSString.class])return value;
    if([value isKindOfClass:NSData.class]&&[value length]<=8){uint64_t n=0;memcpy(&n,[value bytes],[value length]);return @{@"bytes":@([value length]),@"little_endian":@(n)};}
    return NSStringFromClass([value class]);
}
int main(void){@autoreleasepool{
    id<MTLDevice> device=MTLCreateSystemDefaultDevice();if(!device)return 1;
    NSMutableDictionary *report=[@{@"name":device.name,@"class":NSStringFromClass([device class]),
        @"recommended":@(device.recommendedMaxWorkingSetSize),@"allocated":@(device.currentAllocatedSize),
        @"max_buffer":@(device.maxBufferLength),@"unified":@(device.hasUnifiedMemory),
        @"physical":@(NSProcessInfo.processInfo.physicalMemory),@"os":NSProcessInfo.processInfo.operatingSystemVersionString} mutableCopy];
    NSMutableArray *methods=[NSMutableArray new],*classes=[NSMutableArray new],*registry=[NSMutableArray new];
    for(Class c=[device class];c;c=class_getSuperclass(c)){
        NSMutableArray *names=[NSMutableArray new],*ivars=[NSMutableArray new];unsigned count=0;Method *list=class_copyMethodList(c,&count);
        for(unsigned i=0;i<count;i++){NSString *name=NSStringFromSelector(method_getName(list[i]));if(memoryKey(name)||[name hasPrefix:@"initWith"])[names addObject:name];}free(list);
        unsigned ic=0;Ivar *il=class_copyIvarList(c,&ic);
        for(unsigned i=0;i<ic;i++){
            NSString *name=@(ivar_getName(il[i]));
            ptrdiff_t offset=ivar_getOffset(il[i]);const char *type=ivar_getTypeEncoding(il[i]);
            NSMutableDictionary *field=[@{@"name":name,@"offset":@(offset),@"type":@(type)}mutableCopy];
            size_t width=(type[0]=='Q'||type[0]=='q')?8:(type[0]=='I'||type[0]=='i')?4:0;
            if(width&&offset>=0&&(size_t)offset+width<=class_getInstanceSize([device class])){
                uint64_t value=0;memcpy(&value,(const char *)(__bridge void *)device+offset,width);field[@"value"]=@(value);
            }
            [ivars addObject:field];
        }free(il);
        [classes addObject:@{@"class":NSStringFromClass(c),@"methods":names,@"ivars":ivars}];
    }
    for(NSString *name in @[@"recommendedMaxWorkingSetSize",@"currentAllocatedSize",@"maxBufferLength",@"hasUnifiedMemory",@"recommendedMaxMemorySize",@"sharedMemorySize",@"dedicatedMemorySize",@"memoryInfo",@"initWithAccelerator:options:",@"initWithAccelerator:",@"initWithAcceleratorPort:",@"initWithAcceleratorPort:options:"]){
        Method method=class_getInstanceMethod([device class],NSSelectorFromString(name));if(!method)continue;
        uintptr_t code=(uintptr_t)ptrauth_strip(method_getImplementation(method),ptrauth_key_function_pointer);
        Dl_info image={0};dladdr((void *)code,&image);
        NSMutableDictionary *m=[@{@"selector":name,@"encoding":@(method_getTypeEncoding(method)),@"address":@(code),
            @"image":image.dli_fname?@(image.dli_fname):@"unknown",@"image_base":@((uintptr_t)image.dli_fbase)}mutableCopy];
        mach_vm_address_t region=code;mach_vm_size_t size=0;vm_region_basic_info_data_64_t info={0};
        mach_msg_type_number_t count=VM_REGION_BASIC_INFO_COUNT_64;mach_port_t object=MACH_PORT_NULL;
        kern_return_t status=mach_vm_region(mach_task_self(),&region,&size,VM_REGION_BASIC_INFO_64,(vm_region_info_t)&info,&count,&object);
        if(object)mach_port_deallocate(mach_task_self(),object);
        if(status==KERN_SUCCESS&&region<=code&&code-region<size&&(info.protection&VM_PROT_READ)){
            size_t length=(size_t)MIN((uint64_t)4096,size-(code-region));NSString *file=[name stringByAppendingString:@".bin"];
            [[NSData dataWithBytes:(void *)code length:length]writeToFile:file atomically:YES];m[@"code_file"]=file;
        }
        [methods addObject:m];
    }
    io_registry_entry_t entry=IOServiceGetMatchingService(kIOMainPortDefault,IORegistryEntryIDMatching(device.registryID));
    for(unsigned depth=0;entry&&depth<8;depth++){
        io_name_t name={0};IORegistryEntryGetName(entry,name);CFMutableDictionaryRef properties=NULL;
        NSMutableDictionary *values=[NSMutableDictionary new];
        if(IORegistryEntryCreateCFProperties(entry,&properties,kCFAllocatorDefault,0)==KERN_SUCCESS){
            NSDictionary *dict=CFBridgingRelease(properties);for(id key in dict)if([key isKindOfClass:NSString.class])values[key]=scalar(dict[key]);
        }
        [registry addObject:@{@"name":@(name),@"memory_properties":values}];
        io_registry_entry_t parent=MACH_PORT_NULL;IORegistryEntryGetParentEntry(entry,kIOServicePlane,&parent);IOObjectRelease(entry);entry=parent;
    }
    if(entry)IOObjectRelease(entry);
    report[@"methods"]=methods;report[@"classes"]=classes;report[@"registry"]=registry;
    NSData *json=[NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingPrettyPrinted error:nil];
    if(![json writeToFile:@"guest-gpu-budget-probe.json" atomically:YES])return 2;
    puts([[NSString alloc]initWithData:json encoding:NSUTF8StringEncoding].UTF8String);return 0;
}}
