import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from io import StringIO
import time

# Dictionary of URLs and their identifiers
links = {
    "https://fbref.com/en/comps/9/stats/Premier-League-Stats": "stats_standard",
    "https://fbref.com/en/comps/9/keepers/Premier-League-Stats": "stats_keeper",
    "https://fbref.com/en/comps/9/shooting/Premier-League-Stats": "stats_shooting",
    "https://fbref.com/en/comps/9/passing/Premier-League-Stats": "stats_passing",
    "https://fbref.com/en/comps/9/gca/Premier-League-Stats": "stats_gca",
    "https://fbref.com/en/comps/9/defense/Premier-League-Stats": "stats_defense",
    "https://fbref.com/en/comps/9/possession/Premier-League-Stats": "stats_possession",
    "https://fbref.com/en/comps/9/misc/Premier-League-Stats": "stats_misc"
}

# Set up Selenium options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Initialize the WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)


def scrape_table_with_selenium(url, table_id):
    try:
        print(f"Scraping {url}...")
        driver.get(url)
        time.sleep(5)  # Increased wait time

        # Wait for table to load
        table = driver.find_element(By.ID, table_id)
        html = table.get_attribute('outerHTML')

        # Use StringIO to avoid the FutureWarning
        df = pd.read_html(StringIO(html))[0]

        # Clean multi-index columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(col).strip() for col in df.columns.values]

        # Standardize column names
        df.columns = df.columns.str.replace(r'%', 'pct', regex=True)
        df.columns = df.columns.str.replace(r'[^a-zA-Z0-9_]', '_', regex=True)

        return df

    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None


# Initialize the main DataFrame with the standard stats
main_df = scrape_table_with_selenium(
    "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
    "stats_standard"
)

if main_df is None:
    raise Exception("Failed to scrape the initial standard stats table")

# Check for player column (might be 'Player' or 'player')
player_col = next((col for col in main_df.columns if 'player' in col.lower()), None)
if not player_col:
    raise Exception("Could not find player column in the data")

# Rename player column to standard 'Player'
main_df = main_df.rename(columns={player_col: 'Player'})

# Clean player names
main_df['Player'] = main_df['Player'].str.replace(r'^\d+\s*', '', regex=True).str.strip()

# Find minutes column (might be 'Min', 'Minutes', etc.)
minutes_col = next((col for col in main_df.columns if 'min' in col.lower()), None)
if minutes_col:
    # Convert minutes to numeric, coerce errors
    main_df[minutes_col] = pd.to_numeric(main_df[minutes_col], errors='coerce')
    main_df = main_df[main_df[minutes_col] > 90]
    # Rename to standard 'Minutes'
    main_df = main_df.rename(columns={minutes_col: 'Minutes'})
else:
    print("Warning: Could not find minutes column, skipping minutes filter")

# Find squad column (might be 'Squad', 'Team', etc.)
squad_col = next((col for col in main_df.columns if 'squad' in col.lower() or 'team' in col.lower()), None)
if squad_col and squad_col != 'Squad':
    main_df = main_df.rename(columns={squad_col: 'Squad'})

# Iterate through other links and merge them
for url, table_id in links.items():
    if table_id == "stats_standard":  # We already have this
        continue

    try:
        df = scrape_table_with_selenium(url, table_id)
        if df is None:
            continue

        # Find and standardize player column
        player_col = next((col for col in df.columns if 'player' in col.lower()), None)
        if not player_col:
            print(f"Skipping {table_id} - no player column found")
            continue

        df = df.rename(columns={player_col: 'Player'})
        df['Player'] = df['Player'].str.replace(r'^\d+\s*', '', regex=True).str.strip()

        # Find and standardize squad column if available
        squad_col = next((col for col in df.columns if 'squad' in col.lower() or 'team' in col.lower()), None)
        merge_cols = ['Player']
        if squad_col:
            df = df.rename(columns={squad_col: 'Squad'})
            merge_cols.append('Squad')

        # Merge with main DataFrame
        main_df = pd.merge(
            main_df,
            df,
            on=merge_cols,
            how='left',
            suffixes=('', '_drop')
        )

        # Drop duplicate columns
        main_df = main_df.loc[:, ~main_df.columns.str.endswith('_drop')]

    except Exception as e:
        print(f"Error processing {table_id}: {str(e)}")
        continue
    

