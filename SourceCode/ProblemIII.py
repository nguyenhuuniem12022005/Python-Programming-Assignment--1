import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import silhouette_score
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "results.csv")
#  Read data
df = pd.read_csv(csv_path)

#  Convert 'Age' column from "years-days" string format to float
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

#  Filter numeric columns
non_numeric_cols = ['Player', 'Nation', 'Squad', 'Position']
numeric_df = df.drop(columns=non_numeric_cols, errors='ignore')

#  Handle remaining 'N/a' values
numeric_df = numeric_df.replace('N/a', np.nan)

#  Convert to float type
for col in numeric_df.columns:
    numeric_df[col] = pd.to_numeric(numeric_df[col], errors='coerce')

#  Handle missing values
imputer = SimpleImputer(strategy='mean')
numeric_filled = pd.DataFrame(imputer.fit_transform(numeric_df), columns=numeric_df.columns)

#  Standardize data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(numeric_filled)

silhouette_scores = []
for k in range(2, 11):
    kmeans = KMeans(n_clusters=k, random_state=0, n_init=50)
    cluster_labels = kmeans.fit_predict(scaled_data)
    silhouette_avg = silhouette_score(scaled_data, cluster_labels)
    silhouette_scores.append(silhouette_avg)

#  Silhouette Score
plt.figure(figsize=(8, 5))
plt.plot(range(2, 11), silhouette_scores, marker='o', linestyle='--')
plt.title('Silhouette Score for Optimal k')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Silhouette Score')
plt.grid(True)
plt.xticks(range(2, 11))
plt.show()

#  Elbow method to determine optimal number of clusters
wcss = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42, n_init=10)
    kmeans.fit(scaled_data)
    wcss.append(kmeans.inertia_)

plt.figure(figsize=(8, 5))
plt.plot(range(1, 11), wcss, marker='o')
plt.title('Elbow Method to Choose k')
plt.xlabel('Number of Clusters')
plt.ylabel('WCSS')
plt.grid(True)
plt.show()
# We chose to classify the players into 8 groups using the K-means algorithm.
#We used the Elbow Method, which plots the Within-Cluster Sum of Squares (WCSS) for different values of k (number of clusters).
#The “elbow” point — where the rate of WCSS decrease slows down — was found at k = 8, indicating that 8 clusters provide a good balance between accuracy and simplicity.
#This means that increasing beyond 8 clusters only marginally reduces the WCSS, while making interpretation more complex.

#  Apply KMeans with k=8
kmeans = KMeans(n_clusters=8, init='k-means++', n_init=50, random_state=42)
clusters = kmeans.fit_predict(scaled_data)

#  Assign cluster labels to original DataFrame
df['cluster'] = clusters

#  Analyze characteristics of each cluster
print("=== Average metrics by cluster ===")
cluster_profiles = df.groupby('cluster').mean(numeric_only=True)
print(cluster_profiles)

#  PCA for dimensionality reduction to 2D
pca = PCA(n_components=2)
pca_result = pca.fit_transform(scaled_data)

#  Plot clusters
plt.figure(figsize=(10, 6))
sns.scatterplot(x=pca_result[:, 0], y=pca_result[:, 1], hue=clusters, palette='tab10', s=60)
plt.title('K-means Clustering (k=8) with PCA Reduction')
plt.xlabel('Principal Component 1')
plt.ylabel('Principal Component 2')
plt.legend(title='Cluster')
plt.grid(True)
plt.tight_layout()
plt.show()
