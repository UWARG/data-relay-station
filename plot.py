#!/usr/bin/python
from csv import reader
from sys import argv
from matplotlib.pyplot import *
from itertools import cycle
from os import SEEK_END
f=open(argv[1])
READ_BYTES=10000
ion()
fig=figure()
ax=fig.add_subplot(111)
ax2=ax.twinx()
_time_wrap=2**16#0 to disable
while True:
	try:
		try:
			f.seek(-READ_BYTES,SEEK_END)
		except IOError:
			f.seek(0)
		f.readline()#discard half a line or the header
		r=reader(f.readlines()[:-1])
		a=[]
		for x in r:
			x=map(eval,x)
			#x[-1]=ord(x[-1])
			if _time_wrap:
				while len(a) and a[-1][0]>x[0]:
					x[0]+=_time_wrap
			a.append(x)
		b=zip(*a)
		if not b:
			continue
		t=b.pop(0)

		clr=iter(cycle('bgrcmyk'))
		end=max(t)
		xwin=end-1000,end
		ax.cla()
		ax2.cla()
		ax.axis(xwin+(-15,5))
		#ax.axis(ylim=(-15,5))
		ax2.plot(t,b.pop(-2),c=next(clr))
		ax2.axis(xwin+(-1000,1000))
		for v in b:
			ax.plot(t,v,c=next(clr))
		draw()
	except KeyboardInterrupt:
		raw_input('press enter to continue: ')
