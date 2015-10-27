import csv
import pandas as pd 
import math 
import numpy as np
import re
import os
from datetime import datetime


'''this file cleans the game detail files for each conference--combining all and extracting
any useful info, eg team record and making one file
Step 2 after getting the paly by play from ESPN
Gets wins and losses for each team and winning percentage 

'''

#team_gameID = pd.read_csv("Team_GameIDs.csv", delimiter = ',')
conferences = ["ACC_ConfTourney", "Big10", "SEC","A10", "PAC12","Big12","BigEast"]
#conferences = ["ACC_ConfTourney", "Big10"]
filenames = []
game_details = pd.DataFrame()  #create empty dataframe for all read in game details


#"cbb-play-data/"+ 
for conf in conferences:
	filenames.append(conf+"Team_GameIDs.csv")

#view all colmns rows 390 to 396 game_details.iloc[390:396,:]
##read in all game IDs by conference and form one dataframe 
for f in filenames:
	conf_game_details = pd.read_csv(f, delimiter = ',')
	game_details = game_details.append(conf_game_details) 
	print "added %s" % f

conf_record = [None] * len(game_details)
overall_record = [None] * len(game_details)
opponent_record = [None] * len(game_details)

#get wins, losses, and winning percentage for both home and visiting team
TeamRecords = []
for team in ["HomeRecord", "AwayRecord"]:
	overall_record = game_details[team].str.split(",").str[0]
	overall_record = overall_record.str.lstrip("(")
	wins = overall_record.str.split("-").str[0]
	losses = overall_record.str.split("-").str[1]
	win_percentage = np.zeros(shape = (len(game_details),1))

#handling if some values are " "
	for i in range(len(game_details)):
	#team record overall and conference 
		if not wins.iloc[i].isspace():
			Ws= float(wins.iloc[i])	
			Ls = int(losses.iloc[i])
			win_percentage[i] = Ws/(Ws + Ls)

	TeamRecords.extend([wins,losses,win_percentage])

index = game_details.index.values
#Cleaned_Game_Details = pd.DataFrame(TeamRecords, columns = ["Wins by Home Team", "Losses by Home Team", "Record of Home Team","Wins by Road Team", "Losses by Road Team", "Record of Road Team"])
new_Game_Deets = game_details[["Game_id", "Date", "HomeTeam","HomeRank","AwayTeam","AwayRank"]]

#titles = ["Game_id", "Date", "HomeTeam","HomeRank","AwayTeam","AwayRank", "Wins_Home", "Losses_Home","Win Percent", "Wins_Visitor","Losses_Visitor","Visitor Win Percentage"]
Cleaned_Game_Details = pd.DataFrame({"Wins_Home" : TeamRecords[0], "Losses_Home" : TeamRecords[1], "Win Percent" : TeamRecords[2].tolist(), "Wins_Visitor" : TeamRecords[3], "Losses_Visitor" : TeamRecords[4], "Visitor Win Percentage" : TeamRecords[5].tolist()}, index = index)
#titles = ["Wins_Home", "Losses_Home","Win Percent", "Wins_Visitor","Losses_Visitor","Visitor Win Percentage"]
#Cleaned_Game_Details = pd.DataFrame({"Wins_Home" : TeamRecords[0], "Losses_Home" : TeamRecords[1], "Win Percent" : TeamRecords[2].tolist(), "d" : TeamRecords[3], "e" : TeamRecords[4], "f" : TeamRecords[5].tolist()}, index = index, columns = titles)
Full_Game_Deets = pd.concat([new_Game_Deets,Cleaned_Game_Details], axis = 1)
#with pd.option_context('display.max_rows', 1500, 'display.max_columns', 12):
#	print Full_Game_Deets
Full_Game_Deets = Full_Game_Deets.reset_index()   #reset index so can reference one value

gamelist = []
UniqueFull_Game_Deets = pd.DataFrame()
for i in range(len(Full_Game_Deets)):
	game = Full_Game_Deets["Game_id"][i]
	#print Full_Game_Deets.iloc[i]
	if game not in gamelist:
		UniqueFull_Game_Deets = UniqueFull_Game_Deets.append(Full_Game_Deets.iloc[i])
		gamelist.append(Full_Game_Deets["Game_id"][i])

#Full_Game_Deets.to_csv("TEST GAME DEETS.csv",sep = '\t')
colms = ["Game_id", "Date", "HomeTeam","HomeRank","AwayTeam","AwayRank", "Wins_Home", "Losses_Home","Win Percent", "Wins_Visitor","Losses_Visitor","Visitor Win Percentage"]
UniqueFull_Game_Deets = UniqueFull_Game_Deets[colms]
UniqueFull_Game_Deets = pd.DataFrame(UniqueFull_Game_Deets, columns = colms)

print UniqueFull_Game_Deets.shape
UniqueFull_Game_Deets.to_csv("Game_Deets.csv",sep = '\t')
