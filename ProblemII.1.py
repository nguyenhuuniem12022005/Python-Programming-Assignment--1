import pandas as pd
import numpy as np

# Step 1: Read the data
df = pd.read_csv("results.csv")
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

# Step 2: Select only numeric columns (exclude Player, Squad, Pos, etc.)
numeric_df = df.select_dtypes(include=[np.number])

# Step 3: Create top_3.txt with top 3 highest & lowest players for each stat
top3_lines = []
for col in numeric_df.columns:
    top3_high = df.loc[numeric_df[col].nlargest(3).index, ["Player", "Squad","Nation","Position", col]]
    top3_low = df.loc[numeric_df[col].nsmallest(3).index, ["Player", "Squad","Nation","Position", col]]

    top3_lines.append(f"\n=== {col} ===\n")
    top3_lines.append("Top 3 highest:\n")
    top3_lines.extend([f"{row['Player']} (Team:{row['Squad']},Nation:{row['Nation']},Position:{row['Position']}): {row[col]}" for _, row in top3_high.iterrows()])
    top3_lines.append('\n')
    top3_lines.append("Top 3 lowest:\n")
    top3_lines.extend([f"{row['Player']} (Team:{row['Squad']},Nation:{row['Nation']},Position:{row['Position']}): {row[col]}" for _, row in top3_low.iterrows()])
    top3_lines.append('\n')

with open("top_3.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(top3_lines))
