#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__="WANG GE"
__date__ ="$2017-1-5 15:40:09$"
import os
#declaration
kktvar=[]
kktequ=[]
kktsos1=[]
convar=[]
conequ=[]
consos1=[]
mcvar=[]
mcequ=[]
mcsos1=[]
prevar=['u_','z_']
preequ=['equ_z_','equ_u_','equ_umv_','equ_v_']

filename=input("name of gams file, suffix is not necessary\n(default:sos1.gms):")
if '.' in filename:
	pass
elif filename == '':
	filename='sos1.gms'
else:
	filename=filename+'.gms'

if os.path.exists(filename):
    pass
else:
    print('Sorry. No '+filename+' exists.')
    exit();

with open(filename, 'r') as f:
	for line in f.readlines():
		tb1=line.split("..")[0]
		if tb1[0:4] == 'kkt_':
			kktvar.append(tb1)
			if line != '\n':
				tb2=line.split("..")[1].strip().strip('\n').strip('=g=0;').strip('=e=0;')
				kktequ.append(tb2)
		elif tb1[0:3] == 'mc_':
			mcvar.append(tb1)
			if line != '\n':
				tb2=line.split("..")[1].strip().strip('\n').strip('=g=0;').strip('=e=0;')
				mcequ.append(tb2)
		elif line != '\n':
			convar.append(tb1)
			tb2=line.split("..")[1].strip().strip('\n').strip('=g=0;').strip('=e=0;')
			conequ.append(tb2)

def definesos1var(var,sosvar,file):
	file.write('sos1 variable\n');
	for s in var:
		a=('sos_'+s).strip(')')+',s)'
		sosvar.append(a)
		file.write('\t'+a+'\n')
	file.write(';\n\n')
	return

def definevariable(var,file):
	file.write('positive variable\n');
	for x in prevar:
		for s in var:
			file.write('\t'+x+s+'\n')
		file.write('\n')
	file.write(';\n\n')

def defineequation(var,file):
	file.write('equation\n');
	for x in preequ:
		for s in var:
			file.write('\t'+x+s+'\n')
		file.write('\n')
	file.write(';\n')
	return

def showequation(var,sosvar,equ,file):
	for x in preequ:
		for i in list(range(len(var))):
			a=x+var[i]
			file.writelines(a+'..\t')
			if x[-2:] == 'z_':
				file.write(a[4:]+'=e='+equ[i]+';\n')
			elif x[-2:] == 'u_':
				file.write(a[4:]+'=e=('+('a_'+a[6:]).replace('a_kkt_','').replace('a_mc_','')+'+z_'+a[6:]+')/2;\n')
			elif x[-3:] == '_v_':
				file.write(sosvar[i].rstrip('s)')+'\'p\')'+'-'+sosvar[i].rstrip('s)')+'\'n\')=e='+('(a_'+a[6:]).replace('a_kkt_','').replace('a_mc_','')+'-z_'+a[6:]+')/2;\n')
			elif x[-3:] == 'mv_':
				file.write('u_'+var[i]+'-sum(s,'+sosvar[i]+')=e=0;\n')
		file.write('\n')

def writesos1(var,sosvar,equ,file):
	definesos1var(var,sosvar,file)
	definevariable(var,file)
	defineequation(var,file)
	showequation(var,sosvar,equ,file)

with open('out.gms', 'w') as outf:
	writesos1(convar,consos1,conequ,outf)
	writesos1(mcvar,mcsos1,mcequ,outf)
	writesos1(kktvar,kktsos1,kktequ,outf)

print('success! out.gms')