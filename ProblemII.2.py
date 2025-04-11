import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('results.csv')


# Define a function to convert age strings to numeric values
# The function will handle cases like 'N/a' and '0-0' as NaN
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


# Define a function to convert height strings to numeric values
def create_stats_table(input_df):
    # Choose numeric columns
    numeric_cols = input_df.select_dtypes(include=[np.number]).columns.tolist()

    # sort 
    all_teams = sorted(input_df['Squad'].unique().tolist())
    teams = ['All'] + all_teams


    # Create a DataFrame to store the results
    result = pd.DataFrame(columns=['  ', ' '])

    # Iterate through each team and calculate statistics
    for i, team in enumerate(teams, 1):
        if team == 'All':
            team_df = input_df[numeric_cols]
        else:
            team_df = input_df[input_df['Squad'] == team][numeric_cols]

        # Calculate statistics for the current team
        team_stats = {}
        for col in numeric_cols:
            median = round(team_df[col].median(), 2)
            mean = round(team_df[col].mean(), 2)
            std = round(team_df[col].std(), 2) if len(team_df) > 1 else 0

            team_stats[f'Median of {col}'] = median
            team_stats[f'Mean of {col}'] = mean
            team_stats[f'Std of {col}'] = std

        # Add the team name and index to the statistics
        team_stats[' '] = team
        team_stats['  '] = i
        result = pd.concat([result, pd.DataFrame([team_stats])], ignore_index=True)

    # Sort the result DataFrame by the first column (index 0)
    sorted_cols = ['  ', ' ']
    for col in numeric_cols:
        sorted_cols.extend([f'Median of {col}', f'Mean of {col}', f'Std of {col}'])
    result = result[sorted_cols]

    return result


#  
stats_table = create_stats_table(df)
stats_table.to_csv('results2.csv', index=False, encoding='utf-8-sig')
