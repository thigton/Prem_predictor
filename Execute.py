"""Execute the main code"""
import os
import PL_machine_learning as PL
import pandas as pd
# Change working directory to the directory of this script
os.chdir(os.path.dirname(__file__)) 
data_loc = '/Users/Tom/Box/Personal/10 Other/PL_Predictions/PL_data/'
# Get file ids
fid = PL.get_fid('./PL_data','.csv')['.csv']

print(fid)
data = pd.read_csv(data_loc + fid[0] + '.csv', sep = ',', usecols=['Date','HomeTeam','AwayTeam','FTHG','FTAG','FTR','HS','AS','HST','AST'
    ,'HF','AF','WHH','WHD','WHA'])
print(data.head())
PL.preprocess(data)
print(type(data['Date'][0]))
PL.weeknumbers(data)