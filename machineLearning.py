import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

strava_data = pd.read_csv('raw-data-kaggle.csv')

head = strava_data.head()

unique_athletes = strava_data.athlete.unique()

#Adding average pace (min/km)

#Analysis of elapsed time
elapsed_time_data = strava_data['elapsed time (s)']
elapsed_info = elapsed_time_data.describe()
print(elapsed_info)

elapsed_time_largest_smallest = strava_data.sort_values(by=['elapsed time (s)'], ascending=False)
print(elapsed_time_largest_smallest)

#Analysis of distance
distance_data = strava_data['distance (m)']
distance_info = distance_data.describe()
print(distance_info)

distance_largest_smallest = strava_data.sort_values(by=['distance (m)'], ascending=False)
print(distance_largest_smallest)

strava_data = strava_data.drop(strava_data[strava_data['elapsed time (s)'] >= 180000].index)

sns.pairplot(strava_data, vars=['distance (m)', 'elevation gain (m)', 'elapsed time (s)', 'average heart rate (bpm)'])
plt.savefig('strava_pairplot.png', dpi=300)
plt.show() 



'''Analyse data, and clean for better performance of ML:
1. Analyse data with pairplots
2. Check weather to standardize or normalise data, most likely standardize
3. Split data into features and labels
4. Split data into train and test'''

'''Male or female prediction - using classification analysis'''
'''5k, 2k, and Marathon time Prediction - multi-modal linear regression'''