import csv
import pandas as pd 
import math 
import numpy as np
import re
import os
from datetime import datetime

'''this file cleans the game detail files--combining all and extracting
any useful info, eg team record 
Step 3 -- allow user to select team and create stats from PBP data 
'''
#team_gameID = pd.read_csv("Team_GameIDs.csv", delimiter = ',')
conferences = ["ACC_ConfTourney", "Big10", "SEC","A10", "PAC12","Big12","BigEast"]
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

game_details.head(10)  #view first 10 rows 

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
Cleaned_Game_Details = pd.DataFrame({"Wins_Home" : TeamRecords[0], "Losses_Home" : TeamRecords[1], "Win Percent" : TeamRecords[2].tolist(), "Wins_Visitor" : TeamRecords[3], "Losses_Visitor" : TeamRecords[4], "Visitor Win Percentage" : TeamRecords[5].tolist()}, index = index)
Full_Game_Deets = pd.concat([new_Game_Deets,Cleaned_Game_Details], axis = 1)

Full_Game_Deets.to_csv("gameDeetsTest.csv",sep = '\t')

#get unique list of team names 
home_teams = set(game_details["HomeTeam"])
away_teams = set(game_details["AwayTeam"])
TeamList = list(home_teams) + list(away_teams)
TeamList = pd.DataFrame(list(set(TeamList)))  #unique list of team names 
print TeamList


#Num_team_choice = int(raw_input("Please select the number corresponding to the team you want: "))
Num_team_choice = 125
Team_Choice = TeamList[Num_team_choice]

homeschedule = list(set(game_details[game_details['HomeTeam'] == Team_Choice]["Game_id"]))
awayschedule = list(set(game_details[game_details['AwayTeam'] == Team_Choice]["Game_id"]))
fullsched = homeschedule + awayschedule  ##full unique list of games played listed as game_ids

