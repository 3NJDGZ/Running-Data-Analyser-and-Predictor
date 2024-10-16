import pandas as pd
import joblib

# Load the previously saved model
kmeans = joblib.load('kmeans_model.pkl')
scaler = joblib.load('scaler.pkl')

# Predict the cluster of a new run
new_run = {
    'distance (m)': 2000,            # Distance in meters
    'elevation gain (m)': 10,        # Elevation gain in meters
    'pace (min/km)': 6,             # Pace in min/km
    'average heart rate (bpm)': 150   # Heart rate in bpm
}

# Convert the new run to a DataFrame
new_run_df = pd.DataFrame([new_run])

# Select and scale the relevant features for the new run (using the same scaler)
new_run_features = new_run_df[['distance (m)', 'elevation gain (m)', 'pace (min/km)', 'average heart rate (bpm)']]
new_run_scaled = scaler.transform(new_run_features)

# Predict the cluster for the new run
predicted_cluster = kmeans.predict(new_run_scaled)

# Map the predicted cluster to intensity labels (adjust based on actual cluster mapping)
cluster_label_map = {
    0: 'tempo run',   # Cluster 0 represents 'tempo run' (adjust as per your cluster analysis)
    1: 'long run',    # Cluster 1 represents 'long run'
    2: 'easy run'     # Cluster 2 represents 'easy run'
}

# Get the intensity label for the new run
predicted_intensity = cluster_label_map[predicted_cluster[0]]

# Output the result
print(f"Predicted cluster: {predicted_cluster[0]}")
print(f"Predicted run intensity: {predicted_intensity}")
