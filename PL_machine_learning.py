#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 17:48:59 2018

@author: Tom Higton

Machine Learning - Premier League Fixtures

Data has been downloaded for Premier leagure results
Requires some pre-processing to create some useful features
"""


""" 
IMPORT DATA
"""
import pandas as pd
import numpy as np
import os

def filecount(dir_name): 
    x = os.listdir(dir_name)
    return len(x) 

X = filecount('/Users/Tom/Desktop/PL_Predictions/PL_data/')

# Make sure you go to the right folder
os.chdir('/Users/Tom/Desktop/PL_Predictions')
data_by_season = []
for i in range(0, X-1):
   s = 'PL_data/E0 ({})'.format(i) 
   data = pd.read_csv(s+'.csv', sep = ',', usecols=['Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR','HS','AS','HST','AST'
   ,'HF','AF','WHH','WHD','WHA'])
   data_by_season.append(data)




"""
CREATE NEW FEATURES IN THE DATA
"""
def make_data(df):
    for year in range(0,X-1):
        df[year] = df[year].dropna(subset=['Date']) 
       # df[year] = df[year].dropna()  ## NEED TO ONLY DELETE ROWS WHICH ARE MISSING KEY STATS 
        print('Looking at dataframe ' + str(year))
        
        # CONVERT DATE TO DATETIME
        #df[year]['Date'] = pd.to_datetime(df[year]['Date'], format='%d/%m/%Y')
        df[year]['Date'] = pd.to_datetime(df[year]['Date'], infer_datetime_format=True, dayfirst=True)
        # CREATE WEEK NUMBERS AND SUBTRACT STARTING WEEK.  ASSUME THE STARTING WEEK IS AFTER CALANDER WEEK 29
        df[year]['Week_Number'] = df[year]['Date'].dt.week
        df[year]['Week_Number'] = df[year]['Week_Number'] - df[year][df[year].Week_Number > 29]['Week_Number'].min() + 1
        # THOSE WEEKS YOU HAVE MADE NEGATIVE ADD 52.
        df[year]['Week_Number'] = df[year]['Week_Number'].where(df[year]['Week_Number'] > 0 , df[year]['Week_Number']+52)                   
        
        
        ##add points for away and home team : win 3 points, draw 1 point, loss 0 point
        df[year]['HP']=np.select([df[year]['FTR']=='H',df[year]['FTR']=='D',df[year]['FTR']=='A'],[3,1,0])
        df[year]['AP']=np.select([df[year]['FTR']=='H',df[year]['FTR']=='D',df[year]['FTR']=='A'],[0,1,3])
        ## add difference in goals for home and away team
        df[year]['HGD']=df[year]['FTHG']-df[year]['FTAG']
        df[year]['AGD']=-df[year]['FTHG']+df[year]['FTAG']
       
        print('Creating league positions')
        
        #CREATE RUNNING LEAGUE TABLE FIND NAMES OF TEAMS IN THE LEAGUE
        team_list = np.array(df[year].HomeTeam.unique()).tolist()
        team_points = pd.DataFrame(0,index = np.array(df[year].HomeTeam.unique()).tolist() , columns = df[year].Week_Number.unique())
        team_cumsum = pd.DataFrame(0,index = np.array(df[year].HomeTeam.unique()).tolist() , columns = df[year].Week_Number.unique())
        league_position = pd.DataFrame(0,index = np.array(df[year].HomeTeam.unique()).tolist() , columns = df[year].Week_Number.unique())
        team_goal_difference = pd.DataFrame(0,index = np.array(df[year].HomeTeam.unique()).tolist() , columns = df[year].Week_Number.unique())
        team_goal_difference_cumsum = pd.DataFrame(0,index = np.array(df[year].HomeTeam.unique()).tolist() , columns = df[year].Week_Number.unique())
        form = pd.DataFrame(0,index = np.array(df[year].HomeTeam.unique()).tolist() , columns = df[year].Week_Number.unique())
        # FOR EACH WEEK ASSIGN POINTS TO TEAMS 
        for week in df[year].Week_Number.unique():
            for team in team_list:
                # IF THERE ARE ENTRIES IN HOME TEAM SUM THE POINTS IN HP AND PUT IN TEAM POINTS
                if len(df[year].HP[(df[year].Week_Number == week) & (df[year]['HomeTeam'].str.contains(team))]) > 0:
                    team_points.loc[team,week] = int(df[year].HP[(df[year].Week_Number == week) & (df[year]['HomeTeam'].str.contains(team))].sum())
                    team_goal_difference.loc[team,week] = int(df[year].HGD[(df[year].Week_Number == week) & (df[year]['HomeTeam'].str.contains(team))].sum())

                    # IF THERE ARE ENTRIES IN AWAY TEAM SUM THE POINTS IN AP AND PUT IN TEAM POINTS
                if len(df[year].AP[(df[year].Week_Number == week) & (df[year]['AwayTeam'].str.contains(team))]) > 0:
                    team_points.loc[team,week] = team_points.loc[team,week] + int(df[year].AP[(df[year].Week_Number == week) & (df[year]['AwayTeam'].str.contains(team))].sum())
                    team_goal_difference.loc[team,week] = int(df[year].AGD[(df[year].Week_Number == week) & (df[year]['AwayTeam'].str.contains(team))].sum())
                form.loc[team,week] = np.mean(team_points.loc[team,week-5:week])
        # CREATE CUMULATIVE TOTAL
        team_cumsum = team_points.cumsum(axis=1)
        team_goal_difference_cumsum = team_goal_difference.cumsum(axis=1)
        
        # GIVE LEAGUE POSITION
        league_position = team_cumsum.rank(axis = 0, method = 'min',ascending = False)
        
        print('Putting back into Dataframe ' + str(year))
        # REASSIGN TO THE ENTRY IN THE DATA.
        df[year]['H_LP'] = pd.Series(0, index=df[year].index)
        df[year]['A_LP'] = pd.Series(0, index=df[year].index)
        df[year]['H_Form'] = pd.Series(0, index=df[year].index)
        df[year]['A_Form'] = pd.Series(0, index=df[year].index)
        for week in df[year].Week_Number.unique():
            for team in team_list:
                df[year].loc[(df[year].Week_Number == week) & (df[year]['HomeTeam'].str.contains(team)), 'H_LP'] = league_position.loc[team,week]
                df[year].loc[(df[year].Week_Number == week) & (df[year]['AwayTeam'].str.contains(team)), 'A_LP'] = league_position.loc[team,week]
                df[year].loc[(df[year].Week_Number == week) & (df[year]['HomeTeam'].str.contains(team)), 'HGD'] = team_goal_difference_cumsum.loc[team,week]
                df[year].loc[(df[year].Week_Number == week) & (df[year]['AwayTeam'].str.contains(team)), 'AGD'] = team_goal_difference_cumsum.loc[team,week]
                df[year].loc[(df[year].Week_Number == week) & (df[year]['HomeTeam'].str.contains(team)), 'H_Form'] = form.loc[team,week]
                df[year].loc[(df[year].Week_Number == week) & (df[year]['AwayTeam'].str.contains(team)), 'A_Form'] = form.loc[team,week]
                                
make_data(data_by_season)
'''      
        
for week in test.Week_Number.unique():
    for team in team_list:
        test.loc[(test.Week_Number == week) & (test['HomeTeam'].str.contains(team)),'H_LP'] = league_position.loc[team,week]
        test.loc[(test.Week_Number == week) & (test['AwayTeam'].str.contains(team)),'A_LP'] = league_position.loc[team,week]
        
   
for year in range(0,X-1):
    NNvalues =     
'''
#        # TEAMS ARE UNIQUE TO THAT SEASON
#        teams_list = np.array(df[year_data].HomeTeam.unique()).tolist()
#        for team in range(len(teams_list)):  
#            
#            
#            # WILL FIND ALL OF A TEAMS HOME AND AWAY GAMES AND SORT BY DATE
#            HomeFixtures = df[year_data][df[year_data]['HomeTeam'] == teams_list[team]]
#            # Append away games
#            Fixtures = HomeFixtures.append(df[year_data][df[year_data]['AwayTeam'] == teams_list[team]])
#            # Convert date to datetime object
#            Fixtures['Date'] = pd.to_datetime(Fixtures['Date'], format='%d/%m/%y')
#            # Sorted into Date order
#            Fixtures = Fixtures.sort_values(by=['Date'])
#            
#            # Go though and create a cumulative points score
#            Fixtures['Points'] = 0
#            if teams_list[team] in Fixtures['HomeTeam']:
#                Fixtures['Points'] = Fixtures['Points'].tail(1) + Fixtures['HP']
#            else:
#                Fixtures['Points'] = Fixtures['Points'].tail(1) + Fixtures['AP']
                    

    


'''
TESTING AREA FOR LINES TO PUT INTO FUNCTION
'''

'''

for week in range(1, test.Week_Number.max()):
    test.loc[test.Week_Number == week]
    for team in team_list:
        # IF THERE ARE ENTRIES IN HOME TEAM SUM THE POINTS IN HP AND PUT IN TEAM POINTS
        if len(test.HP[(test.Week_Number == week) & (test['HomeTeam'].str.contains(team))]) >0:
            team_points.loc[team,week] = int(test.HP[(test.Week_Number == week) & (test['HomeTeam'].str.contains(team))].sum())
         # IF THERE ARE ENTRIES IN AWAY TEAM SUM THE POINTS IN AP AND PUT IN TEAM POINTS
        if len(test.AP[(test.Week_Number == week) & (test['AwayTeam'].str.contains(team))]) > 0:
            team_points.loc[team,week] = team_points.loc[team,week] + int(test.AP[(test.Week_Number == week) & (test['AwayTeam'].str.contains(team))].sum())


team_points = pd.DataFrame(0,index = np.array(test.HomeTeam.unique()).tolist() , columns = test.Week_Number.unique())
team_cumsum = pd.DataFrame(0,index = np.array(test.HomeTeam.unique()).tolist() , columns = test.Week_Number.unique())
league_position = pd.DataFrame(0,index = np.array(test.HomeTeam.unique()).tolist() , columns = test.Week_Number.unique())

HomeFixtures = data_by_season[0][data_by_season[0]['HomeTeam'] == teams_list[1]]
Fixtures = HomeFixtures.append(data_by_season[0][data_by_season[0]['AwayTeam'] == teams_list[1]])

test['Date'] = pd.to_datetime(test['Date'], format='%d/%m/%y')
test['Week_Number'] = test['Date'].dt.week - test[test.Week_Number > 29]['Week_Number'].min() + 1

df[year][df[year].Week_Number < 0] = df[year]['Week_Number'] + 52
test[test.Week_Number <= 0] = test['Week_Number'] + 52

Fixtures['Points'] = 0
for index, row in Fixtures.iterrows():
    if teams_list[1] in Fixtures['HomeTeam']:
        Fixtures['Points'] = np.select(Fixtures['Points'].tail(1) + Fixtures['HP'])
    else:
        Fixtures['Points'] = np.select(Fixtures['Points'].tail(1) + Fixtures['AP'])

test[test.Week_Number > 29]['Week_Number'].min()
N = Y['Week_Number'].min

df['Date'].dt.week
# COLLECT FULLY PREPROCESSED DATA INTO ONE FRAME
full_df = pd.concat(data_by_season)

MIN = data_by_season[0][data_by_season[0].Week_Number > 29]['Week_Number'].min()
'''