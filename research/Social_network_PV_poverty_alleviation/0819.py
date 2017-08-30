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

#Two status 0 and 1 for uninstall and install

class choose (object):
	def __init__(self,threshold=0.7,degree=7,graph_type='BA',adprobability=0.005):
		self.nodes=200
		self.agents_broke=[0]*self.nodes
		self.agents_status=[0]*self.nodes
		self.all_agent=[]
		self.threshold=threshold

		self.agents_connection=[]
		self.graph_type=graph_type
		self.threshold=threshold
		self.degree=degree
		self.G=nx.Graph()

		self.adprobability=adprobability
		self.agents_sociallearn_weight=[]

		self.expectedprob=[0.4]*self.nodes
		self.realprob=0.1

		self.R=1
		self.D=10
		self.A=0

	def initial(self):
		self.realprob=0.1
		self.threshold=0.7
		self.degree=7
		self.adprobability=0.01
		self.agents_broke=[0]*self.nodes
		self.agents_status=[0]*self.nodes
		self.expectedprob=[0.4]*self.nodes

	def populate(self):
		self.all_agent=list(range(self.nodes))

		if self.graph_type == 'BA':
			self.G=nx.random_graphs.barabasi_albert_graph(self.nodes,self.degree)
		elif self.graph_type == 'RG':
			self.G = nx.random_graphs.random_regular_graph(self.degree,self.nodes)
		elif self.graph_type == 'ER':
			self.G = nx.random_graphs.erdos_renyi_graph(self.nodes,self.degree)
		elif self.graph_type == 'WS':
			self.G = nx.random_graphs.watts_strogatz_graph(self.nodes,self.degree,0.3)

		self.agents_connection=self.G.adjacency_list()

		self.agents_sociallearn_weight=np.random.random_sample(self.nodes)
		#print(self.agents_sociallearn_weight)

	def socialnetwork(self,node,ep,Rt):
		if self.agents_status[node]==1:
			return False

		if Rt==self.R:
			Rt=self.R+self.A
		count_different=0
		count_same=0
		count_broke=0

		prob=ep

		epi=0
		weight=0
		b=0

		for neighbor in self.agents_connection[node]:
			if self.agents_status[neighbor] == 1:
				count_different += 1
				if self.agents_broke[neighbor] == 1:
					count_broke+=1
			else:
				count_same += 1

		if (count_different+count_same) == 0:
			return False
		else:
			b=float(count_different)/(count_different+count_same)

		if count_broke>=1:
			prob=1
		elif b>0 and count_broke==0:
			prob=0

		epi=(Rt-self.D*prob)/self.R
		weight=(1-self.agents_sociallearn_weight[node])*epi+self.agents_sociallearn_weight[node]*b

		self.expectedprob[node]=prob

		if weight > self.threshold:
			return True
		elif np.random.random()<self.adprobability and self.agents_status[node]==0:
			return True
		else:
			return False

	def update(self,t):
		old_agents_status=self.agents_status
		old_agents_broke=self.agents_broke
		count_change=0
		for agent in self.all_agent:
			if self.socialnetwork(agent,self.expectedprob[agent],self.R-0.05*t):
				old_agents_status[agent]=1-self.agents_status[agent]
				count_change+=1
		#print(count_change)
		self.agents_status=old_agents_status

		for agent in self.all_agent:
			if self.agents_status[agent]==1:
				if self.agents_broke[agent]==0:
					if np.random.random()<self.realprob:
						old_agents_broke[agent]=1
		self.agents_broke=old_agents_broke
		if count_change==0:
			return False

	def statistic(self,periods):
		c_ins=[]
		c_degree=[]
		for i in range(periods):
			count_install=0
			for agent in self.all_agent:
				if self.agents_status[agent]==1:
					count_install+=1
			c_ins.append(count_install)
			self.update(i)

		for agent in self.all_agent:
			if self.agents_status[agent]==1:
				c_degree.append(self.G.degree(agent))

		t=list(range(periods))
		return t,c_ins,c_degree

	def plotandsimulate(self,periods):
		sensetiveanalyse={'degree':[3,5,7,9,11],'realep':[0,0.05,0.10,0.15,0.2],\
		'probability':[0.001,0.005,0.01,0.05,0.1]}
#############################
		simulationobject='degree'

		for i in range(5):
			x_ins=[]
			for k in range(100):
				self.initial()
				self.degree=sensetiveanalyse[simulationobject][i]
				self.populate()
				t,c_ins,c_degree=self.statistic(periods)
				x_ins.append(c_ins)
			d_ins=[]
			for j in range(periods):
				a=0
				for k in range(100):
					a+=x_ins[k][j]
				d_ins.append(a/100)
			with open(simulationobject+'%s'%sensetiveanalyse[simulationobject][i], 'w') as f:
				for j in range(periods):
					f.write('%d\n'%(d_ins[j]))
##########################1
		simulationobject='realep'

		for i in range(5):
			x_ins=[]
			for k in range(100):
				self.initial()
				self.realprob=sensetiveanalyse[simulationobject][i]
				self.populate()
				t,c_ins,c_degree=self.statistic(periods)
				x_ins.append(c_ins)
			d_ins=[]
			for j in range(periods):
				a=0
				for k in range(100):
					a+=x_ins[k][j]
				d_ins.append(a/100)
			with open(simulationobject+'%s'%sensetiveanalyse[simulationobject][i], 'w') as f:
				for j in range(periods):
					f.write('%d\n'%(d_ins[j]))
############################2
		simulationobject='probability'

		for i in range(5):
			x_ins=[]
			for k in range(100):
				self.initial()
				self.adprobability=sensetiveanalyse[simulationobject][i]
				self.populate()
				t,c_ins,c_degree=self.statistic(periods)
				x_ins.append(c_ins)
			d_ins=[]
			for j in range(periods):
				a=0
				for k in range(100):
					a+=x_ins[k][j]/100
				d_ins.append(a)
			with open(simulationobject+'%s'%sensetiveanalyse[simulationobject][i], 'w') as f:
				for j in range(periods):
					f.write('%d\n'%(d_ins[j]))
##############################3

c1 = choose()
c1.plotandsimulate(20)

#a=subprocess.call("shutdown -s -t 60")