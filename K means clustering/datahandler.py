import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Class to handle loading of the dataset
class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def load_data(self):
        self.data = pd.read_csv(self.file_path)
        return self.data

# Class to preprocess the data
class DataPreprocessor:
    def __init__(self, data):
        self.data = data.copy()

    def add_pace(self):
        # Add the 'pace (min/km)' feature to the dataset
        self.data['pace (min/km)'] = (self.data['elapsed time (s)'] / 60) / (self.data['distance (m)'] * 0.001)
    
    def drop_invalid_rows(self):
        # Filter out rows based on conditions
        self.data = self.data[
            (self.data['elapsed time (s)'] < 180000) & 
            (self.data['elapsed time (s)'] > 0) & 
            (self.data['distance (m)'] > 0) & 
            (self.data['pace (min/km)'] >= 2.56333) & 
            (self.data['pace (min/km)'] <= 15) & 
            (self.data['average heart rate (bpm)'].notnull()) & 
            (self.data['average heart rate (bpm)'] > 0) &
            (self.data['elevation gain (m)'] < 200.0)
        ]
    
    def get_preprocessed_data(self):
        return self.data

# Class to visualize the data
class DataVisualizer:
    def __init__(self, data):
        self.data = data
    
    def pairplot(self, save_path, variables):
        # Create a pairplot using seaborn
        sns.pairplot(self.data, vars=variables)
        plt.savefig(save_path, dpi=300)

# Class to perform basic analysis and statistics
class DataAnalysis:
    def __init__(self, data):
        self.data = data
    
    def display_head(self):
        print(self.data.head())
    
    def display_nunique_athletes(self):
        print(f"Number of unique athletes: {self.data.athlete.nunique()}")
    
    def display_dtypes(self):
        print(self.data.dtypes)
    
    def describe_data(self):
        print(self.data.describe())