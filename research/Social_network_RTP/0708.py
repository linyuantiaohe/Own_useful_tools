#!/usr/bin/python
# -*- coding: UTF-8 -*-

import matplotlib.pyplot as plt
import itertools
import random
import copy
import sys
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib import animation
import networkx as nx
import collections
import subprocess
import os
import sys

#Two price pattern 1 and 2 for RTP and FP
#Three types of consumers: p1,p2,ep
#20% are p1, 20% are p2, 60% are ep

class choose (object):
	def __init__(self,nodes=500,happy_threshold=0.3,degree=3,graph_type='WS',pricetype=2,p1=0.2,p2=0.2,adprobability=0.01,memoryperiods=2):
		self.nodes=nodes
		self.agents_pri={}
		self.agents_typ={}
		self.all_agent=[]
		self.agents_connection=[]
		self.pricetype=pricetype
		self.graph_type=graph_type
		self.happy_threshold=happy_threshold
		self.degree=degree
		self.p1=p1
		self.p2=p2
		self.ep=1-self.p1-self.p2
		self.G=nx.Graph()
		self.adprobability=adprobability
		self.typstat=[]
		self.memoryperiods=memoryperiods
		self.agents_learn_cost=[[100]*self.memoryperiods]*self.nodes
		self.agents_learn_choose=[[2]*self.memoryperiods]*self.nodes
		self.agents_sociallearn_weight=[]
		self.rtpcost=[0]*3
		self.fpcost=[]
		self.processbarsharp=[chr(22)]
		self.processbarabsense=['']*50
		self.processbarcount=0
		self.processbartotal=[]

	def initial(self):
		self.happy_threshold=0.3
		self.degree=3
		self.p1=0.2
		self.p2=0.2
		self.ep=1-self.p1-self.p2
		self.adprobability=0.01

	def processbar(self):
		self.processbarcount+=1
		sys.stdout.write(str(int((self.processbarcount/self.processbartotal)*100))+'%\t['+''.join(self.processbarsharp)+''.join(self.processbarabsense)+']'+"\r")
		sys.stdout.flush()
		self.processbarsharp=[chr(22)]*int((self.processbarcount/self.processbartotal)*50)
		self.processbarabsense=[' ']*(50-int((self.processbarcount/self.processbartotal)*50))

	def populate(self):
		self.all_agent=list(range(self.nodes))
		random.shuffle(self.all_agent)
		agent_price=[self.all_agent[i::self.pricetype] for i in range(self.pricetype)]
		for i in range(self.pricetype):
			#create agents for each pricetype
			self.agents_pri.update(dict(zip(agent_price[i],[2]*len(agent_price[i]))))
		random.shuffle(self.all_agent)
		agent_type=[self.all_agent[0:int(self.p1*len(self.all_agent))],self.all_agent[int(self.p1*len(self.all_agent)):int(self.p1*len(self.all_agent))+int(self.p2*len(self.all_agent))],self.all_agent[int(self.p1*len(self.all_agent))+int(self.p2*len(self.all_agent)):]]
