import pandas as pd
import os
import numpy as np

Team_Choice = "Abil Christian"
game_details = pd.read_csv("Game_Deets.csv",sep = ',')
homeschedule = list(set(game_details[game_details['HomeTeam'] == Team_Choice]["Game_id"]))
fullsched = homeschedule 
game_days = [None] * len(fullsched)

for i in range(len(fullsched)):
	game_days[i] = list(set(game_details[game_details["Game_id"] == fullsched[i]]["Date"]))[0]
	##for every game day, find the corresponding game 
filename = [None] * len(fullsched)
folder_names = [None] * len(fullsched)
folder_names[0] = os.path.join(".",game_days[0]) 
filename[0] = "%s/%s.csv" % (folder_names[0], fullsched[0])
pbp = pd.read_csv(filename[0],delimiter = '\t')  #read in file
PBP_description = [None] * len(pbp)

pbp = pd.read_csv(filename[j],delimiter = '\t')  #read in file
pbp = pbp.drop(pbp.index[len(pbp)-1]) #drop last row
game_id = np.zeros(shape = (len(pbp),1))  #create game ID for PBP data for each game
game_id[:] = fullsched[j]  #create game ID
pbp = np.column_stack([game_id,pbp])  #concatenate columns 
pbp = pd.DataFrame(pbp, columns = ["Game_id","time", "away", "score","home"])
		

if not pbp.loc[len(pbp)-1,'away'].lower().startswith('end'):
	print "Missing End of Game"
	#pbp.append(["0:00","End of Game",pbp["score"][len(pbp)-2], "End of Game"])
	pbp.loc[len(pbp)] = [game_id[1], "0:00","End of Game",pbp["score"][len(pbp)-2], "End of Game"]
	print len(pbp)
	game_id = np.append(game_id,fullsched[j]) 
	print len(game_id)

Team_GamePBP = pd.DataFrame()
timeout = np.zeros(shape = (len(pbp),1))
foul = np.zeros(shape = (len(pbp),1))
home_off_poss = np.zeros(shape = (len(pbp),1))  #home team on offense 
possession = np.zeros(shape = (len(pbp),1))  #beginning of possession
my_team = np.zeros(shape = (len(pbp),1))   #1 if stats for team of interest
home_game = np.zeros(shape = (len(pbp),1))   #1 if team of interest is playing home game 

if list(set(game_details[game_details.Game_id == fullsched[0]]["HomeTeam"] == Team_Choice))[0]:
	home_game[range(len(pbp))] = 1
elif list(set(game_details[game_details.Game_id == fullsched[0]]["AwayTeam"] == Team_Choice))[0]:
	home_game[range(len(pbp))] = 0
timeout = np.zeros(shape = (len(pbp),1))

for i in range(len(pbp)):
	if pbp['away'][i] is ' ':					
		home_off_poss[i] = 1
		PBP_description[i] = pbp['home'][i]
	else:
		home_off_poss[i] = 0	
		PBP_description[i] = pbp['away'][i]

for i in range(23,len(pbp)):

	if "timeout" in pbp['score'][i].lower():
		timeout[i] = 1
	##make one PBP column
	if pbp['away'][i] is ' ':					
		home_off_poss[i] = 1
		PBP_description[i] = pbp['home'][i]
	else:
		home_off_poss[i] = 0	
		PBP_description[i] = pbp['away'][i]

	if ((home_off_poss[i] == 1) and (home_game[i] == 1)):
		my_team[i] = 1
	elif ((home_off_poss[i] == 0) and (home_game[i] == 0)):
		my_team[i] = 1
	
	if "foul" in PBP_description[i].lower():
		foul[i] = 1
		if home_off_poss[i] == 1:
			home_off_poss[i] = 0
		elif home_off_poss[i] == 0:
			home_off_poss[i] = 1

	if i < (len(pbp)-1):

		if timeout[i] == 1: 
			#if home team has next play
			if ((pbp['away'][i+1] is ' ') and home_game[i] == 1): 
				my_team[i] = 1
				home_off_poss[i] = 1
			if ("foul" in pbp['away'][i+1].lower()) and (home_game[i] == 1):
				home_off_poss[i] = 1
				my_team[i] = 1
			#if team is road team
			if ((pbp['home'][i+1] is ' ') and home_game[i] == 0):
				my_team[i] = 1
				##opponent (home team) fouls them after timeout 
			if ("foul" in pbp['home'][i+1].lower()) and (home_game[i] == 1):
				my_team[i] = 1
		#print PBP_description[i] + " " + str(i)

		if home_off_poss[i] != home_off_poss[i-1]:
			possession[i] = 1
			if foul[i] == 1:
				possession[i] = 0
				possession[i+1] = 1
				if "foul" in PBP_description[i+1].lower():
					possession[i+1] = 0
					possession[i+2] = 1
					if "timeout" in PBP_description[i+2].lower():
						possession[i+2] = 0
						possession[i+3] = 1
				if "timeout" in PBP_description[i+1].lower():
						possession[i+1] = 0
						possession[i+2] = 1
	##home off poss is not updated soon enough for possession on timeouts 
			#print PBP_description[i] + str(i)
			# print "poss"
			# print PBP_description[i]
			# print possession[i]
			# print "i + 3"
			# print PBP_description[i+3]
			# print possession[i+3]
			# 