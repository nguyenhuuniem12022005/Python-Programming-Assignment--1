import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('results.csv')


# Define a function to convert age strings to numeric values
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


def create_stats_table(input_df):
    # First identify columns to exclude
    exclude_cols = ['Player', 'Squad', 'Nation', 'Position']

    # Convert all columns to numeric (except excluded ones), coercing errors to NaN
    numeric_df = input_df.drop(columns=exclude_cols, errors='ignore').apply(pd.to_numeric, errors='coerce')

    # Select only numeric columns
    numeric_cols = numeric_df.select_dtypes(include=[np.number]).columns.tolist()

    # Get unique teams and sort them
    all_teams = sorted(input_df['Squad'].unique().tolist())
    teams = ['All'] + all_teams

    # Create a DataFrame to store the results
    result = pd.DataFrame(columns=[' ', '  '])

    # Iterate through each team and calculate statistics
    for i, team in enumerate(teams, 1):
        if team == 'All':
            team_df = numeric_df[numeric_cols]
        else:
            team_mask = input_df['Squad'] == team
            team_df = numeric_df.loc[team_mask, numeric_cols]

        # Calculate statistics for the current team
        team_stats = {}
        for col in numeric_cols:
            # Get non-NaN values for the column
            valid_values = team_df[col].dropna()

            # Only calculate if we have at least one valid value
            if len(valid_values) > 0:
                median = round(valid_values.median(), 2)
                mean = round(valid_values.mean(), 2)
                std = round(valid_values.std(), 2) if len(valid_values) > 1 else 0
            else:
                median = mean = std = np.nan

            team_stats[f'Median of {col}'] = median
            team_stats[f'Mean of {col}'] = mean
            team_stats[f'Std of {col}'] = std

        # Add the team name and index to the statistics
        team_stats['  '] = team
        team_stats[' '] = i
        result = pd.concat([result, pd.DataFrame([team_stats])], ignore_index=True)

    # Sort the result columns
    sorted_cols = [' ', '  ']
    for col in numeric_cols:
        sorted_cols.extend([f'Median of {col}', f'Mean of {col}', f'Std of {col}'])
    result = result[sorted_cols]

    return result


# Create the statistics table
stats_table = create_stats_table(df)

# Save to CSV with UTF-8 encoding (with BOM for Excel compatibility)
stats_table.to_csv('results2.csv', index=False, encoding='utf-8-sig')
