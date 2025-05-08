import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(BASE_DIR, "final_players_with_etv.csv")
input_path_1 = os.path.join(BASE_DIR, "results.csv")
# Read data from CSV files
df_etv = pd.read_csv(input_path)  # File containing the 'etv' column
df_results = pd.read_csv(input_path_1)  # File containing the results

# Assume you have a common column 'player_id' or 'player_name' between the two files
# Replace 'Player' with your common column (if any)
df_merged = pd.merge(df_results, df_etv[['Player', 'ETV']], on='Player', how='inner')

# Save the results to a new CSV file
output_file = os.path.join(os.path.dirname(__file__), 'results_with_etv.csv')
df_merged.to_csv(output_file, index=False)

print("The 'etv' column has been added and successfully saved to 'results_with_etv.csv'.")
