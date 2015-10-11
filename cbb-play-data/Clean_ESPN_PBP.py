import csv
import pandas as pd 
import math 
import numpy as np
import re
import os


dates = [x for x in os.listdir(".") if os.path.isdir(os.path.join(".",x))] 
for date in dates:
	games = [x for x in os.listdir(date)] 
	for game in games:
		fname = os.path.join(date,game)  #creates path by concatenating and adding / in btw
		print fname

		#pbp is a dataframe -- parse it with pip delimiter 
		df = pd.read_csv(fname, delimiter = '\t')
		game_id = np.zeros(shape = (len(df),1))
		minutes = np.zeros(shape = (len(df),1))
		seconds = np.zeros(shape = (len(df),1))
		away_score = np.zeros(shape = (len(df),1))
		home_score = np.zeros(shape = (len(df),1))
		home_poss = np.zeros(shape = (len(df),1))
		home_margin = np.zeros(shape = (len(df),1))
		home_win = np.zeros(shape = (len(df),1))
		away_points_scored = np.zeros(shape = (len(df),1))
		home_points_scored = np.zeros(shape = (len(df),1))
		turnover = np.zeros(shape = (len(df),1))
		def_reb = np.zeros(shape = (len(df),1))
		off_reb = np.zeros(shape = (len(df),1))
		steal = np.zeros(shape = (len(df),1))
		home_win = np.zeros(shape = (len(df),1))
		FGA3 = np.zeros(shape = (len(df),1))  #3 PT FGA
		FGA3M = np.zeros(shape = (len(df),1))
		FGA = np.zeros(shape = (len(df),1))
		FGM = np.zeros(shape = (len(df),1))
		half = np.zeros(shape = (len(df),1))
		foul = np.zeros(shape = (len(df),1))
		sec_remaining = np.zeros(shape = (len(df),1))
		first_name = [None] * len(df)
		last_name = [None] * len(df)
		player = [None] * len(df)

		half_index = 0
		game_index = 0
		overtime_indicator = 0
		period_counter = 2

		PBP_description = [None] * len(df)

		def stat_generator(game):
			for i in range(len(df)):
				global overtime_indicator
				global period_counter

				game_id[i] = game.split(".")[0]

				minutes[i] = df['time'][i].split(":")[0]
				seconds[i] = df['time'][i].split(":")[1]
				##seconds remaining in half
				sec_remaining[i] = 60 * int(minutes[i]) + int(seconds[i])
				home_margin[i] = home_score[i] - away_score[i]
				
				#mark if 1st/2nd half/OT 
				if sec_remaining[i] < 60:
				
					if df['score'][i].lower().startswith('end') and df['score'][i].lower().endswith('1st half'):
						half_index = i
						half[0:half_index] = '1'
			 
					#if 'end .* 2nd half' in df['score'][i].lower():
					if df['score'][i].lower().startswith('end') and df['score'][i].lower().endswith('2nd half'):
						game_index = i
						half[half_index + 1:game_index] = '2'
						overtime_indicator = 1
					#game didn't go into overtime, ie 2 halves 
					if overtime_indicator == 0 and df['score'][i].lower().startswith('end') and df['score'][i].lower().endswith('game'): 
					#overtime_indicator == 0 & ('end .* game' in df['score'][i]):
						game_index = i
						half[half_index + 1:game_index] = '2'

					if overtime_indicator == 1 and df['score'][i].lower().startswith('end'):
						period_counter = period_counter + 1
						half[game_index + 1:i] = str(period_counter)
						game_index = i
				
				##if timeout, repeat score before timeout 
				if ("timeout" in df['score'][i].lower()) | ("end" in df['score'][i].lower()):
					away_score[i] = away_score[i-1]
					home_score[i] = home_score[i-1]
				else:	
					away_score[i] = df['score'][i].split("-")[0]
					home_score[i] = df['score'][i].split("-")[1]
				if i > 1:
					away_points_scored[i] = int(away_score[i]) - int(away_score[i-1])
					home_points_scored[i] = int(home_score[i]) - int(home_score[i-1])
				if df['away'][i] is ' ':
					home_poss[i] = 1
					PBP_description[i] = df['home'][i]
				else:
					home_poss[i] = 0
					PBP_description[i] = df['away'][i]
				first_name[i] = PBP_description[i].split(' ')[0]
				last_name[i] = PBP_description[i].split(' ')[1]
				##create dummy vars for stats 
				if "turnover" in PBP_description[i].lower():
					turnover[i] = 1
				if "Defensive Rebound" in PBP_description[i].lower():
					def_reb[i] = 1
				if "Offensive Rebound" in PBP_description[i].lower():
					off_reb[i] = 1
				if "Three Point Jumper" in PBP_description[i].lower():
					FGA3[i] = 1
				if ("Three Point Jumper" in PBP_description[i].lower()) & ("made" in PBP_description[i]):
					FGA3M[i] = 1
				if ("made" in PBP_description[i].lower()) | ("missed" in PBP_description[i].lower()):
					FGA[i] = 1
				if "made" in PBP_description[i].lower():
					FGM[i] = 1
				if "foul" in PBP_description[i].lower():
					foul[i] = 1

				
				player[i] = first_name[i] + " " + last_name[i]

			data = np.column_stack((game_id, PBP_description, sec_remaining, home_score,away_score,home_points_scored,away_points_scored,home_poss, turnover, player, steal, foul,off_reb,def_reb))
			titles = ["Game_id", "PBP_description", "sec_remaining", "home_score","away_score","home_points_scored","away_points_scored","home_poss", "turnover"]

			data = pd.DataFrame(data, columns = titles)
			return data

	filename = "../Processed-PBP/%s" % game
	data = stat_generator(game)
	data.to_csv(filename, sep = '\t')

def main():
	#filename = "../Processed-PBP/{0}/".format(d.strftime("%Y-%m-%d")) + game_id + ".csv"
	filename = "../Processed-PBP/test.csv"
	data = stat_generator()
	data.to_csv(filename, sep = '\t')    #data is dataframe
	#print [x[0] for x in os.walk(".")]  ##'.' means in the current directory, ".." means previous directory
	##'.' means in the current directory, ".." means previous directory
	#checks if everything in the current folder is a directory, if so, add to the list


if __name__ == '__main__':
	#main()
	pass

