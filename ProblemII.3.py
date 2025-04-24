import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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


attack_stats = ['Performance_Gls', 'Goals_PerShot', 'Performance_Ast']  
defense_stats = ['Tackles', 'Interceptions', 'Blocks']  

selected_stats = attack_stats + defense_stats

# Function to plot histogram for a given statistic
def plot_histogram(df, stat_name):
    plt.figure(figsize=(10, 6))
    plt.hist(df[stat_name].dropna(), bins=30, color='blue', edgecolor='black')
    plt.title(f'Histogram of {stat_name}')
    plt.xlabel(stat_name)
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.show()

# Function to plot histograms for selected statistics
def plot_selected_histograms(df, stats):
    for stat in stats:
        plot_histogram(df, stat)

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

# Function to plot histograms for selected statistics for all teams
def plot_selected_team_histograms(df, stats):
    teams = df['Squad'].unique()
    for team in teams:
        print(f"\nAnalyzing team: {team}")
        for stat in stats:
            try:
                plot_team_histogram(df, stat, team)
            except Exception as e:
                print(f"Error plotting {stat} for {team}: {str(e)}")

# Plot histograms for selected statistics across all data
plot_selected_histograms(df, selected_stats)

# Plot histograms for selected statistics for all teams
plot_selected_team_histograms(df, selected_stats)
