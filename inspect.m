//
//  inspect.m
//  display a variable's content and data type such as NSArray, NSMutaableDictionary, etc.
//  
//

#import <Foundation/Foundation.h>

// NSLog will not display timestamp
#define NSLog(FORMAT, ...) fprintf(stderr,"%s\n", [[NSString stringWithFormat:FORMAT, ##__VA_ARGS__] UTF8String]);

void inspect(NSString *desc, NSObject *obj) {
    NSLog(@"[{INSPECT #1}] %@: %@", desc, NSStringFromClass([obj class]));
    NSLog(@"[{INSPECT #2}] %@", obj);
    NSLog(@"-------------------------------------------");
}

