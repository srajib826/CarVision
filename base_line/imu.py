import glob
import pandas as pd
from io import StringIO
from timr import timedelta

class IMUProcessor:
    def __init__(self, input_dir, ego_vehicle_file):
        self.input_dir = input_dir
        self.ego_vehicle_file = ego_vehicle_file

    def process_front_vehicle_imu(self, file):
        txt_data_str = ''.join(open(file, 'r').readlines())
        data_io = StringIO(txt_data_str)
        df = pd.read_csv(data_io, delimiter='\t')
        df['TStamp Asia/Kolkata'] = pd.to_datetime(df['TStamp Asia/Kolkata'], unit='ms')
        df['TStamp Asia/Kolkata'] = df['TStamp Asia/Kolkata'].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
        df['TStamp Asia/Kolkata'] = df['TStamp Asia/Kolkata'].dt.strftime('%Y-%m-%d %H:%M:%S')
        return df

    def load_front_vehicle_data(self):
        files = glob.glob(f"{self.input_dir}/*.txt")
        imu_df_front = pd.concat([self.process_front_vehicle_imu(file) for file in files])
        imu_df_front = imu_df_front[['TStamp Asia/Kolkata', 'X [m/s\u00b2]']]
        imu_df_front = imu_df_front.dropna()
        imu_df_front['Timestamp'] = pd.to_datetime(imu_df_front['TStamp Asia/Kolkata'])
        imu_df_front = imu_df_front.sort_values(by='Timestamp').reset_index(drop=True)
        imu_df_front = imu_df_front[['Timestamp', 'X [m/s\u00b2]']]
        imu_df_front.columns = ['Timestamp', 'Ax (g)']
        return imu_df_front

    def distribute_timestamps(group, flag='Front'):
        n = len(group)
        interval = 1000 / n 
        interval_s = interval / 1000  
        
        if 'Timestamp' not in group.columns:
            print("Timestamp column missing in group:")
            print(group)
            return group  
        
        
        new_timestamps = [group['Timestamp'].iloc[0] + timedelta(milliseconds=i*interval) for i in range(n)]
        
        new_velocity = [0] * n
        new_distance = [0] * n
        
       
        for i in range(1, n):

            if flag!='Front':
                acceleration_m_s2 = group['Ax (g)'].iloc[i] * 9.81
            else:
                acceleration_m_s2 = group['Ax (g)'].iloc[i]
            new_velocity[i] = new_velocity[i-1] + (acceleration_m_s2 * interval_s)
            new_distance[i] = new_distance[i-1] + (new_velocity[i] * interval_s)
        
        group['Timestamp'] = new_timestamps
        group['distance'] = new_distance
        group['velocity'] = new_velocity
        return group

    def merge_imu_data(self, imu_df_front):
        imu_df_front = imu_df_front.groupby('Timestamp', group_keys=False).apply(self.distribute_timestamps)
        imu_ego_vehicle = pd.read_csv(self.ego_vehicle_file)
        imu_ego_vehicle['Timestamp'] = pd.to_datetime(imu_ego_vehicle['Timestamp'])
        merged_imu_df = pd.merge_asof(
            imu_ego_vehicle.sort_values('Timestamp'),
            imu_df_front.sort_values('Timestamp'),
            on='Timestamp',
            direction='nearest'
        )
        merged_imu_df['rel_speed'] = abs(merged_imu_df['velocity_y'] - merged_imu_df['velocity_x'])
        merged_imu_df['time_gap'] = merged_imu_df['Timestamp'].diff().dt.total_seconds()
        merged_imu_df['rel_dist'] = abs(merged_imu_df['rel_speed']) * merged_imu_df['time_gap']
        merged_imu_df = merged_imu_df[['Timestamp', 'rel_speed', 'rel_dist']]
        return merged_imu_df

    def process(self):
        imu_df_front = self.load_front_vehicle_data()
        merged_imu_df = self.merge_imu_data(imu_df_front)
        return merged_imu_df

# Example usage
if __name__ == "__main__":
    input_directory = "/home/rajib/millivelo/imu"
    ego_vehicle_file = "ego_vehicle_data.csv"  

    imu_processor = IMUProcessor(input_directory, ego_vehicle_file)
    processed_data = imu_processor.process()
    print(processed_data)