# Close the browser
driver.quit()

# Final cleaning and sorting
main_df = main_df.sort_values('Player').reset_index(drop=True)

# Remove duplicate columns
main_df = main_df.loc[:, ~main_df.columns.duplicated()]

# Define the columns to keep based on the provided list
columns_to_keep = [
    # Player Information
    'Player', 'Unnamed_2_level_0_Nation', 'Squad', 'Unnamed_3_level_0_Pos', 'Unnamed_5_level_0_Age',
    
    # Playing Time
    'Playing_Time_MP', 'Playing_Time_Starts', 'Minutes',
    
    # Performance
    'Performance_Gls','Performance_Ast', 'Performance_CrdY','Performance_CrdR',
    
    # Expected
    'Expected_xG','Expected_xAG',
    
    # Progression
   'Progression_PrgC','Progression_PrgP','Progression_PrgR',
    
    # Per 90
    'Per_90_Minutes_Gls','Per_90_Minutes_Ast', 'Per_90_Minutes_xG','Per_90_Minutes_xAG',
    
    # Goalkeeping
   'Performance_GA90', 'Performance_Savepct', 'Performance_CSpct', 'Penalty_Kicks_Savepct',
    
    # Shooting
    'Standard_SoTpct', 'Standard_SoT_90', 'Standard_G_Sh', 'Standard_Dist',
    
    # Passing
    'Total_Cmp','Total_Cmppct','Total_TotDist', 'Short_Cmppct', 'Medium_Cmppct', 'Long_Cmppct',
    'Unnamed_26_level_0_KP','Unnamed_27_level_0_1_3','Unnamed_28_level_0_PPA', 'Unnamed_29_level_0_CrsPA', 'Unnamed_30_level_0_PrgP',
    
    # Goal and Shot Creation
    'SCA_SCA','SCA_SCA90','GCA_GCA','GCA_GCA90',
    
    # Defensive Actions
    'Tackles_Tkl', 'Tackles_TklW', 'Challenges_Att', 'Challenges_Lost',
    'Blocks_Blocks', 'Blocks_Sh', 'Blocks_Pass', 'Unnamed_20_level_0_Int',
    
    # Possession
    'Touches_Touches', 'Touches_Def_Pen', 'Touches_Def_3rd', 'Touches_Mid_3rd', 'Touches_Att_3rd', 'Touches_Att_Pen',
    'Take_Ons_Att', 'Take_Ons_Succpct', 'Take_Ons_Tkldpct',
    'Carries_Carries', 'Carries_TotDist', 'Carries_PrgDist', 'Carries_PrgC', 'Carries_1_3', 'Carries_CPA', 'Carries_Mis', 'Carries_Dis',
    'Receiving_Rec', 'Receiving_PrgR',
    
    # Miscellaneous
    'Performance_Fls', 'Performance_Fld', 'Performance_Off', 'Performance_Crs', 'Performance_Recov',
    'Aerial_Duels_Won', 'Aerial_Duels_Lost', 'Aerial_Duels_Wonpct'
]

# Standardize column names to avoid issues with special characters
def standardize_column_names(df):
    df.columns = df.columns.str.replace(r'%', 'pct', regex=True)
    df.columns = df.columns.str.replace(r'[^a-zA-Z0-9_]', '_', regex=True)
    df.columns = df.columns.str.replace(r'_+', '_', regex=True)
    df.columns = df.columns.str.strip('_')
    return df

# Standardize column names in the main DataFrame
main_df = standardize_column_names(main_df)

# Find available columns in the main DataFrame
available_columns = [col for col in columns_to_keep if col in main_df.columns]

# Filter to keep only the necessary columns
filtered_df = main_df[available_columns]

# Rearrange the column order according to the given list
ordered_columns = []
for col in columns_to_keep:
    if col in filtered_df.columns:
        ordered_columns.append(col)

