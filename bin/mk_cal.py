#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import argparse

############################################################
# parse arguments:
parser = argparse.ArgumentParser(description='Process calibration curve.')
parser.add_argument('fname', metavar='fname', type=str, nargs=1,
                    help='filename')

## reading data

parser.add_argument('-x', '--colx', dest='colx',
                    type=int, default=1,
                    help='x column in the file (default: 1)')

parser.add_argument('-y', '--coly', dest='coly',
                    type=int, default=2,
                    help='y column in the file (default: 2)')

parser.add_argument('--xmin', dest='xmin',
                    type=float, default=float('nan'),
                    help='x minimum value (default: NaN)')

parser.add_argument('--xmax', dest='xmax',
                    type=float, default=float('nan'),
                    help='x maximum value (default: NaN)')

parser.add_argument('--ymin', dest='ymin',
                    type=float, default=float('nan'),
                    help='y minimum value (default: NaN)')

parser.add_argument('--ymax', dest='ymax',
                    type=float, default=float('nan'),
                    help='y maximum value (default: NaN)')

parser.add_argument('--xlabel', dest='xlabel',
                    type=str, default="X",
                    help='x label')

parser.add_argument('--ylabel', dest='ylabel',
                    type=str, default="Y",
                    help='y label')

## converting data

parser.add_argument('--xfunc', dest='xfunc',
                    type=str, default="",
                    help='function to apply to x column ("1/x", "log10")')

parser.add_argument('--yfunc', dest='yfunc',
                    type=str, default="",
                    help='function to apply to y column ("1/x", "log10")')

## interpolation

parser.add_argument('-n', '--npts', dest='npts',
                    type=int, default=100,
                    help='number of points (default: 100)')

parser.add_argument('-d', '--degree', dest='fdeg',
                    type=int, default=3,
                    help='polynomial degree for fitting (default: 3)')

parser.add_argument('-m', '--minfitpts', dest='minpts',
                    type=int, default=10,
                    help='Increase the fitting range if it containes less points then MINPTS (default: 10).' +
                         ' It is good to have MINPTS larger then --degree setting.'+
                         ' Increase MINPTS to make regions with less points more smooth.')

parser.add_argument('-w', '--win', dest='win',
                    type=float, default=5.0,
                    help='Interpolation window (in interpoint distance, default: 5).'+
                         ' If original curve is smooth, set this to a smaller value (near 1).')

# extrapolation

parser.add_argument('--le_pts', dest='le_pts',
                    type=int, default=0,
                    help='left-side extrapolation, number of intervals (default: 0)')
parser.add_argument('--le_deg', dest='le_deg',
                    type=int, default=2,
                    help='left-side extrapolation polynomial degree (default: 2)')
parser.add_argument('--le_win', dest='le_win',
                    type=float, default=5,
                    help='left-side extrapolation window (in interpoint distance, default 5)')

parser.add_argument('--re_pts', dest='re_pts',
                    type=int, default=0,
                    help='right-side extrapolation, number of intervals (default: 0)')
parser.add_argument('--re_deg', dest='re_deg',
                    type=int, default=2,
                    help='right-side extrapolation polynomial degree (default: 2)')
parser.add_argument('--re_win', dest='re_win',
                    type=float, default=5,
                    help='right-side extrapolation window (in interpoint distance, default 5)')


## plotting

parser.add_argument('-p', '--plot', dest='plot', action='store_true',
                    help='make interactive plot')

parser.add_argument('--png', dest='png', type=str, default="",
                    help='make png file')

args = parser.parse_args()

############################################################


b1=f1=lambda x: x
b2=f2=lambda x: x
xl=args.xlabel
yl=args.ylabel
if args.xfunc == "1/x":
  b1=f1=lambda x: 1/x
  xl="1/" + args.xlabel
if args.yfunc == "1/x":
  b2=f2=lambda x: 1/x
  yl="1/" + args.ylabel

if args.xfunc == "log10":
  f1=lambda x: np.log10(x)
  b1=lambda x: 10**x
  xl="log10(" + args.xlabel + ")"
