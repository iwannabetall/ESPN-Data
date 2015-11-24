import csv
import pandas as pd 
import math 
import numpy as np
import re
import os
from datetime import datetime
'''
running the file "python [file name]" prints out a list of teams for which there is PBP data avail (only major conferences) 
Prompts/Allows user to select a team by number from the list of teams and outputs a file of all PBP data for the games from season
'''
###read in game details for alll conferences file created by step 2, file cbbPBPStep2_GameDetails
def Readme():
	#game_details = pd.read_csv("All_Conf_Game_Details.csv",sep = ',')
	game_details = pd.read_csv("Game_Deets.csv",sep = ',')
	return game_details


def TeamList(game_details):
##get returns list of teams for which i have data
	#get unique list of team names 
	home_teams = set(game_details["HomeTeam"])
	away_teams = set(game_details["AwayTeam"])
	TeamList = list(set(list(home_teams) + list(away_teams)))
	TeamList = sorted(TeamList)
	TeamList = pd.DataFrame(TeamList)  #unique list of team names 
	return TeamList

def schedule(Team_Choice, game_details):
	##returns the schedule for a team of choice (name of team)
	homeschedule = list(set(game_details[game_details['HomeTeam'] == Team_Choice]["Game_id"]))
	awayschedule = list(set(game_details[game_details['AwayTeam'] == Team_Choice]["Game_id"]))
	fullsched = homeschedule + awayschedule  ##full unique list of games played listed as game_ids
	game_days = [None] * len(fullsched)
	##get the list of dates that team played on 
	for i in range(len(fullsched)):
		game_days[i] = list(set(game_details[game_details["Game_id"] == fullsched[i]]["Date"]))[0]
	##for every game day, find the corresponding game 
	filename = [None] * len(fullsched)
	folder_names = [None] * len(fullsched)
	return {"fullsched": fullsched, "game_days": game_days}

