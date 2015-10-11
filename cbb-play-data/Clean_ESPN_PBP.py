import pandas as pd 
import math 
import numpy as np

#pbp is a dataframe -- parse it with pip delimiter 
df = pd.read_csv("400586117.csv", delimiter = '|')

minutes = np.zeros(shape = (len(df),1))
seconds = np.zeros(shape = (len(df),1))
away_score = np.zeros(shape = (len(df),1))
home_score = np.zeros(shape = (len(df),1))
home_poss = np.zeros(shape = (len(df),1))
home_margin = home_score - away_score
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
half_index = 0
game_index = 0
'''Turnover
Defensive Rebound
Jumper
Free Throw
Layup
Dunk'''

PBP_description = [None] * len(df)

for i in range(len(df)):
	minutes[i] = df['time'][i].split(":")[0]
	seconds[i] = df['time'][i].split(":")[1]
	if 'End of 1st half' in df['score'][i]:
		half_index = i
	if 'End of Game' in df['score'][i]:
		game_index = i
	##HANDLE OVERTIME 
	half[0:half_index] = 1 
	half[half_index+1:game_index] = 2

	if i > 1:
		away_points_scored[i] = away_score[i] - away_score[i-1]
		home_points_scored[i] = home_score[i] - home_score[i-1]
	if ("timeout" in df['score'][i].lower()) | ("end" in df['score'][i].lower()):
		away_score[i] = away_score[i-1]
		home_score[i] = home_score[i-1]
	else:	
		away_score[i] = df['score'][i].split("-")[0]
		home_score[i] = df['score'][i].split("-")[1]
	if df['away'][i] is ' ':
		home_poss[i] = 1
		PBP_description[i] = df['home'][i]
	else:
		home_poss[i] = 0
		PBP_description[i] = df['away'][i]
	first_name = PBP_description[i].split(' ')[0]
	last_name = PBP_description[i].split(' ')[1]
	##create dummy vars for stats 
	if "turnover" in PBP_description[i].lower():
		turnover[i] = 1
	if "Defensive Rebound" in PBP_description[i].lower():
		def_reb[i] = 1
	if "Offensive Rebound" in PBP_description[i].lower():
		off_reb[i] = 1
	if "Three Point Jumper" in PBP_description[i].lower():
		FGA3[i] = 1
	if ("made" in PBP_description[i].lower()) | ("missed" in PBP_description[i].lower()):
		FGA[i] = 1
	if "made" in PBP_description[i].lower()
		FGM[i] = 1
	if "foul" in PBP_description[i].lower()
		foul[i] = 1

	#if "Three Point Jumper"




