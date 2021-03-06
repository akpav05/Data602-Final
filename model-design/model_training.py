# -*- coding: utf-8 -*-
"""
@author: Pavan Akula, Nnaemezue Obi-eyisi, Ilya Kats
"""

import sqlite3
import pandas as pd
import numpy as np
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn import tree

def getHomeWinPCT(teamID, season, matchDf):
    '''Returns home match winning percentage for previous season.'''
    if season=='2008/2009':
        return np.nan
    prevSeason = {'2009/2010':'2008/2009',
                  '2010/2011':'2009/2010',
                  '2011/2012':'2010/2011',
                  '2012/2013':'2011/2012',
                  '2013/2014':'2012/2013',
                  '2014/2015':'2013/2014',
                  '2015/2016':'2014/2015'}
    matches = len(matchDf[(matchDf.home_team_api_id==teamID) & (matchDf.season==prevSeason[season])])
    if matches==0:
        return np.nan
    wins = len(matchDf[(matchDf.home_team_api_id==teamID) & (matchDf.season==prevSeason[season]) & (matchDf.result==1)])
    return (wins/matches)*100

def getAwayWinPCT(teamID, season, matchDf):
    '''Returns away match winning percentage for previous season.'''
    if season=='2008/2009':
        return np.nan
    prevSeason = {'2009/2010':'2008/2009',
                  '2010/2011':'2009/2010',
                  '2011/2012':'2010/2011',
                  '2012/2013':'2011/2012',
                  '2013/2014':'2012/2013',
                  '2014/2015':'2013/2014',
                  '2015/2016':'2014/2015'}
    matches = len(matchDf[(matchDf.away_team_api_id==teamID) & (matchDf.season==prevSeason[season])])
    if matches==0:
        return np.nan
    wins = len(matchDf[(matchDf.away_team_api_id==teamID) & (matchDf.season==prevSeason[season]) & (matchDf.result==1)])
    return (wins/matches)*100

def getPrevResult(teamID, asOfDate, matchDf):
    ''' Returns result of previous game for a given team.'''
    homeMatches = matchDf[matchDf.home_team_api_id==teamID]
    awayMatches = matchDf[matchDf.away_team_api_id==teamID]
    allMatches = pd.concat([homeMatches, awayMatches])
    prevMatch = allMatches[allMatches.date < asOfDate].sort_values(by = 'date', ascending = False)[:1]
    if len(prevMatch)==0:
        return -99999
    else:
        return prevMatch['result'].values[0]
    
def getPlayerRanking(playerID, asOfDate, playerAttribDf):
    ''' Returns player ranking (one ID) or average of ranking (list of IDs).'''
    if type(playerID)==int:
        playerID=[playerID]
    ranking = []
    for pl in playerID:
        # Get the most recent available attributes
        playerAttribs = playerAttribDf[playerAttribDf.player_api_id==pl]
        currentAttribs = playerAttribs[playerAttribs.date <= asOfDate].sort_values(by = 'date', ascending = False)[:1]
        if len(currentAttribs)==0:
            ranking += [0]
        else:
            ranking += [currentAttribs.overall_rating.values[0]]
        return sum(ranking)/len(ranking)

def formatHomePlayers(row):
    return list(map(int, row[['home_player_2','home_player_3',
                              'home_player_4','home_player_5','home_player_6',
                              'home_player_7','home_player_8','home_player_9',
                              'home_player_10','home_player_11']].values.tolist()))
def formatAwayPlayers(row):
    return list(map(int, row[['away_player_2','away_player_3',
                              'away_player_4','away_player_5','away_player_6',
                              'away_player_7','away_player_8','away_player_9',
                              'away_player_10','away_player_11']].values.tolist()))

def getTeamName(teamID, teamDf):
    ''' Returns team's abbreviated name.'''
    return teamDf[teamDf.team_api_id==teamID].team_short_name.values[0]

def getPlayerHeight(playerID, playerDf):
    ''' Returns player height (if one ID) or average (if multiple IDs).'''
    if type(playerID)==int:
        playerID=[playerID]
    height = []
    for pl in playerID:
        height += [playerDf[playerDf.player_api_id==pl].height.values[0]]
    return sum(height)/len(height)

def getPlayerWeight(playerID, playerDf):
    ''' Returns player weight (if one ID) or average (if multiple IDs).'''
    if type(playerID)==int:
        playerID=[playerID]
    weight = []
    for pl in playerID:
        weight += [playerDf[playerDf.player_api_id==pl].weight.values[0]]
    return sum(weight)/len(weight)