#os.getcwd()
#a = schedule(Team_Choice,game_details)
def pbp_stats(fullsched, game_days, game_details, Team_Choice):
##for each game in schedule, create stats and append and then merge 
	filename = [None] * len(fullsched)
	folder_names = [None] * len(fullsched)
	Team_GamePBP = pd.DataFrame()
	no_gamecounter = 0   #count number of games that don't have PBP
	for j in range(len(fullsched)):
		folder_names[j] = os.path.join(".",game_days[j])  #path for the folder
		filename[j] = "%s/%s.csv" % (folder_names[j], fullsched[j])  #path of file
		#"./2015-02-21/400591202.csv"
		print "starting game " + str(j) + " " + folder_names[j] + " " + filename[j]
		if not os.path.isfile(filename[j]):
			no_gamecounter = no_gamecounter + 1
			continue  #PBP does not exist for all games, skip to next game

		pbp = pd.read_csv(filename[j],delimiter = '\t')  #read in file
		game_id = np.zeros(shape = (len(pbp),1))  #create game ID for PBP data for each game
		game_id[:] = fullsched[j]  #create game ID
		pbp = np.column_stack([game_id,pbp])  #concatenate columns 
		pbp = pd.DataFrame(pbp, columns = ["Game_id","time", "away", "score","home"])
		
		#handle erroneous PBP without end of game
		if not pbp.loc[len(pbp)-1,'away'].lower().startswith('end'):
			print "Missing End of Game"
		#pbp.append(["0:00","End of Game",pbp["score"][len(pbp)-2], "End of Game"])   ##WHY DOESN'T THIS WORK
			pbp.loc[len(pbp)] = [game_id[1], "0:00","End of Game",pbp["score"][len(pbp)-2], "End of Game"]
			game_id = np.append(game_id,fullsched[j])  #append to game id to get proper length

		my_team = np.zeros(shape = (len(pbp),1))   #1 if stats for team of interest
		home_game = np.zeros(shape = (len(pbp),1))   #1 if team of interest is playing home game 

		minutes = np.zeros(shape = (len(pbp),1))
		seconds = np.zeros(shape = (len(pbp),1))
		away_score = np.zeros(shape = (len(pbp),1))
		home_score = np.zeros(shape = (len(pbp),1))
		home_off_poss = np.zeros(shape = (len(pbp),1))  #home team on offense 
		possession = np.zeros(shape = (len(pbp),1))  #beginning of possession
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
		
		FTA1_1 = np.zeros(shape = (len(pbp),1))   #and one free throw
		FTA1_2 = np.zeros(shape = (len(pbp),1))   #first of two FTs
		FTA2_2 = np.zeros(shape = (len(pbp),1))	   #2nd of 2 shot FT
		FTA3 = np.zeros(shape = (len(pbp),1))   	#fouled shooting a 3 pointer -- 1 for first shot, 2 for 2nd, 3 for 3rd shot
		FTAlast = np.zeros(shape = (len(pbp),1))   	#FTA with REB opp

		block = np.zeros(shape = (len(pbp),1))
		assist = np.zeros(shape = (len(pbp),1))
		sec_remaining = np.zeros(shape = (len(pbp),1))
		timeout = np.zeros(shape = (len(pbp),1))
		first_name = [None] * len(pbp)
		last_name = [None] * len(pbp)
		player = [None] * len(pbp)
		player2 = [None] * len(pbp)  #player getting assist 

		half_index = 0
		game_index = 0
		overtime_indicator = 0
		period_counter = 2

		PBP_description = [None] * len(pbp)

		for i in range(len(pbp)):

			if pbp['away'][i] is ' ':					
				home_off_poss[i] = 1
				PBP_description[i] = pbp['home'][i]
			else:
				home_off_poss[i] = 0	
				PBP_description[i] = pbp['away'][i]

			if "foul" in PBP_description[i].lower():
				foul[i] = 1
				if home_off_poss[i] == 1:
					home_off_poss[i] = 0
				elif home_off_poss[i] == 0:
					home_off_poss[i] = 1

			###use i-1 b/c i+1 wont be defined 
			if i < (len(pbp)-1):

				if timeout[i] == 1: 
					#if home team has next play
					if ((pbp['away'][i+1] is ' ') and home_game[i] == 1): 
						home_off_poss[i] = 1
					if ("foul" in pbp['away'][i+1].lower()) and (home_game[i] == 1):
						home_off_poss[i] = 1
			
			if "free throw" in PBP_description[i].lower():
				FTA[i] = 1

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
			
				if pbp['home'][i].lower().startswith('end') and pbp['home'][i].lower().endswith('1st half'):
					half_index = i
					half[0:half_index] = '1'
		 
				#if 'end .* 2nd half' in pbp['score'][i].lower():
				if pbp['home'][i].lower().startswith('end') and pbp['home'][i].lower().endswith('2nd half'):
					game_index = i
					half[half_index + 1:game_index] = '2'
					overtime_indicator = 1
				#game didn't go into overtime, ie 2 halves 
				if overtime_indicator == 0 and pbp['home'][i].lower().startswith('end') and pbp['home'][i].lower().endswith('game'): 
				#overtime_indicator == 0 & ('end .* game' in pbp['score'][i]):
					game_index = i
					half[half_index + 1:game_index] = '2'

				if overtime_indicator == 1 and pbp['home'][i].lower().startswith('end'):
					period_counter = period_counter + 1
					half[game_index + 1:i] = str(period_counter)
					game_index = i
			

			if "timeout" in pbp['score'][i].lower():
				timeout[i] = 1
			##if timeout, repeat score before timeout 
			if (timeout[i] == 1) | ("end" in pbp['score'][i].lower()):
				away_score[i] = away_score[i-1]
				home_score[i] = home_score[i-1]
			else:	
				away_score[i] = pbp['score'][i].split("-")[0]
				home_score[i] = pbp['score'][i].split("-")[1]
			
			if i > 1:
				away_points_scored[i] = int(away_score[i]) - int(away_score[i-1])
				home_points_scored[i] = int(home_score[i]) - int(home_score[i-1])
				before_home_points[i] = int(home_score[i]) - home_points_scored[i]
				before_away_points[i] =	int(away_score[i]) - away_points_scored[i]
			
		##if missed FTA --> def reb --> FTA 
			#FTA --> timeout --> FTA 
			#1 and 1 
			# one FTA 
			#3 pt FTA 
			##rebounding opp on missed FTA -- immediately after FTA, it's change of poss or oreb 
			if (FTA[i] == 1): #and ((home_points_scored[i] + away_points_scored[i]) == 0):
				if (home_off_poss[i] != home_off_poss[i+1]) or ("offensive rebound" in PBP_description[i+1].lower()):
					FTAlast[i] = 1   ##***INCLUDES MADE FREE THROWS -- FOR PURPOSES OF FT ANALYSIS W/PRESSURE
				##two consecutive made FTs-->change poss
				#if (FTA[i+1] == 1) and (home_off_poss[i+2] != home_off_poss[i+1]):
				#	FTA1_2[i] = 1
				#	FTA2_2[i+1] = 1

				#j = i
				#while (home_off_poss[i] == home_off_poss[j+1]) or ("timeout" in pbp['score'][j+1].lower()):
				#	if FTA[i+1] == 1:

			'''###dealing with possessions
			#indicator if team of interest -- 1 if team is home team and has ball or if they're away team and have the ball
			#first zero gets value of team choice, 2nd [0] gets the "true/false" value from the set
			#if team of interest is the home team'''
			#home game indicator 
			if list(set(game_details[game_details.Game_id == fullsched[j]]["HomeTeam"] == Team_Choice))[0]:
				home_game[range(len(pbp))] = 1
			#if team of interest is the road team 
			elif list(set(game_details[game_details.Game_id == fullsched[j]]["AwayTeam"] == Team_Choice))[0]:
				home_game[range(len(pbp))] = 0
	
			'''##make one PBP column
			if pbp['away'][i] is ' ':					
				home_off_poss[i] = 1
				PBP_description[i] = pbp['home'][i]
			else:
				home_off_poss[i] = 0	
				PBP_description[i] = pbp['away'][i]'''
		
			if ((home_off_poss[i] == 1) and (home_game[i] == 1)):
				my_team[i] = 1
			elif ((home_off_poss[i] == 0) and (home_game[i] == 0)):
				my_team[i] = 1
	
	#possession on fouls should be with team with the ball, not team committing the foul
	##changing home off poss for fouls needs to be changed AFTER my team is set or my team will not be with team committing foul
			'''if "foul" in PBP_description[i].lower():   #moved up
				foul[i] = 1
				if home_off_poss[i] == 1:
					home_off_poss[i] = 0
				elif home_off_poss[i] == 0:
					home_off_poss[i] = 1'''
			
			###use i-1 b/c i+1 wont be defined 
			if i < (len(pbp)-1):

				if timeout[i] == 1: 
					#if home team has next play
					if ((pbp['away'][i+1] is ' ') and home_game[i] == 1): 
						my_team[i] = 1
						#home_off_poss[i] = 1
					if ("foul" in pbp['away'][i+1].lower()) and (home_game[i] == 1):
						#home_off_poss[i] = 1
						my_team[i] = 1
					#if team is road team
					if ((pbp['home'][i+1] is ' ') and home_game[i] == 0):
						my_team[i] = 1
						##opponent (home team) fouls them after timeout 
					if ("foul" in pbp['home'][i+1].lower()) and (home_game[i] == 1):
						my_team[i] = 1

		###Find start of possessions
			if ((i > 0) and (i < (len(pbp)-1))):

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
			
			possession[0] = 1

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
			if "block" in PBP_description[i].lower():
				block[i] = 1
			if "assist" in PBP_description[i].lower():
				assist[i] = 1
			###MOVED FREE THROW			
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
			#print PBP_description[i]

		data = np.column_stack((game_id, PBP_description, my_team, possession, home_off_poss,home_game,sec_remaining, half,home_win, before_home_points,home_score, before_away_points,away_score,home_points_scored,away_points_scored, player, player2,FGA,FGM,FTA,FTAlast, FGA3,FGA3M,turnover, block, steal, assist, foul,off_reb,def_reb, timeout))
		titles = ["Game_id", "PBP_description", "my_team","possession","home_off_poss","home_game", "sec_remaining", "half", "home_win", "before_home_points","home_score","before_away_points","away_score","home_points_scored","away_points_scored","player","player2","FGA","made_FGA","FTA","FTA_RebOpp", "3FGA","3FGA_made","turnover","block", "steal","assist", "foul","off_reb","def_reb", "timeout"]
		data = pd.DataFrame(data, columns = titles)
		Team_GamePBP = Team_GamePBP.append(data)   #PBP for all games played by a particular team 
		
		print "Added " + folder_names[j] + " " + filename[j]

	merged_data = Team_GamePBP.merge(game_details, how = 'left', on = "Game_id") 

	print "Data for " + str(len(fullsched) - no_gamecounter) + " of " + str(len(fullsched)) + " games"

	return merged_data

def main():
	game_details = Readme()  #read in game details for all games by conference
	ListofTeams = TeamList(game_details)  #get list of teams for which there is PBP data
	
	print "Got Game Details"
	with pd.option_context('display.max_rows', 500, 'display.max_columns', 2):
		print ListofTeams

	ListofTeams.to_csv("ListofTeams.csv",sep = ',')

	##takes a number on list of teams th
	Num_team_choice = int(raw_input("Please select the number corresponding to the team you want: "))
	#Num_team_choice = 125
	#name of team chosen 
	Team_Choice = ListofTeams.iloc[Num_team_choice][0] 

	##get schedule for team of choice.  returns a dictionary with columns "fullsched" and "game_days"
	TeamSched = schedule(Team_Choice, game_details)
	print "Got Schedule for %s" % Team_Choice

	merged_data = pbp_stats(TeamSched["fullsched"], TeamSched["game_days"], game_details, Team_Choice)
	print "Merged Data"
	
	#print merged_data.head(10)
	filename = "../Processed-PBP/%s.csv" % Team_Choice
	#filename = "../Processed-PBP/test.csv"

	merged_data.to_csv(filename,sep = '\t')
	print "Done!"


if __name__ == '__main__':
	main()

