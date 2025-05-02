# Read data from CSV files
df_etv = pd.read_csv('final_players_with_etv.csv')  # File containing the 'etv' column
df_results = pd.read_csv('results.csv')  # File containing the results

# Assume you have a common column 'player_id' or 'player_name' between the two files
# Replace 'Player' with your common column (if any)
df_merged = pd.merge(df_results, df_etv[['Player', 'ETV']], on='Player', how='inner')

# Save the results to a new CSV file
df_merged.to_csv('results_with_etv.csv', index=False)

print("The 'etv' column has been added and successfully saved to 'results_with_etv.csv'.")