def getTeamAttribute(teamID, asOfDate, attrib, teamAttribDf):
    ''' Returns team's attribute.'''
    teamAttribs = teamAttribDf[teamAttribDf.team_api_id==teamID]
    currentAttribs = teamAttribs[teamAttribs.date <= asOfDate].sort_values(by = 'date', ascending = False)[:1]
    if len(currentAttribs)==0:
        return np.nan
    else:
        return currentAttribs[attrib].values[0]

# --------------------------------------------------------------------
# READ DATA FROM DATABASE TO DATA FRAME
# --------------------------------------------------------------------
sqliteFile = "C:\\Temp\\CUNY\\data602-final\\app\\database\\database.sqlite"
conn = sqlite3.connect(sqliteFile)

# Match info
query = ("SELECT match_api_id, home_team_api_id, away_team_api_id, "+
         "       season, stage, home_team_goal, away_team_goal, date, "+
         "       home_player_1, home_player_2, home_player_3, "+
         "       home_player_4, home_player_5, home_player_6, "+
         "       home_player_7, home_player_8, home_player_9, "+
         "       home_player_10, home_player_11, "+
         "       away_player_1, away_player_2, away_player_3, "+
         "       away_player_4, away_player_5, away_player_6, "+
         "       away_player_7, away_player_8, away_player_9, "+
         "       away_player_10, away_player_11 "+
         "FROM Match;")
matchDf = pd.read_sql_query(query, conn)

# Player info
query = ("SELECT player_api_id, birthday, height, weight "+
         "FROM Player;")
playerDf = pd.read_sql_query(query, conn)

# Player attributes
query = ("SELECT player_api_id, date, overall_rating "+
         "FROM Player_Attributes;")
playerAttribDf = pd.read_sql_query(query, conn)

# Team info
query = ("SELECT team_api_id, team_short_name "+
         "FROM Team;")
teamDf = pd.read_sql_query(query, conn)

# Team attributes
query = ("SELECT team_api_id, date, "+
         "       buildUpPlaySpeed, buildUpPlayPassing, "+
         "       chanceCreationPassing, chanceCreationCrossing, "+
         "       chanceCreationShooting, "+
         "       defencePressure, defenceAggression, defenceTeamWidth "+
         "FROM Team_Attributes;")
teamAttribDf = pd.read_sql_query(query, conn)

conn.close()
del conn

# --------------------------------------------------------------------
# MODIFY DATA FOR TRAINING / GET FEATURES and LABEL
# --------------------------------------------------------------------
# Match outcome - 1-Win by home team, 2-Draw, 3-Loss by home team
matchDf.loc[matchDf.home_team_goal >  matchDf.away_team_goal, 'result'] = 1
matchDf.loc[matchDf.home_team_goal == matchDf.away_team_goal, 'result'] = 2
matchDf.loc[matchDf.home_team_goal <  matchDf.away_team_goal, 'result'] = 3

matchDf = matchDf.dropna()

# Average ranking of players
matchDf['home_ranking'] = matchDf.apply (lambda row: getPlayerRanking(formatHomePlayers(row), row['date'], playerAttribDf), axis=1)
matchDf['away_ranking'] = matchDf.apply (lambda row: getPlayerRanking(formatAwayPlayers(row), row['date'], playerAttribDf), axis=1)
# Ranking of goalies
matchDf['home_goalie_ranking'] = matchDf.apply (lambda row: getPlayerRanking(int(row['home_player_1']), row['date'], playerAttribDf), axis=1)
matchDf['away_goalie_ranking'] = matchDf.apply (lambda row: getPlayerRanking(int(row['away_player_1']), row['date'], playerAttribDf), axis=1)

# Previous match result
matchDf['home_prev'] = matchDf.apply (lambda row: getPrevResult(row['home_team_api_id'], row['date'], matchDf), axis=1)
matchDf['away_prev'] = matchDf.apply (lambda row: getPrevResult(row['away_team_api_id'], row['date'], matchDf), axis=1)

matchDf['home_win_rate'] = matchDf.apply (lambda row: getHomeWinPCT(row['home_team_api_id'], row['season'], matchDf), axis=1)
matchDf['away_win_rate'] = matchDf.apply (lambda row: getAwayWinPCT(row['away_team_api_id'], row['season'], matchDf), axis=1)

# Average height and weight of players
#matchDf['home_height'] = matchDf.apply (lambda row: getPlayerHeight(formatHomePlayers(row), playerDf), axis=1)
#matchDf['away_height'] = matchDf.apply (lambda row: getPlayerHeight(formatAwayPlayers(row), playerDf), axis=1)
#matchDf['home_weight'] = matchDf.apply (lambda row: getPlayerWeight(formatHomePlayers(row), playerDf), axis=1)
#matchDf['away_weight'] = matchDf.apply (lambda row: getPlayerWeight(formatAwayPlayers(row), playerDf), axis=1)

