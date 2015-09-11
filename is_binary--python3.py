#!/usr/bin/env python3

# return True if a string is considered binary, otherwise False
# tested with Python 3.4.3

from itertools import zip_longest

textchars = bytearray([0,7,8,9,10,12,13,27]) + bytearray(range(0x20, 0x100))
textdict = dict(zip_longest(textchars,[''],fillvalue=''))
is_binary_string = lambda data: True if not len(data) else bool(data.translate(textdict))

data = "test 1 2 3"
print(is_binary_string(data))

data ="""Ïúíþ"""
print(is_binary_string(data))

