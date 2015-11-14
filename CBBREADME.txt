Key Files listed in order of steps 
-cbb.py — this file scrapes espn for pbp data between two dates for a particular conference.  creates a folder by date for all games, filename is gameid.  also outputs a list of games played on that night (not nec that pbp data exists), will be referred to here as the game_details file 
	**game_details files need to be renamed to conference name (script currently does not automatically name script to conference name)
	- run script by: “python cbb.py yyyy-mm-dd yyyy-mm-dd” 
	##major conf IDs: ACC: 2; Big 10: 7; Big 12:8; SEC: 23; Pac 12:21; Big East: 4; A10: 3; Mountain West: 44; Am East: 1 

-cbbPBPStep2_GameDetails — if cbb run for multiple conferences, this file compiles the list of games for each conference into one list of games, cleans the win/loss/rank details from the pbp stats
-Step3PBP_Stats.py — gives user a list of teams for which pbp data is avail and prompts user to enter a number corresponding to team of interest and returns cleaned pbp data w/stats for specified team

#####TO DO THE ABOVE REPEATEDLY 
-TeamStats.py —calls TeamPBPStats.py and gets pbp data for a list of teams automatically 
-TeamPBPStats.py — same as step 3 except main has been altered so that the file can be called and run for multiple teams 



