import pandas as pd
import numpy as np

# Step 1: Read the data
df = pd.read_csv("results.csv")

# Step 2: Select only numeric columns (exclude Player, Squad, Pos, etc.)
numeric_df = df.select_dtypes(include=[np.number])

# Step 3: Create top_3.txt with top 3 highest & lowest players for each stat
top3_lines = []
for col in numeric_df.columns:
    top3_high = df.loc[numeric_df[col].nlargest(3).index, ["Player", "Squad", col]]
    top3_low = df.loc[numeric_df[col].nsmallest(3).index, ["Player", "Squad", col]]

    top3_lines.append(f"\n=== {col} ===\n")
    top3_lines.append("Top 3 highest:\n")
    top3_lines.extend([f"{row['Player']} ({row['Squad']}): {row[col]}" for _, row in top3_high.iterrows()])
    top3_lines.append("Top 3 lowest:\n")
    top3_lines.extend([f"{row['Player']} ({row['Squad']}): {row[col]}" for _, row in top3_low.iterrows()])

with open("top_3.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(top3_lines))
