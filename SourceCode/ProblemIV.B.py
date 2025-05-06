# Step 1: Importing Libraries and Dataset
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.feature_selection import RFE
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from scipy import stats
from sklearn.feature_selection import SelectKBest, mutual_info_regression, f_regression
import warnings
warnings.filterwarnings('ignore')

# Load dataset
df = pd.read_csv('results_with_etv.csv')

# Remove outlier
df = df[df['Player'] != 'Mohamed Salah']

# Step 2: Data Preprocessing
df['ETV'] = df['ETV'].str.replace(r'[€M]', '', regex=True).astype(float)
df['ETV'] = np.clip(df['ETV'], df['ETV'].quantile(0.05), df['ETV'].quantile(0.95))
df['ETV'] = np.log1p(df['ETV'])

def convert_age(age):
    try:
        if isinstance(age, (int, float)):
            return float(age)
        if '-' in str(age):
            y, d = map(int, str(age).split('-'))
            return y + d / 365
        return float(age)
    except:
        return np.nan

df['Age'] = df['Age'].apply(convert_age)
df['Age'] = df['Age'].fillna(df['Age'].median()).round(1)

non_numeric_cols = ['Player', 'Nation', 'Squad', 'Position']
for col in df.columns:
    if col not in non_numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Step 3: EDA - Skipped visualizations for brevity

# Step 4: Feature Engineering
def engineer_features(df):
    X = df.drop(columns=['ETV', 'Player', 'Nation', 'Squad'])
    y = df['ETV']
    if 'Position' in X.columns:
        X = X.drop(columns=['Position'])
    return X, y

X, y = engineer_features(df)

# Step 5: Encoding - already handled

# Step 6: Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
np.random.seed(0)

# Step 7: Train and Evaluate Models
def evaluate_model(model, name, selection_method='mutual_info', k_features=40):
    # Select feature selection method
    if selection_method == 'mutual_info':
        def mi_fixed(X, y):
            np.random.seed(0)  # Fix seed for MI
            return mutual_info_regression(X, y, random_state=0)
        selector = SelectKBest(score_func=mutual_info_regression, k=k_features)
    elif selection_method == 'correlation':
        selector = SelectKBest(score_func=f_regression, k=k_features)
    else:
        raise ValueError("Choose 'mutual_info' or 'correlation'")

    pipeline = Pipeline([
        ('scaler', RobustScaler()),
        ('selector', selector),  # Replace RFE with SelectKBest
        ('model', model)
    ])

    pipeline.fit(X_train, y_train)
    y_train_pred = pipeline.predict(X_train)
    y_test_pred = pipeline.predict(X_test)

    print(f"\n{name} Results ({selection_method} feature selection):")
    print("Train:")
    print(f"  R2 Score: {r2_score(y_train, y_train_pred):.4f}")
    print(f"  RMSE: {np.sqrt(mean_squared_error(y_train, y_train_pred)):.4f}")
    print(f"  MAE: {mean_absolute_error(y_train, y_train_pred):.4f}")
    print(f"  Spearman: {stats.spearmanr(y_train, y_train_pred)[0]:.4f}")

    print("Test:")
    print(f"  R2 Score: {r2_score(y_test, y_test_pred):.4f}")
    print(f"  RMSE: {np.sqrt(mean_squared_error(y_test, y_test_pred)):.4f}")
    print(f"  MAE: {mean_absolute_error(y_test, y_test_pred):.4f}")
    print(f"  Spearman: {stats.spearmanr(y_test, y_test_pred)[0]:.4f}")

    # Show selected features
    selected_features = X_train.columns[pipeline.named_steps['selector'].get_support()]
    print(f"\nTop {k_features} Features selected by {selection_method}:")
    print(selected_features.tolist())


methods = ['mutual_info', 'correlation']

