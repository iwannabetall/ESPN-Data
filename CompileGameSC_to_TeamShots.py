import os
import csv
import pandas as pd 
import math 
import numpy as np
import re
''' file compiles all game shots from individual game files into files by team.'''

def get_games(conf, season):
    game_details = pd.read_csv("cbb-pbp-data-" + season + "/" + conf + "GameDetails.csv",sep = ',')
    #2014-15 season
    #game_details = pd.read_csv("cbb-play-data/" + conf + "Team_GameIDs.csv",sep = ',')
    game_ids = game_details["Game_id"]
    # dates = game_details["Date"]
    # Home_Team = game_details["HomeTeam"]
    # Away_Team = game_details["AwayTeam"]
    # #return dates, game_ids, Home_Team, Away_Team
    return game_ids

def get_missing_games(conf, season):
	 #game_details = pd.read_csv("cbb-pbp-data-15-16/" + conf + "GameDetails.csv",sep = ',')
    MissingGames = pd.read_csv("cbb-pbp-data-" + season + "/" + "MissingShotsfor" + conf + ".csv",sep = ',')
    #MissingGames = pd.read_csv("cbb-play-data/" + "MissingShotsfor" + conf + ".csv",sep = ',')
    game_ids = MissingGames["Game_id"]
    # dates = MissingGames["Date"]
    # Home_Team = MissingGames["Home_Team"]
    # Away_Team = MissingGames["Away_Team"]
    return game_ids

def Readme(conf, season):
    game_details = pd.read_csv("cbb-pbp-data-" + season + "/" + conf + "GameDetails.csv",sep = ',')
    #game_details = pd.read_csv("cbb-play-data/" + conf + "Team_GameIDs.csv",sep = ',')
    return game_details

##copied from Step3PBP_Stats
def schedule(Team_Choice, game_details, MissingGameList):
	##returns the schedule for a team of choice (name of team)
	homeschedule = list(set(game_details[game_details['HomeTeam'] == Team_Choice]["Game_id"]))
	awayschedule = list(set(game_details[game_details['AwayTeam'] == Team_Choice]["Game_id"]))
	fullsched = homeschedule + awayschedule  ##full unique list of games played listed as game_ids
	#games with def no Shot Chart info
	#missing = get_missing_games(conference) 
	#missing = missing.tolist()
	SCgames = []
	for game in fullsched:
		if game not in MissingGameList:
			SCgames.append(game)
	##get the list of dates that team played on 
	game_days = [None] * len(SCgames)
	for i in range(len(SCgames)):
		game_days[i] = list(set(game_details[game_details["Game_id"] == SCgames[i]]["Date"]))[0]
	##for every game day, find the corresponding game 
	#filename = [None] * len(SCgames)
	#folder_names = [None] * len(SCgames)
	return {"SCsched": SCgames, "game_days": game_days}

def TeamList(game_details):
##get returns list of teams for which i have data
	#get unique list of team names 
	home_teams = set(game_details["HomeTeam"])
	away_teams = set(game_details["AwayTeam"])
	TeamList = list(set(list(home_teams) + list(away_teams)))
	TeamList = sorted(TeamList)
	TeamList = pd.DataFrame(TeamList)  #unique list of team names 
	return TeamList

def TeamShots(fullsched, game_days, season):
	no_gamecounter = 0   #count number of games that don't have PBP
	filename = [None] * len(fullsched)
	folder_names = [None] * len(fullsched)
	Shots = pd.DataFrame()
	for j in range(len(fullsched)):
		#folder_names[j] = os.path.join("cbb-play-data",game_days[j])  #path for the 14-15 folder
		folder_names[j] = os.path.join("cbb-pbp-data-" + season,game_days[j])  #path for the folder
		#filename[j] = "%s/" + "SC_" + "%s.csv" % (folder_names[j], fullsched[j])  #path of file
		filename[j] = "{0}/".format(folder_names[j]) + "SC_" + "{0}.csv".format(fullsched[j])  #path of file
		#"./2015-02-21/400591202.csv"
		#print "starting game " + str(j) + " " + folder_names[j] + " " + filename[j]
		if not os.path.isfile(filename[j]):
			no_gamecounter = no_gamecounter + 1
			continue  #PBP does not exist for all games, skip to next game
		gameshots = pd.read_csv(filename[j],delimiter = '\t', skiprows = 1, header = None)
		gameshots.columns = ["Game_id","player","pd", "homeaway", "team","distance","angle", "leftside", "left","top", "description", "playerid","shotnum","made", "FGA3", "assisted","jumper", "layup", "dunk"]
		Shots = Shots.append(gameshots)
	return Shots

def main():
	#conference = str(raw_input("Pick a conference: ACC, Big10, SEC, A10, PAC12, Big12, BigEast. "))
	season = str(raw_input("Pick a season: 13-14, 14-15, 15-16 "))
	conferences = ["ACC", "Big10", "SEC", "A10", "PAC12", "Big12", "BigEast"]
	#conferences = ["ACC", "Big10", "SEC", "PAC12", "Big12", "BigEast"]
	Teams = pd.DataFrame()
	AllGamesDeets = pd.DataFrame()
	MissingGameList = pd.DataFrame()
	for i in range(len(conferences)):
		MissingGameList = MissingGameList.append(list(get_missing_games(conferences[i], season)))
		game_details = Readme(conferences[i], season)  #read in game details for all games by conference
		ListofTeams = TeamList(game_details)  #get list of teams for which there is PBP data
		AllGamesDeets = AllGamesDeets.append(game_details)  ##all game details 
		Teams = Teams.append(ListofTeams)
		ListofTeams = list(set(Teams[0]))  #unique list of teams 

#	with pd.option_context('display.max_rows', 500, 'display.max_columns', 2):
#		print ListofTeams
	#ListofTeams.to_csv("ListofTeams.csv",sep = ',')
	##takes a number on list of teams th
#	Num_team_choice = int(raw_input("Please select the number corresponding to the team you want: "))
	#Num_team_choice = 125
	#name of team chosen 
	#Team_Choice = ListofTeams.iloc[Num_team_choice][0] 

	##get schedule for team of choice.  returns a dictionary with columns "SCsched" and "game_days"
	for i in range(len(ListofTeams)):
		TeamSched = schedule(ListofTeams[i], AllGamesDeets, MissingGameList)
		Shots = TeamShots(TeamSched["SCsched"], TeamSched["game_days"], season)
		#teamshotfile = "Shots 2014-15/" + Team_Choice + ".csv"
		teamshotfile = "Shots 20" + season + "/" + ListofTeams[i] + ".csv"
		print "Got Shots for " + ListofTeams[i]
		Shots.to_csv(teamshotfile,sep = '\t', index = False)

	os.system('say "DunDunDun Donnne"')
	os.system('afplay /System/Library/Sounds/Sosumi.aiff')



if __name__ == '__main__':
	main()