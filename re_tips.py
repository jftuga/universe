
# re_tips.py
# -John Taylor
# started on Aug-26-2015
#

import re

##################################################################################################
### Tip 1
##################################################################################################

print() ; print("="*77); print()

# https://news.ycombinator.com/item?id=10282121
# http://www.rexegg.com/regex-best-trick.html
# match all the content between certain delimiters (in this case double quotes)
a_re = re.compile('[^"]+')
a_test='A regex trick uses regex grammar to compose a "phrase" that achieves certain goals.'
print( a_re.findall(a_test) )



subject = 'Jane"" ""Tarzan12"" Tarzan11@Tarzan22 {4 Tarzan34}'
regex = re.compile(r'{[^}]+}|"Tarzan\d+"|(Tarzan\d+)')
# put Group 1 captures in a list
matches = [group for group in re.findall(regex, subject) if group]

######## The six main tasks we're likely to have ########

# Task 1: Is there a match?
print("*** Is there a Match? ***")
if len(matches)>0:
	print ("Yes")
else:
	print ("No")

# Task 2: How many matches are there?
print("\n" + "*** Number of Matches ***")
print(len(matches))

# Task 3: What is the first match?
print("\n" + "*** First Match ***")
if len(matches)>0:
	print (matches[0])
	
# Task 4: What are all the matches?
print("\n" + "*** Matches ***")
if len(matches)>0:
	for match in matches:
	    print (match)
		
# Task 5: Replace the matches
def myreplacement(m):
    if m.group(1):
        return "Superman"
    else:
        return m.group(0)
replaced = regex.sub(myreplacement, subject)
print("\n" + "*** Replacements ***")
print(replaced)

# Task 6: Split
# Start by replacing by something distinctive,
# as in Step 5. Then split.
splits = replaced.split('Superman')
print("\n" + "*** Splits ***")
for split in splits:
	    print (split)

##################################################################################################
### Tip 2
##################################################################################################

print() ; print("="*77); print()

# How can I check if a string contains ANY letters from the alphabet?
# https://stackoverflow.com/questions/9072844/how-can-i-check-if-a-string-contains-any-letters-from-the-alphabet

string_1 = "(555).555-5555"
print ( re.search('[a-zA-Z]', string_1) )
string_2 = "(555) 555 - 5555 ext. 5555"
print ( re.search('[a-zA-Z]', string_2) )

# even better for this particular scenario:
print ( any(c.isalpha() for c in string_1) )
print ( any(c.isalpha() for c in string_2) )

##################################################################################################
### Tip 3
##################################################################################################

# String replacement using Python 3 re.sub
# https://stackoverflow.com/questions/32974191/string-replacement-using-python-3-re-sub
