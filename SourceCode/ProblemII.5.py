import pandas as pd
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(BASE_DIR, "best_teams_per_statistic.csv")
output_stats_path = os.path.join(BASE_DIR, "positive_stats_leaders.csv")
output_ranking_path = os.path.join(BASE_DIR, "team_rankings_by_positive_stats.csv")

# Load the CSV file
df = pd.read_csv(input_path)

# Define positive and negative metrics (convert all to lowercase)
positive_keywords = [x.lower() for x in [
    'Matches', 'Playing_Time_Starts', 'Minutes', 'Performance_Gls', 'Performance_Ast',
    'Expected_xG', 'Expected_xAG', 'Progression_PrgC', 'Progression_PrgP', 'Progression_PrgR',
    'Per_90_Minutes_Gls', 'Per_90_Minutes_Ast', 'Per_90_Minutes_xG', 'Per_90_Minutes_xAG',
    'Save_Percentage', 'CleanSheet_Percentage', 'Penalty_Save_Percentage', 'Shots_On_Target_Percentage',
    'Shots_On_Target_Per90', 'Goals_PerShot', 'Total_Passes_Completed', 'Total_Passes_Completed_Percentage',
    'Short_Passe_Completed_Percentage', 'Medium_Passes_Completed_Percentage', 'Long_Passes_Completed_Percentage',
    'Keypasses', 'Passes_Into_Final_Third', 'Passes_Into_Penalty_Area', 'Crossed_Into_Penalty_Area',
    'Progressive_Passes', 'Shot_Creating_Actions', 'Shot_Creating_Actions_Per90', 'Goal_Creating_Actions',
    'Goal_Creating_Actions_Per90', 'Tackles', 'Tackles_Won', 'Defensive_Actions_Attempted', 'Blocks',
    'Shots_Blocked', 'Passes_Blocked', 'Interceptions', 'Touches', 'Touches_Def_3rd', 'Touches_Mid_3rd',
    'Touches_Att_3rd', 'Touches_Att_Pen', 'Take_Ons_Attempted', 'Take_Ons_Success_Percentage', 'Carries',
    'Progressive_Carrying_Distance', 'Progressive_Carries', 'Carries_Into_Final_Third', 'Carries_Into_Penalty_Area',
    'Receiving', 'Progressive_Receiving', 'Fouled', 'Crosses', 'Recoveries', 'Aerial_Duels_Won', 'Aerial_Duels_Wonpct'
]]

negative_keywords = [x.lower() for x in [
    'Yellow_Cards', 'Red_Cards', 'Goals_Against_Per90', 'Defensive_Actions_Lost', 'Miscontrols',
    'Dispossessions', 'Fouls', 'Offsides', 'Aerial_Duels_Lost', 'Take_Ons_Tackled_Percentage'
]]


def is_positive_stat(stat_name):
    stat_name = str(stat_name).lower()
    return any(keyword.lower() == stat_name for keyword in positive_keywords)


def is_negative_stat(stat_name):
    stat_name = str(stat_name).lower()
    return any(keyword.lower() == stat_name for keyword in negative_keywords)


# Analyze positive stats
positive_stats = []
team_scores = {}

for stat in df['Statistic'].unique():
    stat_data = df[df['Statistic'] == stat]

    if is_positive_stat(stat):
        max_value = stat_data['Value'].max()
        best_teams = stat_data[stat_data['Value'] == max_value]['Team'].tolist()

        for team in best_teams:
            positive_stats.append({
                'Statistic': stat,
                'Best_Team': team,
                'Value': max_value
            })
            team_scores[team] = team_scores.get(team, 0) + 1

# Create detailed results DataFrame
result_df = pd.DataFrame(positive_stats)
result_df = result_df.sort_values(by=['Best_Team', 'Statistic'])

# Rank teams by total positive stats
ranked_teams = pd.DataFrame.from_dict(team_scores, orient='index', columns=['Score'])
ranked_teams = ranked_teams.sort_values(by='Score', ascending=False)

# Generate conclusions
if not ranked_teams.empty:
    top_team = ranked_teams.index[0]
    top_score = ranked_teams.iloc[0]['Score']
    dominant_stats = result_df[result_df['Best_Team'] == top_team]['Statistic'].tolist()

    # Output results
    print("=== POSITIVE STATS LEADERS ===")
    print(result_df.to_string(index=False))

    print("\n=== TEAM RANKINGS BY POSITIVE STATS ===")
    print(ranked_teams.to_string())

    print("\n=== FINAL ANALYSIS ===")
    print(f"Best-performing team: {top_team} (Leads in {top_score} positive stats)")
    print(f"Key strengths: {', '.join(dominant_stats[:5])}... (and {len(dominant_stats) - 5} more stats)")

    # Export to CSV
    result_df.to_csv(output_stats_path, index=False)
    ranked_teams.to_csv(output_ranking_path, index=True)
else:
    print("No positive stats found in the data.")
