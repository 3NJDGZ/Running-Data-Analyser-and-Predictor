import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#Original data
strava_data = pd.read_csv('raw-data-kaggle.csv')
head = strava_data.head()
nunique_athletes = strava_data.athlete.nunique()
strava_data.dtypes
sns.pairplot(strava_data, vars=['distance (m)', 'elevation gain (m)', 'elapsed time (s)', 'average heart rate (bpm)'])
plt.savefig('strava_pairplot_before.png', dpi=300)
print(strava_data.describe())


#Adding pace
strava_data['pace (min/km)'] = (strava_data['elapsed time (s)'] / 60) /(strava_data['distance (m)'] * 0.001)


# Dropping rows based on conditions
strava_data = strava_data[
    (strava_data['elapsed time (s)'] < 180000) & 
    (strava_data['elapsed time (s)'] > 0) & 
    (strava_data['distance (m)'] > 0) & 
    (strava_data['pace (min/km)'] >= 2.56333) & 
    (strava_data['pace (min/km)'] <= 15) & 
    (strava_data['average heart rate (bpm)'].notnull()) & 
    (strava_data['average heart rate (bpm)'] > 0)
]


#Analysis of average pace (min/km)
pace_info = strava_data['pace (min/km)'].describe()
pace_largest_smallest = strava_data.sort_values(by=['pace (min/km)'], ascending=False)
plt.hist(strava_data['pace (min/km)'], bins=100)
plt.xlabel('Pace (min/km)')
plt.ylabel('Frequency')
#plt.show()


#Analysis of elapsed time
elapsed_time_data = strava_data['elapsed time (s)']
elapsed_info = elapsed_time_data.describe()
elapsed_time_largest_smallest = strava_data.sort_values(by=['elapsed time (s)'], ascending=False)


#Analysis of distance
distance_data = strava_data['distance (m)']
distance_info = distance_data.describe()
distance_largest_smallest = strava_data.sort_values(by=['distance (m)'], ascending=False)


#Analysis of cleaned data
print(strava_data)
print(strava_data.describe())
print('Current length of data: ' + str(len(strava_data)))


sns.pairplot(strava_data, vars=['distance (m)', 'elevation gain (m)', 'elapsed time (s)', 'average heart rate (bpm)'])
plt.savefig('strava_pairplot_after.png', dpi=300)