
// regexMatch.m
// Oct-13-2015
// -John Taylor
//
// objective-c regular expression match

// when searching for reserved RE characters such as { } ^ $ 
// they need to be escaped twice:
// 1) for the regular expression 2) because the backslashes in (1) needed to be escaped themselves
// Example: searching for: (${.*?}) becomes (\\$\\{.*?\\})
- (NSString *) regexMatch:(NSString *)searchText pattern:(NSString *)pattern isCaseSensitive:(BOOL)isCaseSensitive {
    NSError *error = NULL;
    NSRegularExpressionOptions regexOptions = isCaseSensitive ? 0 : NSRegularExpressionCaseInsensitive;
    NSRegularExpression *regex = [NSRegularExpression regularExpressionWithPattern:pattern options:regexOptions error:&error];
                                  
    if( error ) {
        NSLog(@"Could not create regex: %@", error);
        return nil;
    }
    
    NSTextCheckingResult *match = [regex firstMatchInString:searchText options:0 range:NSMakeRange(0, [searchText length])];
    //NSLog(@"isMatch: %d", (match != nil));

    if (match) {
        NSInteger position = [match rangeAtIndex:1].location;
        NSInteger distance = [match rangeAtIndex:1].length;
        return [searchText substringWithRange:NSMakeRange(position,distance)];
    } else {
        return nil;
    }
}