#		print(len(agent_type[1]))
		for i in range(3):
			self.agents_typ.update(dict(zip(agent_type[i],[i+1]*len(agent_type[i]))))
			#print(len(agent_type[i]))

		if self.graph_type == 'BA':
			self.G=nx.random_graphs.barabasi_albert_graph(self.nodes,self.degree)
		elif self.graph_type == 'RG':
			self.G = nx.random_graphs.random_regular_graph(self.degree,self.nodes)
		elif self.graph_type == 'ER':
			self.G = nx.random_graphs.erdos_renyi_graph(self.nodes,self.degree)
		elif self.graph_type == 'WS':
			self.G = nx.random_graphs.watts_strogatz_graph(self.nodes,self.degree,0.3)

		self.agents_connection=self.G.adjacency_list()
		self.typstat=collections.Counter(self.agents_typ.values())

		self.agents_sociallearn_weight=np.random.random_sample(self.nodes)
		#print(self.agents_typ)

	def socialnetwork(self,node):
		price=self.agents_pri[node]
		typ=self.agents_typ[node]
		count_different=0
		count_same=0
		#-1 for unchange, 1 for change
		a=self.learn(node)
		weight=0

		for neighbor in self.agents_connection[node]:
			if self.agents_pri[neighbor] != price:
				count_different += 1
			else:
				count_same += 1

		if (count_different+count_same) == 0:
			return False
		else:
			b=float(count_different)/(count_different+count_same)

		weight=(1-self.agents_sociallearn_weight[node])*a+self.agents_sociallearn_weight[node]*b

		if weight > self.happy_threshold:
			return True
		elif np.random.random()<self.adprobability and price==2:
			return True
		else:
			return False

	def learn(self,node):
		price=self.agents_pri[node]
		typ=self.agents_typ[node]
		for i in range(self.memoryperiods-1):
			self.agents_learn_cost[node][self.memoryperiods-1-i]=self.agents_learn_cost[node][self.memoryperiods-1-i-1]
			self.agents_learn_choose[node][self.memoryperiods-1-i]=self.agents_learn_choose[node][self.memoryperiods-1-i-1]
		self.agents_learn_choose[node][0]=price
		if price==2:
			self.agents_learn_cost[node][0]=self.fpcost
		elif price==1:
			self.agents_learn_cost[node][0]=self.rtpcost[typ-1]
		if self.agents_learn_choose[node][self.agents_learn_cost[node].index(min(self.agents_learn_cost[node]))] != price:
			return (self.agents_learn_cost[node][0]/min(self.agents_learn_cost[node])-1)*10
		else:
			return 0

	def update(self):
		choosertp=[0]*3
		for agent in self.agents_pri:
			if self.agents_pri[agent]==1:
				choosertp[self.agents_typ[agent]-1]+=1
		with open('consumernumber', 'w') as f:
			for i in range(3):
				f.write('consumer(\'%d\')=%d;\n'%(i+1,self.typstat[i]))
			for i in range(3):
				f.write('choosertp(\'%d\')=%d;\n'%(i+1,choosertp[i]))
		a=subprocess.call("gams ./simplified.gms")
		#a.communicate()
		#i = os.system('cls')
		with open('rtpcost', 'r') as f:
			for i in range (3):
				line=f.readline()
				self.rtpcost[i]=float(line.strip())
			line=f.readline()
			self.fpcost=float(line.strip())
		old_agents=copy.deepcopy(self.agents_pri)
		count_change=0
		for agent in old_agents:
			if self.socialnetwork(agent):
				old_agents[agent]=3-self.agents_pri[agent]
				count_change+=1
		#print(count_change)
		self.agents_pri=old_agents

		self.processbar()
		if count_change==0:
			return False

	def plotanimation(self,periods,filename):
		fig, ax = plt.subplots()
#		fig.set_tight_layout(True)
		agent_colors = {1:'b', 2:'r', 3:'g', 4:'c', 5:'m', 6:'y', 7:'k'}
		pos=nx.spring_layout(self.G)

		c1=[agent for agent in self.agents_pri if self.agents_pri[agent]==1]
		c2=[agent for agent in self.agents_pri if self.agents_pri[agent]==2]

		nx.draw_networkx_nodes(self.G,pos,nodelist=c1,node_color='r')
		nx.draw_networkx_nodes(self.G,pos,nodelist=c2,node_color='b')
		nx.draw_networkx_edges(self.G,pos)
