//
//  inspect.m
//  display's a variable's content and data type such as NSArray, NSMutaableDictionary, etc.
//

#import <Foundation/Foundation.h>

#define NSLog(FORMAT, ...) fprintf(stderr,"%s\n", [[NSString stringWithFormat:FORMAT, ##__VA_ARGS__] UTF8String]);

void inspect(NSString *desc, NSObject *obj) {
    NSString *className = [[obj class] description];
    NSLog(@"[{INSPECT #1}] %@: %@", desc, className);
    NSLog(@"[{INSPECT #2}] %@", obj);
    NSLog(@"-------------------------------------------");
    
}

