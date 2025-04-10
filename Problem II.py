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

# Step 4: Calculate median, mean, std for the whole dataset
median_all = numeric_df.median().to_frame(name="Median").T
mean_all = numeric_df.mean().to_frame(name="Mean").T
std_all = numeric_df.std().to_frame(name="Std").T

# Add column "Team" = all to distinguish from team-level stats
summary_all = pd.concat([median_all, mean_all, std_all])
summary_all.insert(0, "Team", ["all", "all", "all"])

# Step 5: Calculate mean & std for each team
summary_by_team = (
    df.groupby("Squad")[numeric_df.columns]
    .agg(["mean", "std"])
    .stack(level=0, future_stack=True)  # Use future_stack=True to avoid future warning
    .reset_index()
    .rename(columns={"level_0": "Squad", "level_1": "Stat"})
    .pivot(index="Squad", columns="Stat", values=["mean", "std"])
)

# Rename columns: e.g., PrgC_mean, PrgC_std,...
summary_by_team.columns = [f"{stat}_{agg}" for agg, stat in summary_by_team.columns]
summary_by_team.reset_index(inplace=True)
summary_by_team.rename(columns={"Squad": "Team"}, inplace=True)

# Step 6: Combine and export to results2.csv
results2 = pd.concat([summary_all, summary_by_team], ignore_index=True)
results2.to_csv("results2.csv", index=False)
