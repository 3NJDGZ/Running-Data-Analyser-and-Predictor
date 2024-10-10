import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

strava_data = pd.read_csv('raw-data-kaggle.csv')

print(strava_data.head())

print(strava_data.athlete.unique())

plt.scatter(strava_data['elapsed time (s)'], strava_data['distance (m)'])
plt.show()

sns.pairplot(strava_data, vars=['distance (m)', 'elevation gain (m)', 'elapsed time (s)', 'average heart rate (bpm)'])

plt.show()

'''Analyse data, and clean of any problems or outliers for better performance of ML'''
'''Standardize data for ML'''
'''Split data into features and labels'''
'''Male or female prediction - using classification analysis'''