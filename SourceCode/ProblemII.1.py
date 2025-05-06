import pandas as pd
import numpy as np

# Read the data from CSV file
df = pd.read_csv("results.csv")


# Function to convert age string to numerical value
def convert_age(age_str):
    # Return NaN if the value is missing or 'N/a'
    if pd.isna(age_str) or age_str == "N/a":
        return np.nan
    try:
        # Handle cases where age isn't in year-day format
        if '-' not in str(age_str):
            return float(age_str)
        # Split into years and days, then convert to decimal years
        years, days = map(int, str(age_str).split('-'))
        return round(years + days / 365, 2)
    except:
        # Return NaN if conversion fails
        return np.nan


# Apply age conversion to the Age column
df['Age'] = df['Age'].apply(convert_age)

# Initialize list to store output lines
top3_lines = []

# Process each column in the dataframe
for col in df.columns:
    # Skip non-numeric columns (player info columns)
    if col in ["Player", "Squad", "Nation", "Position"]:
        continue

    # Convert column to numeric, coercing errors (like 'N/a') to NaN
    numeric_series = pd.to_numeric(df[col], errors='coerce')

    # Get top 3 highest values (ignores NaN automatically)
    top3_high = df.loc[numeric_series.nlargest(3).index, ["Player", "Squad", "Nation", "Position", col]]

    # Get top 3 lowest values (ignores NaN automatically)
    top3_low = df.loc[numeric_series.nsmallest(3).index, ["Player", "Squad", "Nation", "Position", col]]

    # Add section header for current statistic
    top3_lines.append(f"\n=== {col} ===\n")

    # Add top 3 highest players
    top3_lines.append("Top 3 highest statistics:\n")
    for _, row in top3_high.iterrows():
        top3_lines.append(
            f"{row['Player']} (Team:{row['Squad']}, Nation:{row['Nation']}, Position:{row['Position']}): {row[col]}\n")

    # Add top 3 lowest players
    top3_lines.append("\nTop 3 lowest statistics:\n")
    for _, row in top3_low.iterrows():
        top3_lines.append(
            f"{row['Player']} (Team:{row['Squad']}, Nation:{row['Nation']}, Position:{row['Position']}): {row[col]}\n")

    # Add extra spacing between statistics
    top3_lines.append('\n')
    top3_lines.append('\n')

# Write results to file using UTF-8 encoding (supports special characters)
with open("top_3.txt", "w", encoding="utf-8") as f:
    f.writelines(top3_lines)