# Considered using team names instead of IDs
# Does not seem to be necessary    
#matchDf['home_team'] = matchDf.apply (lambda row: getTeamName(row['home_team_api_id'], teamDf), axis=1)
#matchDf['away_team'] = matchDf.apply (lambda row: getTeamName(row['away_team_api_id'], teamDf), axis=1)

# Team attributes:
# Build-up play speed and passing
matchDf['home_play_speed'] = matchDf.apply (lambda row: getTeamAttribute(row['home_team_api_id'], row['date'], 'buildUpPlaySpeed', teamAttribDf), axis=1)
matchDf['home_play_passing'] = matchDf.apply (lambda row: getTeamAttribute(row['home_team_api_id'], row['date'], 'buildUpPlayPassing', teamAttribDf), axis=1)
matchDf['away_play_speed'] = matchDf.apply (lambda row: getTeamAttribute(row['away_team_api_id'], row['date'], 'buildUpPlaySpeed', teamAttribDf), axis=1)
matchDf['away_play_passing'] = matchDf.apply (lambda row: getTeamAttribute(row['away_team_api_id'], row['date'], 'buildUpPlayPassing', teamAttribDf), axis=1)
# Chance creation - passing, crossing, shooting
matchDf['home_creation_passing'] = matchDf.apply (lambda row: getTeamAttribute(row['home_team_api_id'], row['date'], 'chanceCreationPassing', teamAttribDf), axis=1)
matchDf['home_creation_crossing'] = matchDf.apply (lambda row: getTeamAttribute(row['home_team_api_id'], row['date'], 'chanceCreationCrossing', teamAttribDf), axis=1)
matchDf['home_creation_shooting'] = matchDf.apply (lambda row: getTeamAttribute(row['home_team_api_id'], row['date'], 'chanceCreationShooting', teamAttribDf), axis=1)
matchDf['away_creation_passing'] = matchDf.apply (lambda row: getTeamAttribute(row['away_team_api_id'], row['date'], 'chanceCreationPassing', teamAttribDf), axis=1)
matchDf['away_creation_crossing'] = matchDf.apply (lambda row: getTeamAttribute(row['away_team_api_id'], row['date'], 'chanceCreationCrossing', teamAttribDf), axis=1)
matchDf['away_creation_shooting'] = matchDf.apply (lambda row: getTeamAttribute(row['away_team_api_id'], row['date'], 'chanceCreationShooting', teamAttribDf), axis=1)
# Defence - aggression and team width
matchDf['home_aggression'] = matchDf.apply (lambda row: getTeamAttribute(row['home_team_api_id'], row['date'], 'defenceAggression', teamAttribDf), axis=1)
matchDf['home_team_width'] = matchDf.apply (lambda row: getTeamAttribute(row['home_team_api_id'], row['date'], 'defenceTeamWidth', teamAttribDf), axis=1)
matchDf['away_aggression'] = matchDf.apply (lambda row: getTeamAttribute(row['away_team_api_id'], row['date'], 'defenceAggression', teamAttribDf), axis=1)
matchDf['away_team_width'] = matchDf.apply (lambda row: getTeamAttribute(row['away_team_api_id'], row['date'], 'defenceTeamWidth', teamAttribDf), axis=1)

matchDf.to_csv('matchDf.csv')
# --------------------------------------------------------------------
# SELECT FIELD FOR TRAINING
# --------------------------------------------------------------------
modelDf = matchDf[[
#                   'home_team_api_id', 'away_team_api_id', 
                   'stage', 
                   'home_ranking', 'away_ranking',
                   'home_goalie_ranking', 'away_goalie_ranking', 
                   'home_prev', 'away_prev', 
                   'home_win_rate', 'away_win_rate',
#                   'home_height', 'away_height', 
#                   'home_weight', 'away_weight', 
#                   'home_play_speed', 'away_play_speed', 
                   'home_play_passing',  'away_play_passing',  
#                   'home_creation_passing', 'home_creation_crossing', 'home_creation_shooting', 
#                   'away_creation_passing', 'away_creation_crossing', 'away_creation_shooting', 
                   'home_aggression', 'away_aggression', 
                   'home_team_width', 'away_team_width', 
                   'result']]
modelDf = modelDf.dropna()
#print(len(modelDf))

# --------------------------------------------------------------------
# MODEL TRAINING
# --------------------------------------------------------------------
X = np.array(modelDf.drop(['result'], 1))
y = np.array(modelDf['result'])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

#clf = svm.SVC()
#clf = KNeighborsClassifier(n_neighbors=5)
#clf = GaussianNB()
#clf = AdaBoostClassifier(base_estimator=tree.DecisionTreeClassifier(max_depth=1), n_estimators=1000, random_state=1)
clf = AdaBoostClassifier()
clf.fit(X_train, y_train)
accuracy = clf.score(X_test, y_test)

print(accuracy)