#!/usr/bin/env python 
from time import sleep 
import sys 

for x in range(100): 
    print '\rDownloading: (%d%%) %s ' % ( x, "|"*(x/2)), 
    sys.stdout.flush() 
    sleep(0.1) 