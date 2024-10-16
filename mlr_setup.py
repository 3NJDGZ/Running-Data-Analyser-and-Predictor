from datahandler import DataLoader, DataAnalysis, DataPreprocessor, DataVisualizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import pandas as pd
import joblib

# Main execution flow (EXAMPLE)
if __name__ == "__main__":
    # Load the data
    data_loader = DataLoader('raw-data-kaggle.csv')
    strava_data = data_loader.load_data()

    data_preprocessor = DataPreprocessor(strava_data)
    data_preprocessor.add_pace()
    data_preprocessor.drop_invalid_rows()
    processed_data = data_preprocessor.get_preprocessed_data()

    data_analysis = DataAnalysis(processed_data)
    data_analysis.display_head()
    data_analysis.display_nunique_athletes()
    data_analysis.display_dtypes()
    data_analysis.describe_data()

    # Visualize the data
    data_visualizer = DataVisualizer(processed_data)
    data_visualizer.pairplot('strava_pairplot_after.png', ['distance (m)', 'elevation gain (m)', 'elapsed time (s)', 'average heart rate (bpm)'])

    # Features (X)
    X = processed_data[['elevation gain (m)', 'distance (m)', 'average heart rate (bpm)']]
    # Target (y)
    y = processed_data[['elapsed time (s)']]

    # Split the data into training and testing sets
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and fit the Linear Regression model
    mlr = LinearRegression()
    mlr.fit(x_train, y_train)

    # Make predictions
    y_pred = mlr.predict(x_test)

    # Calculate performance metrics
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Print the performance metrics
    print(f"Mean Absolute Error (MAE): {mae:.2f}")
    print(f"Mean Squared Error (MSE): {mse:.2f}")
    print(f"R² Score: {r2:.2f}")

    # Visualize Predictions vs Actual Values
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, color='blue', label='Predicted vs Actual', alpha=0.6)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='red', linestyle='--', label='Ideal Fit (y=x)')
    plt.xlabel('Actual Distance (m)')
    plt.ylabel('Predicted Distance (m)')
    plt.title('Actual vs Predicted Distance')
    plt.grid()
    plt.legend()
    plt.savefig('mlr_prediction_vs_actial_values', dpi=300)

    # Optional: Plotting Residuals
    plt.figure(figsize=(10, 6))
    residuals = y_test - y_pred
    plt.scatter(y_pred, residuals, color='green', alpha=0.6)
    plt.axhline(y=0, color='red', linestyle='--')
    plt.xlabel('Predicted Distance (m)')
    plt.ylabel('Residuals')
    plt.title('Residuals Plot')
    plt.grid()
    plt.savefig('mlr_residuals', dpi=300)

    # Save the model for later use
    joblib.dump(mlr, 'linear_regression_model.pkl')

   # Make a prediction using a DataFrame
    new_data = pd.DataFrame([[100, 2000, 150]], columns=['elevation gain (m)', 'distance (m)', 'average heart rate (bpm)'])
    y_pred1 = mlr.predict(new_data)
    print(f"Predicted Elapsed Time for [100, 2000, 150]: {y_pred1[0][0]:.2f} seconds")

