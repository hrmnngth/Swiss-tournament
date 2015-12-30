#!/usr/bin/env python
#
# player.py -- player info of tournament
#

class Player(object):

	def __init__(self,wins, player_id, name):
		self.wins=wins
		self.player_id=player_id
		self.name=name		

	def getWins(self):
		return self.wins

	def getPlayerId(self):
		return self.player_id

	def getName(self):
		return self.name


