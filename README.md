# Prem_predictor
## Aim
Aim of the project is to beat the bookies, come up with a betting strategy using insights to make some money.

### Initial data exporation
Not actually done any...to get a feel for it.
## Structure
Functions are sitting in PL_machine_learning.py which are then called from Execute.py
## Current state of affairs:
A bit of a mess...
I have only done preprocessing so far, getting league posotions, running goal differences, goals per game etc.  Currently halfway through adding a feature so you can get all these features for both home and away, just home or just away.
### But...
My computer at uni doesn't want to load the CSV files so can't work on it.  So thought I would focus on starting the horses code instead...But this code is hear if you want to have a play.  I started it when I was just learning the basics of Python, so it is unlikely the best approach / most efficient way to do what Im trying to do.  If there are easier ways please improve!

## Future plans
 ### Get more data, no reason to limit it just to the Premier League - We use the league as a qualative feature in the analysis.
### List of features to add/create:
#### must haves:
- League Position - scaled on mean position and std
- Goals for - scaled on mean and std (both as a recent form thing, i.e. last 5 games and historic (entire season) or more than a single season?
- Goals difference - scaled on mean and std (both as a recent form thing, i.e. last 5 games and historic (entire season) or more than a single season?
- Days since last game - overall/since last home/since last away
- Team Form - overall/home/away
- Corners - scaled on mean and std (both as a recent form thing, i.e. last 5 games and historic (entire season) or more than a single season?
- Previous season league positions
### Model options?
- Neural nets
- SVM
### Link to Betfair API
