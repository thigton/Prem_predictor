"""Execute the main code"""
import os
import PL_machine_learning as PL
import pandas as pd
# Change working directory to the directory of this script
os.chdir(os.path.dirname(__file__)) 
data_loc = '/Users/Tom/Box/Personal/10 Other/PL_Predictions/PL_data/'
# Get file ids
fid = PL.get_fid('./PL_data','.csv')['.csv']


for f in fid:
	
	data = pd.read_csv(data_loc + f + '.csv', sep = ',', usecols=['Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR','HS','AS','HST','AST'
    ,'HF','AF','WHH','WHD','WHA'])

	# --------------------------------------------------

	# Remove NaNs in the date column and change to date format
	PL.date_clean(data)

	# Team list in the league that year
	teams = PL.team_list(data)
	
	
	# Games Played
	season_length = PL.games_played(data,teams)

	# Goalteams
	# PL.goals_scored(data, teams, season_length)
	# Goals difference
	# PL.goal_difference(data, teams, season_length)
	#data[['H_Goals Diff (Ave)', 'H_Goals For (Ave)', 'H_Goals Against (Ave)']].to_csv('test.csv')
	PL.home_away(data,teams,season_length)
	PL. team_form(data, teams, season_length, Home = False)
	exit()

	# create features
	PL.league_positions(data, teams ,season_length) # League Postions
	print(data.tail(10))
exit()


