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
import glob

def get_fid(rel_dir, *ext):
    """Function to get a list of file IDs to import.
    rel_imgs_dir = string - relative file path to this script
    *img_ext = string - extensions you want to list the IDs of"""
    try:
        os.chdir(os.path.dirname(__file__)) # Change working directory to the directory of this script
        os.chdir(rel_dir)
        fid = {}
        for exts in ext:
            exts = '*.' + exts.split('.')[-1] # try to ensure if the input is "".txt" or "txt" it doesn't matter
            values = []
            for file in glob.glob(exts):
                # remove the file extension
                values.append(file.split('.')[0])
                values.sort()
            fid[str(exts[1:])] = values
        return fid
    except NameError as e:
        print(e)
    except AttributeError as e:
        print(e)
    except TypeError as e:
        print(e)




"""
CREATE NEW FEATURES IN THE DATA
"""
def date_clean(df):
    '''Remove blank rows in the csv, and convert the date string to a datetime object'''

    df['Date'] = pd.to_datetime(df['Date'], dayfirst = True ,format = "%d/%m/%y", exact = False) # convert dates to datetime format
    df = df.dropna(subset=['Date'])  # Drop empty entries (Not full clean up)



def games_played(df, team_list):
    # filter df to just a list of fixtures played by a team both home and away
    
    for team in team_list:
        gamesplayed = 0 
        HG_idx = df.index[ (df.HomeTeam == team) ].tolist() # list of row idx which the team plays a home game
        AG_idx = df.index[ (df.AwayTeam == team) ].tolist() # list of row idx which the team plays a away game

        for game in sorted(sorted(HG_idx) + sorted(AG_idx)):
            if game in HG_idx:
                df.loc[game,'H_GP'] = int(gamesplayed) # if game is in home list, put the count in H_GP
                gamesplayed += 1
            else: 
                df.loc[game,'A_GP'] = int(gamesplayed) # else its an away game
                gamesplayed += 1

    return len(HG_idx + AG_idx)               



def team_week_matrix(df, team_list, season_length):
    '''Creates a matrix of teasms on rows and weeknumbers on the columns'''
    try:
        return pd.DataFrame(0,index = team_list , columns = range(season_length))
    except:
        print('Have you run weeknumbers(df) before this?')



def team_list(df):    
    '''Create a list of teams in a season'''
    return np.array(df.HomeTeam.unique()).tolist()



def reassign_matrix_to_df(df, team_list, season_length, feature_name, feature_mat):
    '''Function will create a column in the dataframe with the feature_name and assign the feature_mat
    The assumption is that there is a Home and away column for all features and that the feature_mat is in the form
    created by team_week_matrix'''
    # REASSIGN TO THE ENTRY IN THE DATA.
    df['H_' + feature_name] = pd.Series(0, index=df.index)
    df['A_' + feature_name] = pd.Series(0, index=df.index)
    for week in range(season_length):
        for team in team_list:
            df.loc[(df.H_GP == week) & (df['HomeTeam'].str.contains(team)), 'H_' + feature_name] = feature_mat.loc[team,week]
            df.loc[(df.A_GP== week) & (df['AwayTeam'].str.contains(team)), 'A_' + feature_name] = feature_mat.loc[team,week]



def team_points(df,team_list,season_length):
    '''Creates feature of how many points each team got each week in a matrix ''' 

    ##add points for away and home team : win 3 points, draw 1 point, loss 0 point
    home_points = np.select( [df['FTR']=='H', df['FTR']=='D', df['FTR']=='A'], [3,1,0] )
    away_points = np.select( [df['FTR']=='H', df['FTR']=='D', df['FTR']=='A'], [0,1,3] )

    team_points = team_week_matrix(df, team_list, season_length)
    
    # run for loop to check all teams and all weeks
    for week in range(season_length):
        for team in team_list:
            # Check for entries in the home team column
            if len( home_points[ (df.H_GP == week) & ( df['HomeTeam'].str.contains(team)) ] ) > 0:
                team_points.loc[team,week] = int( home_points[(df.H_GP == week) & (df['HomeTeam'].str.contains(team))].sum() )
                # Check for entries in the home team column
            if len( away_points[ (df.A_GP == week) & (df['AwayTeam'].str.contains(team)) ] ) > 0:
                team_points.loc[team,week] = team_points.loc[team,week] + int(away_points[(df.A_GP == week) & (df['AwayTeam'].str.contains(team))].sum() )
    return team_points


def goals(df,team_list,season_length):
    '''Creates a matrix of the the teams goals each week either for or against'''

    goals_for = team_week_matrix(df, team_list, season_length)
    goals_against = team_week_matrix(df, team_list, season_length)

    for week in range(season_length):
        for team in team_list:
            if len(df.FTHG[(df.H_GP == week) & (df['HomeTeam'].str.contains(team))]) == 1:
                goals_for.loc[team, week] = int(df.FTHG[ (df.H_GP == week) & (df['HomeTeam'].str.contains(team)) ])
                goals_against.loc[team, week] = int(df.FTAG[ (df.H_GP == week) & (df['HomeTeam'].str.contains(team)) ])

            if len(df.FTHG[(df.A_GP == week) & (df['AwayTeam'].str.contains(team))]) == 1:
                goals_for.loc[team, week] = int(df.FTAG[ (df.A_GP == week) & (df['AwayTeam'].str.contains(team)) ])
                goals_against.loc[team, week] = int(df.FTHG[ (df.A_GP == week) & (df['AwayTeam'].str.contains(team)) ])

    return (goals_for, goals_against)


def goal_difference(df,team_list, season_length):
    ''' Goals difference for each team each game and average'''

    df['H_GD'] = df['FTHG'] - df['FTAG']
    df['A_GD'] = df['FTAG'] - df['FTHG']

    goal = goals(df, team_list, season_length)
    goal_diff = (goal[0] - goal[1]).cumsum(axis=1) / np.arange(1,season_length+1, dtype = int).T
    reassign_matrix_to_df(df, team_list, season_length, 'Goals Diff (Ave)', goal_diff)


def goals_scored(df, team_list, season_length):
    '''Feature : average goals scored'''

    goal = goals(df, team_list, season_length)
    print(goal[0])
    print(type(goal))
    print(type(goal[0]))
    goals_for = goal[0].cumsum(axis=1) / np.arange(1,season_length+1, dtype = int).T
    reassign_matrix_to_df(df, team_list, season_length, 'Goals For (Ave)', goals_for)


def league_positions(df,team_list,season_length):
    ''''Create league position for each week '''

    # league_position = team_week_matrix(df, team_list, week_numbers)
    team_point = team_points(df,team_list, season_length)
    team_cumsum = team_point.cumsum(axis=1)
    # Give Legue Position, only based on points at the moment, maybe extend to include goal difference
    league_position = team_cumsum.rank(axis = 0, method = 'min',ascending = False)

    reassign_matrix_to_df(df, team_list, season_length, 'LP', league_position)



def team_form(df, team_list, week_numbers, numberofweeks = 5):
    '''Create team form for the last n weeks'''
    team_point = team_points(df,team_list, week_numbers)
    for week in week_numbers:
        for team in team_list:
            form.loc[team,week] = np.mean(team_point.loc[team,week - numberofweeks:week])
            
    
    
    

                            


