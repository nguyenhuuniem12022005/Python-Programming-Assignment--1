import pandas as pd
import numpy as np

# Read data from CSV file
df = pd.read_csv("results.csv")


# Function to convert age strings to numeric values
def convert_age(age_str):
    if pd.isna(age_str) or age_str == "N/a":
        return np.nan
    try:
        if '-' not in str(age_str):
            return float(age_str)
        years, days = map(int, str(age_str).split('-'))
        return round(years + days / 365, 2)
    except:
        return np.nan


df['Age'] = df['Age'].apply(convert_age)

# Get list of all stats columns (excluding player info columns)
stats_columns = [col for col in df.columns if col not in ['Player', 'Squad', 'Nation', 'Position', 'Age']]

# Dictionary to store results
best_teams = {}

for stat in stats_columns:
    # Convert to numeric and ignore N/a values
    numeric_series = pd.to_numeric(df[stat], errors='coerce')

    # Calculate mean value for each team
    team_stats = df.groupby('Squad').apply(lambda x: numeric_series[x.index].mean(),include_groups=False)

    # Find team with highest value (ignore NaN)
    if not team_stats.isna().all():
        best_team = team_stats.idxmax()
        best_value = team_stats.max()
        best_teams[stat] = {
            'Team': best_team,
            'Value': round(best_value, 2),
            'Statistic': stat  # Add stat name to dictionary
        }


# Convert results to DataFrame
result_df = pd.DataFrame.from_dict(best_teams, orient='index')

# Reorder columns: Statistic, Team, Value
result_df = result_df[['Statistic', 'Team', 'Value']]

# Sort results by team and statistic
result_df.sort_values(by=['Team', 'Statistic'], inplace=True)

# Save results to CSV with UTF-8 encoding
result_df.to_csv('best_teams_per_statistic.csv', index=False, encoding='utf-8-sig')
