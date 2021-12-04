#! /usr/local/bin/python3

import sys
import base64

if len(sys.argv) <=1:
    print('Insufficient parameter passed, Usage: ./json2base64jwt.py abcd.json')
    exit()
x=base64.b64encode(open(sys.argv[1], 'r').read().encode('ascii'))
print(x.decode('ascii'))