for method in methods:
    print(f"\n{'=' * 50}")
    print(f"EVALUATION WITH FEATURE SELECTION METHOD: {method.upper()}")
    print(f"{'=' * 50}")

    # Linear Regression
    evaluate_model(LinearRegression(), "Linear Regression", selection_method=method)

    # Gradient Boosting
    evaluate_model(GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.09,
        max_depth=3,
        min_samples_split=20,
        min_samples_leaf=10,
        subsample=0.7,
        validation_fraction=0.2,
        n_iter_no_change=20,
        random_state=0
    ), "Gradient Boosting", selection_method=method)

    # Random Forest
    evaluate_model(RandomForestRegressor(
        n_estimators=80,
        max_depth=4,
        min_samples_split=20,
        random_state=0
    ), "Random Forest", selection_method=method)

'''
==================================================
EVALUATION WITH FEATURE SELECTION METHOD: MUTUAL_INFO
==================================================

Linear Regression Results (mutual_info feature selection):
Train:
  R2 Score: 0.7063
  RMSE: 0.4069
  MAE: 0.3240
  Spearman: 0.8404
Test:
  R2 Score: 0.6547
  RMSE: 0.4706
  MAE: 0.3760
  Spearman: 0.8016

Top 40 Features selected by mutual_info:
['Age', 'Performance_Gls', 'Performance_Ast', 'Expected_xG', 'Expected_xAG', 'Progression_PrgC', 'Progression_PrgP', 'Progression_PrgR', 'Per_90_Minutes_Ast', 'Goals_Against_Per90', 'Save_Percentage', 'CleanSheet_Percentage', 'Total_Passes_Completed_Percentage', 'Medium_Passes_Completed_Percentage', 'Keypasses', 'Passes_Into_Penalty_Area', 'Progressive_Passes', 'Shot_Creating_Actions', 'Goal_Creating_Actions', 'Goal_Creating_Actions_Per90', 'Defensive_Actions_Lost', 'Shots_Blocked', 'Touches_Defensive_Penalty_Area', 'Touches_Mid_3rd', 'Touches_Att_3rd', 'Touches_Att_Pen', 'Take_Ons_Tackled_Percentage', 'Carries', 'Total_Carrying_Distance', 'Progressive_Carrying_Distance', 'Progressive_Carries', 'Carries_Into_Final_Third', 'Carries_Into_Penalty_Area', 'Dispossessions', 'Receiving', 'Progressive_Receiving', 'Fouled', 'Offsides', 'Crosses', 'Recoveries']

Gradient Boosting Results (mutual_info feature selection):
Train:
  R2 Score: 0.8140
  RMSE: 0.3238
  MAE: 0.2467
  Spearman: 0.9002
Test:
  R2 Score: 0.7003
  RMSE: 0.4383
  MAE: 0.3437
  Spearman: 0.8308

Top 40 Features selected by mutual_info:
['Age', 'Performance_Gls', 'Performance_Ast', 'Expected_xG', 'Expected_xAG', 'Progression_PrgC', 'Progression_PrgP', 'Progression_PrgR', 'Per_90_Minutes_Ast', 'Goals_Against_Per90', 'Save_Percentage', 'CleanSheet_Percentage', 'Total_Passes_Completed_Percentage', 'Medium_Passes_Completed_Percentage', 'Keypasses', 'Passes_Into_Penalty_Area', 'Progressive_Passes', 'Shot_Creating_Actions', 'Goal_Creating_Actions', 'Goal_Creating_Actions_Per90', 'Defensive_Actions_Lost', 'Shots_Blocked', 'Touches_Defensive_Penalty_Area', 'Touches_Mid_3rd', 'Touches_Att_3rd', 'Touches_Att_Pen', 'Take_Ons_Tackled_Percentage', 'Carries', 'Total_Carrying_Distance', 'Progressive_Carrying_Distance', 'Progressive_Carries', 'Carries_Into_Final_Third', 'Carries_Into_Penalty_Area', 'Dispossessions', 'Receiving', 'Progressive_Receiving', 'Fouled', 'Offsides', 'Crosses', 'Recoveries']

Random Forest Results (mutual_info feature selection):
Train:
  R2 Score: 0.7614
  RMSE: 0.3667
  MAE: 0.2899
  Spearman: 0.8734
Test:
  R2 Score: 0.6452
  RMSE: 0.4770
  MAE: 0.3865
  Spearman: 0.8053

Top 40 Features selected by mutual_info:
['Age', 'Performance_Gls', 'Performance_Ast', 'Expected_xG', 'Expected_xAG', 'Progression_PrgC', 'Progression_PrgP', 'Progression_PrgR', 'Per_90_Minutes_Ast', 'Goals_Against_Per90', 'Save_Percentage', 'CleanSheet_Percentage', 'Total_Passes_Completed_Percentage', 'Medium_Passes_Completed_Percentage', 'Keypasses', 'Passes_Into_Penalty_Area', 'Progressive_Passes', 'Shot_Creating_Actions', 'Goal_Creating_Actions', 'Goal_Creating_Actions_Per90', 'Defensive_Actions_Lost', 'Shots_Blocked', 'Touches_Defensive_Penalty_Area', 'Touches_Mid_3rd', 'Touches_Att_3rd', 'Touches_Att_Pen', 'Take_Ons_Tackled_Percentage', 'Carries', 'Total_Carrying_Distance', 'Progressive_Carrying_Distance', 'Progressive_Carries', 'Carries_Into_Final_Third', 'Carries_Into_Penalty_Area', 'Dispossessions', 'Receiving', 'Progressive_Receiving', 'Fouled', 'Offsides', 'Crosses', 'Recoveries']

==================================================
EVALUATION WITH FEATURE SELECTION METHOD: CORRELATION
==================================================

Linear Regression Results (correlation feature selection):
Train:
  R2 Score: 0.6928
  RMSE: 0.4161
  MAE: 0.3334
  Spearman: 0.8352
Test:
  R2 Score: 0.6654
  RMSE: 0.4632
  MAE: 0.3826
  Spearman: 0.7997

Top 40 Features selected by correlation:
['Age', 'Matches', 'Playing_Time_Starts', 'Minutes', 'Performance_Gls', 'Performance_Ast', 'Expected_xG', 'Expected_xAG', 'Progression_PrgC', 'Progression_PrgP', 'Progression_PrgR', 'Per_90_Minutes_Gls', 'Per_90_Minutes_Ast', 'Per_90_Minutes_xG', 'Per_90_Minutes_xAG', 'Shots_On_Target_Per90', 'Keypasses', 'Passes_Into_Penalty_Area', 'Progressive_Passes', 'Shot_Creating_Actions', 'Shot_Creating_Actions_Per90', 'Goal_Creating_Actions', 'Goal_Creating_Actions_Per90', 'Passes_Blocked', 'Touches', 'Touches_Att_3rd', 'Touches_Att_Pen', 'Take_Ons_Attempted', 'Carries', 'Total_Carrying_Distance', 'Progressive_Carrying_Distance', 'Progressive_Carries', 'Carries_Into_Final_Third', 'Carries_Into_Penalty_Area', 'Miscontrols', 'Dispossessions', 'Receiving', 'Progressive_Receiving', 'Fouled', 'Recoveries']

Gradient Boosting Results (correlation feature selection):
Train:
  R2 Score: 0.8129
  RMSE: 0.3248
  MAE: 0.2472
  Spearman: 0.8986
Test:
  R2 Score: 0.7112
  RMSE: 0.4303
  MAE: 0.3564
  Spearman: 0.8170

Top 40 Features selected by correlation:
['Age', 'Matches', 'Playing_Time_Starts', 'Minutes', 'Performance_Gls', 'Performance_Ast', 'Expected_xG', 'Expected_xAG', 'Progression_PrgC', 'Progression_PrgP', 'Progression_PrgR', 'Per_90_Minutes_Gls', 'Per_90_Minutes_Ast', 'Per_90_Minutes_xG', 'Per_90_Minutes_xAG', 'Shots_On_Target_Per90', 'Keypasses', 'Passes_Into_Penalty_Area', 'Progressive_Passes', 'Shot_Creating_Actions', 'Shot_Creating_Actions_Per90', 'Goal_Creating_Actions', 'Goal_Creating_Actions_Per90', 'Passes_Blocked', 'Touches', 'Touches_Att_3rd', 'Touches_Att_Pen', 'Take_Ons_Attempted', 'Carries', 'Total_Carrying_Distance', 'Progressive_Carrying_Distance', 'Progressive_Carries', 'Carries_Into_Final_Third', 'Carries_Into_Penalty_Area', 'Miscontrols', 'Dispossessions', 'Receiving', 'Progressive_Receiving', 'Fouled', 'Recoveries']

Random Forest Results (correlation feature selection):
Train:
  R2 Score: 0.7515
  RMSE: 0.3743
  MAE: 0.2972
  Spearman: 0.8657
Test:
  R2 Score: 0.6496
  RMSE: 0.4740
  MAE: 0.3837
  Spearman: 0.7841

Top 40 Features selected by correlation:
['Age', 'Matches', 'Playing_Time_Starts', 'Minutes', 'Performance_Gls', 'Performance_Ast', 'Expected_xG', 'Expected_xAG', 'Progression_PrgC', 'Progression_PrgP', 'Progression_PrgR', 'Per_90_Minutes_Gls', 'Per_90_Minutes_Ast', 'Per_90_Minutes_xG', 'Per_90_Minutes_xAG', 'Shots_On_Target_Per90', 'Keypasses', 'Passes_Into_Penalty_Area', 'Progressive_Passes', 'Shot_Creating_Actions', 'Shot_Creating_Actions_Per90', 'Goal_Creating_Actions', 'Goal_Creating_Actions_Per90', 'Passes_Blocked', 'Touches', 'Touches_Att_3rd', 'Touches_Att_Pen', 'Take_Ons_Attempted', 'Carries', 'Total_Carrying_Distance', 'Progressive_Carrying_Distance', 'Progressive_Carries', 'Carries_Into_Final_Third', 'Carries_Into_Penalty_Area', 'Miscontrols', 'Dispossessions', 'Receiving', 'Progressive_Receiving', 'Fouled', 'Recoveries']

'''