#		for agent in self.agents_pri:
#			c1=[]
#			ax.scatter(agent[0]+0.5, agent[1]+0.5, color=agent_colors[self.agents_pri[agent]],alpha=0.7)

		def plotgif(i):
			label = 'Time period {0}'.format(i+1)
			plt.cla()
			self.update()
			c1=[agent for agent in self.agents_pri if self.agents_pri[agent]==1]
			c2=[agent for agent in self.agents_pri if self.agents_pri[agent]==2]

			nx.draw_networkx_nodes(self.G,pos,nodelist=c1,node_color='r',node_size=30)
			nx.draw_networkx_nodes(self.G,pos,nodelist=c2,node_color='b',node_size=30)
			nx.draw_networkx_edges(self.G,pos)

			ax.set_title(label, fontsize=10, fontweight='bold')

			return ax

		ani = animation.FuncAnimation(fig, plotgif, frames=list(range(periods)), interval=1000)
		FFwriter = animation.FFMpegWriter(fps=1)
		ani.save('%s.mp4'%filename,writer = FFwriter)

	def statistic(self,periods):
		self.processbartotal=periods*5*6
		c11=[]
		c21=[]
		c31=[]
		c2=[]
		for i in range(periods):
			count_c11=0
			count_c21=0
			count_c31=0
			for agent in self.agents_pri:
				if self.agents_typ[agent]==1:
					if self.agents_pri[agent]==1:
						count_c11+=1
				elif self.agents_typ[agent]==2:
					if self.agents_pri[agent]==1:
						count_c21+=1
				elif self.agents_typ[agent]==3:
					if self.agents_pri[agent]==1:
						count_c31+=1
			c11.append(count_c11/self.nodes)
			c21.append(count_c21/self.nodes)
			c31.append(count_c31/self.nodes)
			c2.append((self.nodes-count_c11-count_c21-count_c31)/self.nodes)
			self.update()

		t=list(range(periods))
		return t,c11,c31,c21
		#c12=[self.p1-c11[i] for i in range(len(c11))]
		#c22=[self.p2-c21[i] for i in range(len(c21))]
		#c32=[1-self.p1-self.p2-c31[i] for i in range(len(c11))]
		#plt.figure(figsize=(8,5))
		#plt.plot(c11,label="Type 1 consumers choose RTP",color="red",linewidth=2)
		#plt.plot(c21,"b--",label="Type 2 consumers choose RTP")
		#plt.plot(c31,"g-.",label="Type 3 consumers choose RTP")
		#plt.plot(c2,"y:",label="Consumers choose FP")

	def plotandsimulate(self,periods):
		sensetiveanalyse={'degree':[3,5,7],'threshold':[0.2,0.4,0.6],'probability':[0.01,0.1,0.5],\
		'p1':[0,0.2,0.4],'p2':[0,0.2,0.4]}
		simulationobject='degree'
		
		for i in range(3):
			self.initial()
			self.degree=sensetiveanalyse[simulationobject][i]
			self.populate()
			t,c11,c31,c21=self.statistic(periods)
			with open(simulationobject+'%s'%sensetiveanalyse[simulationobject][i], 'w') as f:
				for i in t:
					f.write('%.4f,%.4f,%.4f\n'%(c11[i],c31[i],c21[i]))
##########################1
		simulationobject='threshold'

		for i in range(3):
			self.initial()
			self.happy_threshold=sensetiveanalyse[simulationobject][i]
			self.populate()
			t,c11,c31,c21=self.statistic(periods)
			with open(simulationobject+'%s'%sensetiveanalyse[simulationobject][i], 'w') as f:
				for i in t:
					f.write('%.4f,%.4f,%.4f\n'%(c11[i],c31[i],c21[i]))
############################2
		simulationobject='probability'

		for i in range(3):
			self.initial()
			self.adprobability=sensetiveanalyse[simulationobject][i]
			self.populate()
			t,c11,c31,c21=self.statistic(periods)
			with open(simulationobject+'%s'%sensetiveanalyse[simulationobject][i], 'w') as f:
				for i in t:
					f.write('%.4f,%.4f,%.4f\n'%(c11[i],c31[i],c21[i]))
#############################3
		simulationobject='p1'

		for i in range(3):
			self.initial()
			self.p1=sensetiveanalyse[simulationobject][i]
			self.populate()
			t,c11,c31,c21=self.statistic(periods)
			with open(simulationobject+'%s'%sensetiveanalyse[simulationobject][i], 'w') as f:
				for i in t:
					f.write('%.4f,%.4f,%.4f\n'%(c11[i],c31[i],c21[i]))
##############################4
		simulationobject='p2'

		for i in range(3):
			self.initial()
			self.p2=sensetiveanalyse[simulationobject][i]
			self.populate()
			t,c11,c31,c21=self.statistic(periods)
			with open(simulationobject+'%s'%sensetiveanalyse[simulationobject][i], 'w') as f:
				for i in t:
					f.write('%.4f,%.4f,%.4f\n'%(c11[i],c31[i],c21[i]))
##############################5

c1 = choose()
c1.plotandsimulate(100)

#a=subprocess.call("shutdown -s -t 60")