##get the list of dates that team played on 
game_days = list(set(game_details[game_details["Game_id"].isin(fullsched)]["Date"]))
##for every game day, find the corresponding game 
filename = [None] * len(fullsched)
folder_names = [None] * len(fullsched)
Team_GamePBP = pd.DataFrame()
#os.getcwd()
##for each game in schedule
for j in range(len(fullsched)):
	folder_names[j] = os.path.join(".",game_days[j])  #path for the folder
	filename[j] = "%s/%s.csv" % (folder_names[j], fullsched[j])  #path of file
	pbp = pd.read_csv(filename[j],delimiter = '\t')  #read in file
	game_id = np.zeros(shape = (len(pbp),1))  #create game ID for PBP data for each game
	game_id[:] = fullsched[j]  #create game ID
	pbp = np.column_stack([game_id,pbp])  #concatenate columns 
	pbp = pd.DataFrame(pbp, columns = ["Game_id","time", "away", "score","home"])
		
	my_team = np.zeros(shape = (len(pbp),1))   #1 if stats for team of interest
	home_game = np.zeros(shape = (len(pbp),1))   #1 if team of interest is playing home game 

	minutes = np.zeros(shape = (len(pbp),1))
	seconds = np.zeros(shape = (len(pbp),1))
	away_score = np.zeros(shape = (len(pbp),1))
	home_score = np.zeros(shape = (len(pbp),1))
	home_poss = np.zeros(shape = (len(pbp),1))
	home_margin = np.zeros(shape = (len(pbp),1))
	home_win = np.zeros(shape = (len(pbp),1))
	away_points_scored = np.zeros(shape = (len(pbp),1))
	home_points_scored = np.zeros(shape = (len(pbp),1))
	before_away_points = np.zeros(shape = (len(pbp),1))
	before_home_points = np.zeros(shape = (len(pbp),1))
	
	turnover = np.zeros(shape = (len(pbp),1))
	def_reb = np.zeros(shape = (len(pbp),1))
	off_reb = np.zeros(shape = (len(pbp),1))
	steal = np.zeros(shape = (len(pbp),1))
	home_win = np.zeros(shape = (len(pbp),1))
	FGA3 = np.zeros(shape = (len(pbp),1))  #3 PT FGA
	FGA3M = np.zeros(shape = (len(pbp),1))
	FGA = np.zeros(shape = (len(pbp),1))
	FGM = np.zeros(shape = (len(pbp),1))
	half = np.zeros(shape = (len(pbp),1))
	foul = np.zeros(shape = (len(pbp),1))
	FTA = np.zeros(shape = (len(pbp),1))
	block = np.zeros(shape = (len(pbp),1))
	assist = np.zeros(shape = (len(pbp),1))
	sec_remaining = np.zeros(shape = (len(pbp),1))
	timeout = np.zeros(shape = (len(pbp),1))
	first_name = [None] * len(pbp)
	last_name = [None] * len(pbp)
	player = [None] * len(pbp)
	player2 = [None] * len(pbp)

	half_index = 0
	game_index = 0
	overtime_indicator = 0
	period_counter = 2

	PBP_description = [None] * len(pbp)

	for i in range(len(pbp)):
		global overtime_indicator
		global period_counter

		minutes[i] = pbp['time'][i].split(":")[0]
		seconds[i] = pbp['time'][i].split(":")[1]
		##seconds remaining in half
		sec_remaining[i] = 60 * int(minutes[i]) + int(seconds[i])
		home_margin[i] = home_score[i] - away_score[i]
		
		#mark if 1st/2nd half/OT 
		if sec_remaining[i] < 60:
		
			if pbp['score'][i].lower().startswith('end') and pbp['score'][i].lower().endswith('1st half'):
				half_index = i
				half[0:half_index] = '1'
	 
			#if 'end .* 2nd half' in pbp['score'][i].lower():
			if pbp['score'][i].lower().startswith('end') and pbp['score'][i].lower().endswith('2nd half'):
				game_index = i
				half[half_index + 1:game_index] = '2'
				overtime_indicator = 1
			#game didn't go into overtime, ie 2 halves 
			if overtime_indicator == 0 and pbp['score'][i].lower().startswith('end') and pbp['score'][i].lower().endswith('game'): 
			#overtime_indicator == 0 & ('end .* game' in pbp['score'][i]):
				game_index = i
				half[half_index + 1:game_index] = '2'

			if overtime_indicator == 1 and pbp['score'][i].lower().startswith('end'):
				period_counter = period_counter + 1
				half[game_index + 1:i] = str(period_counter)
				game_index = i
		
		##if timeout, repeat score before timeout 
		if ("timeout" in pbp['score'][i].lower()) | ("end" in pbp['score'][i].lower()):
			away_score[i] = away_score[i-1]
			home_score[i] = home_score[i-1]
			timeout[i] = 1
		else:	
			away_score[i] = pbp['score'][i].split("-")[0]
			home_score[i] = pbp['score'][i].split("-")[1]
		
		
		if i > 1:
			away_points_scored[i] = int(away_score[i]) - int(away_score[i-1])
			home_points_scored[i] = int(home_score[i]) - int(home_score[i-1])
			before_home_points[i] = int(home_score[i]) - home_points_scored[i]
			before_away_points[i] =	int(away_score[i]) - away_points_scored[i]
		
		if pbp['away'][i] is ' ':					
			home_poss[i] = 1
			PBP_description[i] = pbp['home'][i]
		else:
			home_poss[i] = 0
			PBP_description[i] = pbp['away'][i]


		#indicator if team of interest -- 1 if team is home team and has ball or if they're away team and have the ball
		
		#if team of interest is the home team
		if list(set(Full_Game_Deets[Full_Game_Deets.Game_id == fullsched[j]]["HomeTeam"] == Team_Choice))[0]:
			home_game[range(len(pbp))] = 1
			if home_poss[i] == 1:
				my_team[i] = 1
		#if team of interest is the road team 
		elif list(set(Full_Game_Deets[Full_Game_Deets.Game_id == fullsched[j]]["AwayTeam"] == Team_Choice))[0]:
			home_game[range(len(pbp))] = 0
			if home_poss[i] == 0:
				my_team[i] = 1

		##create dummy vars for stats 
		if "turnover" in PBP_description[i].lower():
			turnover[i] = 1
		if "defensive rebound" in PBP_description[i].lower():
			def_reb[i] = 1
		if "offensive rebound" in PBP_description[i].lower():
			off_reb[i] = 1
		if "three point jumper" in PBP_description[i].lower():
			FGA3[i] = 1
		if ("three point jumper" in PBP_description[i].lower()) & ("made" in PBP_description[i]):
			FGA3M[i] = 1
		
		#possession on fouls should be with team with the ball, not team committing the foul
		if "foul" in PBP_description[i].lower():
			foul[i] = 1
			if home_poss[i] == 1:
				home_poss[i] = 0
			elif home_poss[i] == 0:
				home_poss[i] = 1

		if "block" in PBP_description[i].lower():
			block[i] = 1
		if "assist" in PBP_description[i].lower():
			assist[i] = 1
		if "free throw" in PBP_description[i].lower():
			FTA[i] = 1
		if ("made" in PBP_description[i].lower()) | ("missed" in PBP_description[i].lower()):
			FGA[i] = 1 - FTA[i] ##FTA is either 1 or 0, FGA included FTAs
		if "made" in PBP_description[i].lower():
			FGM[i] = 1 - FTA[i]    #if attempted FT, doesn't matter if made or missed, FGM will have counted made FT

		if foul[i] == 1: 
			first_name[i] = PBP_description[i].split(' ')[-2].rstrip(".")
			last_name[i] = PBP_description[i].split(' ')[-1].rstrip(".")
		else:
			first_name[i] = PBP_description[i].split(' ')[0]
			last_name[i] = PBP_description[i].split(' ')[1]

		if assist[i] == 1:
			CP_assist = PBP_description[i].split(" ")
			player2[i] = CP_assist[-2] + " " + CP_assist[-1].rstrip(".")

		player[i] = first_name[i] + " " + last_name[i]
		#print player
	###home wins 
	if away_score[-1] < home_score[-1]:
		home_win[range(len(pbp))] = 1
	else: 
		home_win[range(len(pbp))] = 0

	data = np.column_stack((game_id, PBP_description, my_team, home_game,sec_remaining, half,home_win, before_home_points,home_score, before_away_points,away_score,home_points_scored,away_points_scored,home_poss, player, player2,FGA,FGM,FTA,FGA3,FGA3M,turnover, block, steal, assist, foul,off_reb,def_reb, timeout))
	titles = ["Game_id", "PBP_description", "my_team","home_game", "sec_remaining", "half", "home_win", "before_home_points","home_score","before_away_points","away_score","home_points_scored","away_points_scored","home_poss","player","player2","FGA","made_FGA","FTA","3FGA","3FGA_made","turnover","block", "steal","assist", "foul","off_reb","def_reb", "timeout"]
	data = pd.DataFrame(data, columns = titles)

	Team_GamePBP = Team_GamePBP.append(data)   #PBP for all games played by a particular team 


merged_data = Team_GamePBP.merge(Full_Game_Deets, how = 'left', on = "Game_id") 

merged_data.to_csv("../Processed-PBP/test.csv",sep = '\t')



##unique list of games from year 

#print win_percentage[300:305]
##what's the diff btwn 
#game_details["HomeRecord"] and game_details["HomeRecord"].str.split(",")
