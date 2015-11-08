#calls TeamPBPStats repeatedly and gets stats for different teams and saves as CSV
import TeamPBPStats
import pandas as pd

def Readme():
	#game_details = pd.read_csv("All_Conf_Game_Details.csv",sep = ',')
	#ListofTeams = pd.read_csv("ListofTeams.csv",sep = ',')  #all teams 
	ListofTeams = pd.read_csv("Top100List.csv",sep = ',')  #top 100 teams	
	return ListofTeams

def main():
	ListofTeams = Readme()
	for i in range(10):  #69 = davidson, Duquesne, La Salle; richmond; skipped E Illinois, fordham, franklin pierce, fresno st
	#for i in range(280,len(ListofTeams)):
	#for i in range(0,9):
	#for i in range(0,2):
		team_choice = ListofTeams.iloc[i][0]
		TeamPBPStats.main(team_choice)

if __name__ == '__main__':
	main()