filtered_df = filtered_df[ordered_columns]

# Rename columns to more user-friendly names
column_rename_map = {
    'Playing_Time_MP': 'Matches',
    'Unnamed_3_level_0_Pos': 'Position',
    'Unnamed_5_level_0_Age':'Age',
    'Unnamed_2_level_0_Nation':'Nation',
    'Performance_CrdY' : 'Yellow_Cards',
    'Performance_CrdR': 'Red_Cards',
    'Unnamed_26_level_0_KP':'Keypasses',
    'Unnamed_27_level_0_1_3':'Passes_Into_Final_Third',
    'Unnamed_28_level_0_PPA':'Passes_Into_Penalty_Area',
    'Unnamed_29_level_0_CrsPA':'Crossed_Into_Penalty_Area',
    'Unnamed_30_level_0_PrgP':'Progressive_Passes',
    'Unnamed_20_level_0_Int':'Interceptions',
    'Performance_GA90':'Goals_Against_Per90',
    'Performance_Savepct':'Save_Percentage',
    'Performance_CSpct':'CleanSheet_Percentage',
    'Penalty_Kicks_Savepct':'Penalty_Save_Percentage',
    'Standard_SoTpct':'Shots_On_Target_Percentage',
    'Standard_SoT_90':'Shots_On_Target_Per90',
    'Standard_G_Sh':'Goals_PerShot',
    'Standard_Dist':'Shooting_Distance',
    'Total_Cmp':'Total_Passes_Completed',
    'Total_Cmppct':'Total_Passes_Completed_Percentage',
    'Total_TotDist':'Total_Passing_Distance',
    'Short_Cmppct':'Short_Passe_Completed_Percentage',
    'Medium_Cmppct':'Medium_Passes_Completed_Percentage',
    'Long_Cmppct':'Long_Passes_Completed_Percentage',
    'SCA_SCA':'Shot_Creating_Actions',
    'SCA_SCA90':'Shot_Creating_Actions_Per90',
    'GCA_GCA':'Goal_Creating_Actions',
    'GCA_GCA90':'Goal_Creating_Actions_Per90',
    'Tackles_Tkl':'Tackles',
    'Tackles_TklW':'Tackles_Won',
    'Challenges_Att':'Defensive_Actions_Attempted',
    'Challenges_Lost':'Defensive_Actions_Lost',
    'Blocks_Blocks':'Blocks',
    'Blocks_Sh':'Shots_Blocked',
    'Blocks_Pass':'Passes_Blocked',
    'Touches_Touches':'Touches',
    'Touches_Def_Pen':'Touches_Defensive_Penalty_Area',
    'Take_Ons_Att':'Take_Ons_Attempted',
    'Take_Ons_Succpct':'Take_Ons_Success_Percentage',
    'Take_Ons_Tkldpct':'Take_Ons_Tackled_Percentage',
    'Carries_Carries':'Carries',
    'Carries_TotDist':'Total_Carrying_Distance',
    'Carries_PrgDist':'Progressive_Carrying_Distance',
    'Carries_PrgC':'Progressive_Carries',
    'Carries_1_3':'Carries_Into_Final_Third',
    'Carries_CPA':'Carries_Into_Penalty_Area',
    'Carries_Mis':'Miscontrols',
    'Carries_Dis':'Dispossessions',
    'Receiving_Rec':'Receiving',
    'Receiving_PrgR':'Progressive_Receiving',
    'Performance_Fls':'Fouls',
    'Performance_Fld':'Fouled',
    'Performance_Off':'Offsides',
    'Performance_Crs':'Crosses',
    'Performance_Recov':'Recoveries'
 
}

filtered_df = filtered_df.rename(columns=column_rename_map)
filtered_df = filtered_df.fillna("N/a")


# Save to CSV
output_file = 'results.csv'
filtered_df.to_csv(output_file, index=False, encoding='utf-8')
print(f"\nSuccess! Data saved to {output_file}")
print("\nColumns in final dataset:")
print(filtered_df.columns.tolist())
