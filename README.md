Python Programming
Assignment 1
I
Write a Python program to collect footballer player statistical data with the following 
requirements:
• Collect statistical data  for all players who have played more than 90 minutes in the 
2024-2025 English Premier League season.
• Data source: https://fbref.com/en/
• Save the result to a file named 'results.csv', where the result table has the following 
structure:
o Each column corresponds to a statistic.
o Players are sorted alphabetically by their first name. 
o Any statistic that is unavailable or inapplicable should be marked as "N/a".
•  The required statistics are:
o Nation
o Team
o Position
o Age
o Playing Time: matches played, starts, minutes
o Performance: goals, assists, yellow cards, red cards
o Expected: expected goals (xG), expedted Assist Goals (xAG)
o Progression: PrgC, PrgP, PrgR
o Per 90 minutes: Gls, Ast, xG, xGA
o Goalkeeping:
▪ Performance: goals against per 90mins (GA90), Save%, CS%
▪ Penalty Kicks: penalty kicks Save%
o Shooting:
▪ Standard: shoots on target percentage (SoT%), Shoot on Target per 90min 
(SoT/90), goals/shot (G/sh), average shoot distance (Dist)
o Passing:
▪ Total: passes completed (Cmp),Pass completion (Cmp%), progressive
passing distance (TotDist)
▪ Short: Pass completion (Cmp%),
▪ Medium: Pass completion (Cmp%),
▪ Long: Pass completion (Cmp%),
▪ Expected: key passes (KP), pass into final third (1/3), pass into penalty 
area (PPA), CrsPA, PrgP
o Goal and Shot Creation:
▪ SCA: SCA, SCA90
▪ GCA: GCA, GCA90
o Defensive Actions:
▪ Tackles: Tkl, TklW
▪ Challenges: Att, Lost
▪ Blocks: Blocks, Sh, Pass, Int
o Possession:
▪ Touches: Touches, Def Pen, Def 3rd, Mid 3rd, Att 3rd, Att Pen
▪ Take-Ons: Att, Succ%, Tkld%
▪ Carries: Carries, ProDist, ProgC, 1/3, CPA, Mis, Dis
▪ Receiving: Rec, PrgR
o Miscellaneous Stats:
▪ Performance: Fls, Fld, Off, Crs, Recov
▪ Aerial Duels: Won, Lost, Won%
o Reference: https://fbref.com/en/squads/822bd0ba/Liverpool-Stat
