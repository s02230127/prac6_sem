'''
while s := input():
    s = s.split()
    cmd, args = s[0], s[1:]
    print(cmd, len(args), *args)


import shlex
line = input("")
print(shlex.split(line))

'''

import shlex
while s := input():
    print(shlex.join(shlex.split(s)))
