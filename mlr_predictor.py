import pandas as pd
import joblib

# Load the previously saved model
mlr_loaded = joblib.load('linear_regression_model.pkl')

# Make a prediction using a DataFrame
new_data = pd.DataFrame([[14, 10700, 150]], columns=['elevation gain (m)', 'distance (m)', 'average heart rate (bpm)'])
y_pred1 = mlr_loaded.predict(new_data)
print(f"Predicted Elapsed Time for: {y_pred1[0][0]:.2f} seconds")