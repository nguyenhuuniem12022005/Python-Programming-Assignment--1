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
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 7: Train and Evaluate Models
def evaluate_model(model, name):
    pipeline = Pipeline([
        ('scaler', RobustScaler()),
        ('selector', RFE(estimator=RandomForestRegressor(n_estimators=120), n_features_to_select=40)),
        ('model', model)
    ])
    pipeline.fit(X_train, y_train)
    y_train_pred = pipeline.predict(X_train)
    y_test_pred = pipeline.predict(X_test)

    # RFE helps remove noise:
    # Removes features that contribute little, helping the model:
    # - Reduce overfitting.
    # - Become more interpretable and deployable.
    # Random Forest is used as RFE estimator because:
    # - It provides solid feature importance scores from multiple decision trees.
    # - It is stable and less sensitive to outliers.

    print(f"\n{name} Results:")
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

    # Feature Importance
    selector = pipeline.named_steps['selector']
    selected_features = X_train.columns[selector.get_support()]
    if hasattr(pipeline.named_steps['model'], 'feature_importances_'):
        importances = pipeline.named_steps['model'].feature_importances_
        feature_importance = pd.Series(importances, index=selected_features).sort_values(ascending=False)
        print("\nTop 20 Important Features:")
        print(feature_importance.head(20))

# Linear Regression
evaluate_model(LinearRegression(), "Linear Regression")

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
    random_state=42), "Gradient Boosting")

# Random Forest
evaluate_model(RandomForestRegressor(
    n_estimators=80,
    max_depth=4,
    min_samples_split=20,
    random_state=42), "Random Forest")


'''Linear Regression Results:
Train:
  R2 Score: 0.7106
  RMSE: 0.4049
  MAE: 0.3191
  Spearman: 0.8442
Test:
  R2 Score: 0.5940
  RMSE: 0.4984
  MAE: 0.4137
  Spearman: 0.7846

Gradient Boosting Results:
Train:
  R2 Score: 0.8324
  RMSE: 0.3081
  MAE: 0.2312
  Spearman: 0.9095
Test:
  R2 Score: 0.6958
  RMSE: 0.4314
  MAE: 0.3451
  Spearman: 0.7955

Top 20 Important Features:
Age                                   0.453779
Carries                               0.040307
Expected_xG                           0.039020
Shots_Blocked                         0.038917
Total_Carrying_Distance               0.032285
Per_90_Minutes_xG                     0.032266
Take_Ons_Success_Percentage           0.028823
Touches_Att_Pen                       0.027820
Touches_Att_3rd                       0.025993
Touches_Def_3rd                       0.025525
Shots_On_Target_Per90                 0.022617
Progression_PrgP                      0.020743
Minutes                               0.020648
Aerial_Duels_Wonpct                   0.019053
Per_90_Minutes_Ast                    0.015598
Medium_Passes_Completed_Percentage    0.015423
Matches                               0.015089
Total_Passes_Completed_Percentage     0.013819
Long_Passes_Completed_Percentage      0.013063
Short_Passe_Completed_Percentage      0.012776
dtype: float64

Random Forest Results:
Train:
  R2 Score: 0.7640
  RMSE: 0.3657
  MAE: 0.2862
  Spearman: 0.8789
Test:
  R2 Score: 0.6661
  RMSE: 0.4520
  MAE: 0.3512
  Spearman: 0.7497

Top 20 Important Features:
Age                                  0.573254
Total_Carrying_Distance              0.063013
Progressive_Carrying_Distance        0.046141
Touches_Att_3rd                      0.033295
Touches_Att_Pen                      0.026146
Matches                              0.019381
Carries                              0.018303
Per_90_Minutes_xG                    0.016485
Shot_Creating_Actions                0.014218
Expected_xG                          0.013891
Per_90_Minutes_Gls                   0.012210
Total_Passes_Completed_Percentage    0.011792
Progressive_Receiving                0.011675
Shots_Blocked                        0.010099
Take_Ons_Success_Percentage          0.009899
Expected_xAG                         0.009204
Carries_Into_Penalty_Area            0.008917
Passes_Into_Penalty_Area             0.008271
Progression_PrgP                     0.007270
Per_90_Minutes_Ast                   0.007263
dtype: float64'''

'''Linear Regression Results:

Train R²: 0.7106 → Test R²: 0.5940 → Moderate performance, serves as a good baseline.

Spearman correlation is decent but lower than others.

Gradient Boosting Results:

Best overall performance on test set across all 4 metrics (R², RMSE, MAE, Spearman).

Slight overfitting (Train R² 0.8324 → Test R² 0.6958), but still acceptable.

Highest Spearman correlation, indicating the best ability to rank players.

Random Forest Results:

Lower test performance than Gradient Boosting.

Slight underfitting (Train R² 0.7640 and Test R² 0.6661 both relatively lower).

Lower Spearman than GBM.'''

'''Final Choice: Gradient Boosting Regressor
Because it:

Achieves the best test performance.

Has the highest ranking ability (Spearman correlation).

Is not severely overfitting or underfitting.'''