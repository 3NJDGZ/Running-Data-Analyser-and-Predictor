import pandas as pd
import joblib


def predict(distance, elevationGain, elapsedTime, averageHeartRate):
    # Load the previously saved model
    kmeans = joblib.load('kMeansClustering/kmeans_model.pkl')
    scaler = joblib.load('kMeansClustering/scaler.pkl')
    
    # Predict the cluster of a new run
    new_run = {
        'distance (m)': distance,
        'elevation gain (m)': elevationGain,
        'elapsed time (s)': elapsedTime,
        'average heart rate (bpm)': averageHeartRate,
        'pace (min/km)': (elapsedTime / 60) / (distance * 0.001),
    }

    # Convert the new run to a DataFrame
    new_run_df = pd.DataFrame([new_run])

    # Select and scale the relevant features for the new run (using the same scaler)
    new_run_features = new_run_df[['distance (m)', 'elevation gain (m)', 'elapsed time (s)', 'average heart rate (bpm)', 'pace (min/km)']]
    new_run_scaled = scaler.transform(new_run_features)

    # Predict the cluster for the new run
    predicted_cluster = kmeans.predict(new_run_scaled)

    # Map the predicted cluster to intensity labels (adjust based on actual cluster mapping)
    cluster_label_map = {
        0: 'easy run',
        1: 'long run',
        2: 'intense run'
    }

    # Get the intensity label for the new run
    predicted_intensity = cluster_label_map[predicted_cluster[0]]

    # Output the result
    print(f"\nDistance (m): {distance}, Max Elevation (m): {elevationGain}, Elapsed Time (s): {elapsedTime}, Avg HR: {averageHeartRate}");
    print(f"Predicted cluster: {predicted_cluster[0]}")
    print(f"Predicted run intensity: {predicted_intensity}\n")

# predict(3000, 5, 1200, 140)  # 3 km run, small elevation, 20 min, lower heart rate
# predict(7000, 50, 2400, 155)  # 7 km run, some elevation, 40 min, moderate heart rate
# predict(15000, 300, 5400, 160)  # 15 km run, significant elevation, 90 min, higher heart rate
# predict(5000, 20, 1200, 175)  # 5 km run, minimal elevation, 20 min, high heart rate
# predict(21000, 400, 7500, 165)  # 21 km run, 400m elevation, 125 min, medium-high heart rate
# predict(5000, 0, 1800, 130)  # 5 km run, no elevation, 30 min, low heart rate
# predict(3000, 10, 600, 180)  # 3 km run, minimal elevation, 10 min, very high heart rate

predict(1000, 24, 900, 190) # my max run