if args.yfunc == "log10":
  f2=lambda x: np.log10(x)
  b2=lambda x: 10**x
  yl="log10(" + args.ylabel + ")"

if args.xfunc == "log10(1/x)":
  f1=lambda x: np.log10(1/x)
  b1=lambda x: 1.0/10**x
  xl="log10(1/" + args.xlabel + ")"
if args.yfunc == "log10(1/x)":
  f2=lambda x: np.log10(1/x)
  b2=lambda x: 1.0/10**x
  yl="log10(1/" + args.ylabel + ")"

# Get data
# We need two calibration columns and maybe time.
data = np.loadtxt(args.fname[0])
x = data[:,args.colx]
y = data[:,args.coly]

# apply min/max
if (not np.isnan(args.xmin)):
  ii = np.where(x>args.xmin)
  x=x[ii]; y=y[ii]
if (not np.isnan(args.xmax)):
  ii = np.where(x<args.xmax)
  x=x[ii]; y=y[ii]
if (not np.isnan(args.ymin)):
  ii = np.where(y>args.ymin)
  x=x[ii]; y=y[ii]
if (not np.isnan(args.ymax)):
  ii = np.where(y<args.ymax)
  x=x[ii]; y=y[ii]

# apply function
x = f1(x)
y = f2(y)


# build interpolation points
calx = np.linspace(x.min(), x.max(), args.npts)
caly = np.zeros(calx.size)
dx=(x.max()-x.min())/(args.npts-1)

########################################################
## Interpolation

# for each calibration point do polynomial fit
# with degree <args.fdeg> in the range <win>
# and fill caly array
for i in np.arange(calx.size):
   n=1
   while True:
     fiti = np.where(abs(x-calx[i])<n*args.win*dx/2)
     if ((x[fiti].size<args.minpts) & (n*args.win*dx/2<x.max()-x.min())):
       n*=2
       continue
     break
     # w=1/(1+x[fiti]-calx[i])
   pp=np.polyfit(x[fiti], y[fiti], args.fdeg)
   caly[i]=np.polyval(pp,calx[i])

   plt.plot(x[fiti], np.polyval(pp,x[fiti])+i*0.1, 'r-')

plt.savefig("a.png", dpi=100)
plt.clf

########################################################
## Extrapolation
if (args.le_pts>0):
  ii = np.where(abs(x-calx[0])<args.le_win*dx)
  pp=np.polyfit(x[ii], y[ii], args.le_deg)
  xx = calx[0] - np.arange(args.le_pts,0,-1)*dx
  yy = np.polyval(pp,xx)
  calx=np.insert(calx,0,xx)
  caly=np.insert(caly,0,yy)

if (args.re_pts>0):
  ii = np.where(abs(x-calx[-1])<args.re_win*dx)
  pp=np.polyfit(x[ii], y[ii], args.re_deg)
  xx = calx[-1] + (np.arange(args.re_pts)+1)*dx
  yy = np.polyval(pp,xx)
  calx=np.append(calx,xx)
  caly=np.append(caly,yy)

########################################################
## Printing

print("# ", xl, " ", yl)
for i in np.arange(calx.size):
  print(calx[i], " ", caly[i])

########################################################
## Plotting
if (len(args.png) | args.plot):

  plt.subplot(2, 1, 1)
  plt.plot(x, y, 'g.', markersize=3)
  plt.plot(calx, caly, 'r.-', markersize=2, linewidth=0.5)
  plt.ylabel(yl)

  plt.subplot(2, 1, 2)
  plt.plot(x, 100*(1-b2(np.interp(x,calx,caly))/b2(y)), 'b.', markersize=3)
  plt.xlabel(xl)
  plt.ylabel(args.ylabel + ' difference, %')

  plt.title('')
  plt.grid(True)

  if (len(args.png)):
    fig = plt.gcf()
    fig.set_size_inches(6, 12)
    plt.savefig(args.png, dpi=100)

  if (args.plot):
    plt.show()