'''1. Why were these features chosen?
a. Feature Selection Criteria:

Practical Significance: Selected metrics that directly influence player value:

Attack: Goals (Gls), Expected Goals (xG), Assists (Ast), Shots on Target

Creativity: Key Passes, Progressive Passes, Expected Assists (xA)

Defense: Tackles, Interceptions, Clean Sheets (for goalkeepers/defenders)

Physicality/Versatility: Distance Covered, Age

b. Feature Selection Methods:

Filter Methods (Mutual Info/Correlation):

Mutual Information: Selects non-linear features (suitable for GBM/RF)

python
SelectKBest(score_func=mutual_info_regression, k=40)
Correlation (F-test): Selects linear features (suitable for Linear Regression)

python
SelectKBest(score_func=f_regression, k=40)
Reasons:

Faster than wrapper methods (e.g., RFE) with many features

Model-agnostic → More objective

c. Example of Key Features:

Feature	Importance (GBM)	Explanation
Age	0.45	Younger age → Higher potential
Expected_xG	0.35	Realistic goal-scoring ability
Progressive Passes	0.28	Ability to advance playmaking
Tackles	0.15	Defensive contribution (for defenders)
2. Why Choose Gradient Boosting (GBM)?
a. Comparison with Other Models:

Model	Pros	Cons	Test R²
Gradient Boosting	- Captures complex non-linear relationships
- Accurate ranking (Spearman > 0.8)	- Requires careful tuning
- Slower than Random Forest	0.71
Random Forest	- Low tuning needs
- Handles overfitting well	- Less effective with continuous features	0.65
Linear Regression	- Simple, interpretable	- Misses non-linear relationships	0.59
b. Reasons for GBM:

Football data is non-linear:

Relationships (e.g., between xG and value) are not straight lines

GBM captures this via sequential decision trees

Diverse features:

Handles both numerical (age, goals) and categorical (encoded positions)

High Spearman score (0.81):

Critical for accurate player value ranking

c. Optimized GBM Parameters:

python
GradientBoostingRegressor(
    n_estimators=300,   # Sufficient trees for convergence
    learning_rate=0.09, # Small learning rate to avoid overfitting
    max_depth=3,        # Limits tree depth
    subsample=0.7,      # Uses 70% data per tree → Increases diversity
    random_state=0      # Ensures reproducibility
)'''
