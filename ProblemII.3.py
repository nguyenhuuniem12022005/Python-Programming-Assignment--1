import pandas as pd
import matplotlib.pyplot as plt

# Load the data from CSV
df = pd.read_csv('results.csv')

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

# Function to plot histogram for a given statistic
def plot_histogram(df, stat_name):
    plt.figure(figsize=(10, 6))
    plt.hist(df[stat_name].dropna(), bins=30, color='blue', edgecolor='black')
    plt.title(f'Histogram of {stat_name}')
    plt.xlabel(stat_name)
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()

# Function to plot histograms for each statistic
def plot_all_histograms(df):
    stats =[df.columns[3]] + df.columns[4:].tolist()  # Assuming the first four columns are not statistics
    for stat in stats:
        plot_histogram(df, stat)

# Plot histograms for all statistics


# Function to plot histogram for a given statistic and team
def plot_team_histogram(df, stat_name, team):
    team_df = df[df['Squad'] == team]
    plt.figure(figsize=(10, 6))
    plt.hist(team_df[stat_name].dropna(), bins=30, color='blue', edgecolor='black')
    plt.title(f'Histogram of {stat_name} for Team: {team}')
    plt.xlabel(stat_name)
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()


# Function to plot histograms for all statistics for all teams
def plot_all_team_histograms(df):
    # Get all unique teams
    teams = df['Squad'].unique()

    # Get all statistics columns (assuming first 4 columns are not statistics)
    stats = [df.columns[3]] + df.columns[4:].tolist()

    # Loop through each team and each statistic
    for team in teams:
        print(f"\nAnalyzing team: {team}")
        for stat in stats:
            try:
                plot_team_histogram(df, stat, team)
            except Exception as e:
                print(f"Error plotting {stat} for {team}: {str(e)}")


# Plot histograms for all statistics across all data
plot_all_histograms(df)

# Plot histograms for all statistics for all teams
plot_all_team_histograms(df)

