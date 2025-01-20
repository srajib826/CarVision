import numpy as np
from scipy.signal import find_peaks
import time
from datetime import datetime
import csv
from collections import deque
import matplotlib.pyplot as plt
import pandas as pd

class MMWaveRadarProcessor:
    
    def __init__(self):
        self.RANGE_RESOLUTION = 0.244  
        self.DOPPLER_RESOLUTION = 0.13  
        self.NUM_RANGE_BINS = 64
        self.NUM_DOPPLER_BINS = 16
        self.NUM_FRAMES = 4
        
        self.MIN_RANGE = 1.5  
        self.MAX_RANGE = 6.0  
        self.PEAK_HEIGHT_THRESHOLD = 0.85
        self.DOPPLER_CENTER_BIN = 8
        
        self.distance_history = deque(maxlen=50)
        self.velocity_history = deque(maxlen=50)
        self.timestamp_history = deque(maxlen=50)
        
        self.csv_filename = f"radar_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self._initialize_csv()

    def _initialize_csv(self):
        with open(self.csv_filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['datetime', 'distance', 'velocity'])

    def process_frame(self, doppler_data):
        min_bin = int(self.MIN_RANGE / self.RANGE_RESOLUTION)
        max_bin = int(self.MAX_RANGE / self.RANGE_RESOLUTION)
        cropped_dop = doppler_data.sum(axis=0)[min_bin:max_bin]
        
        peaks, properties = find_peaks(cropped_dop, 
                                    height=max(cropped_dop) * self.PEAK_HEIGHT_THRESHOLD)
        
        distance = None
        highest_peak_idx = None
        if len(peaks) > 0:
            highest_peak_idx = peaks[np.argmax(properties['peak_heights'])]
            distance = highest_peak_idx * self.RANGE_RESOLUTION
        
        velocity = None
        if distance is not None and highest_peak_idx < self.NUM_DOPPLER_BINS:
            doppler_profile = doppler_data[:, highest_peak_idx]
            max_doppler_idx = np.argmax(doppler_profile)
            
            if max_doppler_idx > self.DOPPLER_CENTER_BIN:
                velocity = (max_doppler_idx - self.DOPPLER_CENTER_BIN) * self.DOPPLER_RESOLUTION * (-1)
            elif max_doppler_idx == self.DOPPLER_CENTER_BIN:
                velocity = 0
            else:
                velocity = (self.DOPPLER_CENTER_BIN - max_doppler_idx) * self.DOPPLER_RESOLUTION
        
        return distance, velocity

    def update_history(self, distance, velocity, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
        
        self.distance_history.append(distance)
        self.velocity_history.append(velocity)
        self.timestamp_history.append(timestamp)
        
        # Log to CSV
        with open(self.csv_filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp.strftime('%Y-%m-%d %H:%M:%S.%f'), 
                           f"{distance:.2f}" if distance is not None else "None",
                           f"{velocity:.2f}" if velocity is not None else "None"])

    def visualize_results(self):
        plt.figure(figsize=(12, 6))
        
        # Plot distance
        plt.subplot(2, 1, 1)
        times = [(t - self.timestamp_history[0]).total_seconds() 
                for t in self.timestamp_history]
        distances = [d for d in self.distance_history if d is not None]
        plt.plot(times[-len(distances):], distances, 'b-')
        plt.ylabel('Distance (m)')
        plt.title('Object Tracking Results')
        plt.grid(True)
        
        # Plot velocity
        plt.subplot(2, 1, 2)
        velocities = [v for v in self.velocity_history if v is not None]
        plt.plot(times[-len(velocities):], velocities, 'r-')
        plt.xlabel('Time (s)')
        plt.ylabel('Velocity (m/s)')
        plt.grid(True)
        
        plt.tight_layout()
        plt.pause(0.01)

def process_doppler_dataframe(df, timestamp_column='timestamp'):
    radar_processor = MMWaveRadarProcessor()
    
    try:
        for idx, row in df.iterrows():
            doppler_data = np.array([row[f'doppler_{i}'] for i in range(radar_processor.NUM_DOPPLER_BINS)])
            doppler_data = doppler_data.reshape(radar_processor.NUM_RANGE_BINS, radar_processor.NUM_DOPPLER_BINS)
            
            distance, velocity = radar_processor.process_frame(doppler_data)
            timestamp = pd.to_datetime(row[timestamp_column]) if timestamp_column in row else datetime.now()
            
            if distance is not None and velocity is not None:
                radar_processor.update_history(distance, velocity, timestamp)
                print(f"Timestamp: {timestamp}, Distance: {distance:.2f}m, Velocity: {velocity:.2f}m/s")
                # radar_processor.visualize_results()
            else:
                print(f"Timestamp: {timestamp}, No valid detection")
            
            plt.pause(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping radar processing...")
        plt.close('all')

def main():
    df = pd.read_csv('mmwavedf.pkl')  
    process_doppler_dataframe(df['doppz'], df['datetime'])

if __name__ == "__main__":
    main()
