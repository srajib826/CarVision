import numpy as np
from sklearn.cluster import DBSCAN
from datetime import datetime
import matplotlib.pyplot as plt

def parse_lidar_data(data_str):
    items = data_str.replace("'", "").split(", ")
    timestamp = items[0].split(": ")[1]
    timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    measurements = {}
    for item in items[1:]:
        angle, distance = item.split(": ")
        measurements[int(angle)] = float(distance)
    
    return timestamp, measurements

def polar_to_cartesian(angle, distance):
    angle_rad = np.radians(angle)
    x = distance * np.cos(angle_rad)
    y = distance * np.sin(angle_rad)
    return x, y

def process_lidar_scan(measurements):
    points = []
    angles = []
    distances = []
    
    for angle, distance in measurements.items():
        if distance > 0:  
            x, y = polar_to_cartesian(angle, distance)
            points.append([x, y])
            angles.append(angle)
            distances.append(distance)
    
    return np.array(points), np.array(angles), np.array(distances)

def cluster_points(points, eps=500, min_samples=5):
    if len(points) == 0:
        return None, None
    
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    clusters = dbscan.fit_predict(points)
    return clusters

class LidarTracker:
    def __init__(self):
        self.previous_time = None
        self.previous_center = None
        self.previous_distance = None
        self.velocities = []
        self.timestamps = []
        self.distances = []
    
    def get_largest_cluster_info(self, points, clusters):
        if clusters is None or len(points) == 0:
            return None, None
        
        unique_clusters = np.unique(clusters)
        largest_cluster_size = 0
        largest_cluster_center = None
        largest_cluster_distance = None
        
        for cluster_id in unique_clusters:
            if cluster_id == -1:  
                continue
                
            cluster_points = points[clusters == cluster_id]
            if len(cluster_points) > largest_cluster_size:
                largest_cluster_size = len(cluster_points)
                largest_cluster_center = np.mean(cluster_points, axis=0)
                largest_cluster_distance = np.sqrt(np.sum(largest_cluster_center**2))
        
        return largest_cluster_center, largest_cluster_distance
    
    def update(self, timestamp, points, clusters):
        center, distance = self.get_largest_cluster_info(points, clusters)
        
        if center is not None:
            self.distances.append(distance)
            self.timestamps.append(timestamp)
            if self.previous_center is not None and self.previous_time is not None:
                time_diff = (timestamp - self.previous_time).total_seconds()
                if time_diff > 0:
                    displacement = np.sqrt(np.sum((center - self.previous_center)**2))
                    velocity = displacement / time_diff 
                    self.velocities.append(velocity)
            
    
            self.previous_center = center
            self.previous_time = timestamp
            self.previous_distance = distance
    
    def get_latest_values(self):
        latest_velocity = self.velocities[-1] if self.velocities else None
        latest_distance = self.distances[-1] if self.distances else None
        return latest_velocity, latest_distance

def visualize_tracking(tracker):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    timestamps = [t.timestamp() for t in tracker.timestamps]
    ax1.plot(timestamps, tracker.distances, 'b-')
    ax1.set_ylabel('Distance (mm)')
    ax1.set_title('Largest Cluster Distance Over Time')
    ax1.grid(True)
    
    if tracker.velocities:
        timestamps = timestamps[1:]  
        ax2.plot(timestamps, tracker.velocities, 'r-')
        ax2.set_ylabel('Velocity (mm/s)')
        ax2.set_xlabel('Time (s)')
        ax2.set_title('Largest Cluster Velocity Over Time')
        ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

def process_lidar_data(data_str, tracker=None):
    if tracker is None:
        tracker = LidarTracker()
    timestamp, measurements = parse_lidar_data(data_str)
    points, angles, distances = process_lidar_scan(measurements)
    clusters = cluster_points(points)
    tracker.update(timestamp, points, clusters)
    velocity, distance = tracker.get_latest_values()
    
    return {
        'timestamp': timestamp,
        'velocity': velocity,
        'distance': distance,
        'tracker': tracker
    }
def process_multiple_scans(data_list):
    tracker = LidarTracker()
    results = []
    
    for data_str in data_list:
        result = process_lidar_data(data_str, tracker)
        results.append(result)
        
        print(f"Timestamp: {result['timestamp']}")
        print(f"Distance to largest cluster: {result['distance']:.2f} mm")
        if result['velocity'] is not None:
            print(f"Velocity of largest cluster: {result['velocity']:.2f} mm/s")
        print("---")
    
    visualize_tracking(tracker)
    
    return results
