import os
import csv
import pandas as pd 
import math 
import numpy as np
import re
from os import listdir
from os.path import isfile, join

'''get player stats read team stats, create files for players
 for shot charts and distribution of distance and left right '''

season = str(raw_input("Pick a season: 13-14, 14-15, 15-16. "))
mypath = "Shots 20" + season
files_compiledteam_shots = [f for f in listdir(mypath) if isfile(join(mypath, f))]

def get_player_SC(team, TeamGameShotData_Season):
	#TeamGameShotData_Season is team's shot data over season 
	TeamShots_Season = TeamGameShotData_Season.loc[TeamGameShotData_Season["team"] == team]
	players = list(set(TeamShots_Season["player"]))
	for i in range(len(players)):
		Player_Shots = TeamShots_Season.loc[TeamShots_Season["player"] == players[i]]
		save_to_file(Player_Shots, players[i], team)

def save_to_file(Player_Shots, player, team):
	filename = mypath + "/" + team + "/" + player + ".csv"
	if not os.path.exists(os.path.dirname(filename)):
		os.makedirs(os.path.dirname(filename))
	Player_Shots.to_csv(filename, sep = '\t', index = False)
	#with open(filename, "w") as f:
		#writer = csv.writer(f, delimiter="\t")
        #header of the data                
        #writer.writerow(["Game_id","player","pd", "homeaway", "team","distance","angle", "leftside", "left","top", "description", "playerid","shotnum","made", "FGA3", "assisted","jumper", "layup", "dunk"])
        #writer.writerows(Player_Shots)

def main():
	for i in range(len(files_compiledteam_shots)):
		team = files_compiledteam_shots[i].split(".csv")[0]
		##check if file has data - must be > 1 byte
		if not files_compiledteam_shots[i].startswith('.'):
			if os.path.getsize(mypath + "/" + files_compiledteam_shots[i]) > 1:
				print "Got " + team
				TeamGameShotData_Season = pd.read_csv(mypath + "/" + files_compiledteam_shots[i], sep = '\t')
				data = get_player_SC(team, TeamGameShotData_Season)
	os.system('say "DunDunDun Donnne"')
	os.system('afplay /System/Library/Sounds/Sosumi.aiff')


if __name__ == '__main__':
	main()