#!/usr/bin/env python
#
# player.py -- player info of tournament
#

class Player(object):

	def __init__(self,wins, player_id, name,matches):
		self.wins=wins
		self.player_id=player_id
		self.name=name
		self.matches=matches

	def getWins(self):
		return self.wins

	def getPlayerId(self):
		return self.player_id

	def getName(self):
		return self.name

	def getMatches(self):
		return self.matches




