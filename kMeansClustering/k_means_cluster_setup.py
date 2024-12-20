import sys
import os
# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dataHandler import DataAnalysis, DataLoader, DataPreprocessor, DataVisualizer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Load the data (simulating your dataset)
if __name__ == "__main__":
    # Load the data
    data_loader = DataLoader('raw-data-kaggle.csv')
    strava_data = data_loader.load_data()

    data_preprocessor = DataPreprocessor(strava_data)
    data_preprocessor.add_pace()
    data_preprocessor.drop_invalid_rows()
    processed_data = data_preprocessor.get_preprocessed_data()

    # Select relevant features for clustering
    features = processed_data[['distance (m)', 'elevation gain (m)', 'elapsed time (s)', 'average heart rate (bpm)', 'pace (min/km)']]

    # Scale the features
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    joblib.dump(scaler, "kMeansClustering/scaler.pkl") # dump pkl files in corresponding folder
    

    # Apply K-Means clustering with 3 clusters
    kmeans = KMeans(n_clusters=3, random_state=42)
    processed_data['cluster'] = kmeans.fit_predict(features_scaled)

    # Analyze the cluster centers
    cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
    cluster_centers_df = pd.DataFrame(cluster_centers, columns=features.columns)
    print("Cluster Centers (Original Scale):")
    print(cluster_centers_df)

    # Example output based on real clustering analysis (you should adjust after analyzing)
    # Cluster 0: low distance, slow pace, low heart rate -> easy
    # Cluster 1: medium distance, moderate pace, moderate heart rate -> medium
    # Cluster 2: high distance, faster pace, higher heart rate -> hard

    # Assign labels based on cluster centers analysis
    # Mapping each cluster to an intensity level: easy, medium, hard
    cluster_centers_df['intensity'] = ['easy run', 'long run', 'intense run']  # Adjust these labels based on your analysis
    processed_data['intensity'] = processed_data['cluster'].map({
        0: 'easy run',  # Example mapping (adjust based on actual analysis of your cluster centers)
        1: 'long run',
        2: 'intense run'
    })

    # Visualize the clusters
    sns.pairplot(processed_data, vars=['distance (m)', 'elapsed time (s)', 'elevation gain (m)', 'average heart rate (bpm)', 'pace (min/km)'], hue='intensity')
    plt.show()

    # Display the final data with intensity labels
    print(processed_data[['distance (m)', 'elapsed time (s)', 'elevation gain (m)', 'average heart rate (bpm)', 'pace (min/km)', 'intensity']])

    # Saving K means model
    joblib.dump(kmeans, "kMeansClustering/kmeans_model.pkl") # save to corresponding folder location

    