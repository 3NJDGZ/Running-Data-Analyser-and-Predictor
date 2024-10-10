import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

strava_data = pd.read_csv('raw-data-kaggle.csv')

print(strava_data.head())

print(strava_data.athlete.unique())

plt.hist(strava_data['elapsed time (s)'], bins=100)
plt.show()

sns.pairplot(strava_data, vars=['distance (m)', 'elevation gain (m)', 'elapsed time (s)', 'average heart rate (bpm)'])
plt.savefig('Pair_Plot')


'''Analyse data, and clean for better performance of ML:
1. Analyse data with pairplots
2. Check weather to standardize or normalise data, most likely standardize
3. Split data into features and labels
4. Split data into train and test'''

'''Male or female prediction - using classification analysis'''
'''5k, 2k, and Marathon time Prediction - multi-modal linear regression'''