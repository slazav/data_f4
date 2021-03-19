#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import argparse

############################################################
# parse arguments:
parser = argparse.ArgumentParser(
  description='Use existing calibration (N V1 T) and table (V1 V2), make calibration (N V2 T)')

parser.add_argument('fname1', metavar='fname1', type=str, help='filename')
parser.add_argument('fname2', metavar='fname2', type=str, help='filename')

parser.add_argument('-i', '--inv', dest='inv', action='store_true',
                    help='use (V2 V1) file instead of (V1 V2)')

args = parser.parse_args()

############################################################

# Get calibration data
regexp = r'\s*\d+' + r'\s+([-.0-9]+)'*2
data1 = np.fromregex(args.fname1, regexp, dtype='f')
CX = data1[:,0]
CT = data1[:,1]

# Get RR data
regexp = r'\s*([-.0-9]+)\s+([-.0-9]+)'
data2 = np.fromregex(args.fname2, regexp, dtype='f')
if args.inv:
  X = data2[:,1]
  Y = data2[:,0]
else:
  X = data2[:,0]
  Y = data2[:,1]

if not np.all(np.diff(X) > 0):
  X=np.flip(X,0)
  Y=np.flip(Y,0)

if not np.all(np.diff(X) > 0):
  error("non-monotonic RR data")

CY=np.interp(CX,X,Y, float('nan'), float('nan'))

########################################################
## Printing

print("No.   Units      Temperature (K)")
j=1
for i in np.arange(CX.size):
  if np.isnan(CY[i]): continue
  print(j, " ", CY[i], " ", CT[i])
  j+=1

########################################################
## Plotting
plt.subplot(2,1,1)
plt.semilogx(CT, CX, 'g.', markersize=3)
plt.subplot(2,1,2)
plt.semilogx(CT, CY, 'r.', markersize=3)
plt.savefig("move_cal.png", dpi=100)
