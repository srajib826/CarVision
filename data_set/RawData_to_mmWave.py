import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime, timedelta
import csv

# ground_df = pd.read_csv("/home/rajib/millivelo/obd_data/ground_truth_df.csv")
# print(ground_df.head())
# ground_df = ground_df[['timestamp', 'value_x', 'value_y', 'distance']]

mmwave_files = glob.glob('/home/rajib/millivelo/millivelo_mmwaveData/day_4_mmwave_data/*.txt')



def process_mmwave(f):
    print(f'starting file {f}')	
    data = [json.loads(val) for val in open(f, "r")]
    mmwave_df = pd.DataFrame()
    
    for d in data:
        mmwave_df = mmwave_df._append(d['answer'], ignore_index=True)
    
    datetime_str = data[0]['answer']['datenow'].split("/")[-1]+"-"+str("0")+str(int(data[0]['answer']['datenow'].split("/")[1])+1)+"-"+data[0]['answer']['datenow'].split("/")[0]
    mmwave_df['datetime'] = mmwave_df['timenow'].apply(lambda e: datetime_str+' ' + ':'.join(e.split('_')))
   
    skip_row = []
    for i, row in mmwave_df.iterrows():
        row['doppz'] = np.array(row['doppz'])
        if row['doppz'].shape != (16,256):
            skip_row.append(i)
            # print(f'need to skip: {i}')
    
    mmwave_df = mmwave_df.drop(skip_row)
    mmwave_df.reset_index(drop=True, inplace=True)  
    try:
        mmwave_df['doppz'] = list(np.array(mmwave_df['doppz'].values.tolist()))
        mmwave_df['azimuthz'] = list(np.array(mmwave_df['azimuthz'].values.tolist()))
        print("Correct: ", mmwave_df['doppz'].values.shape)
    except:
        print("Error: ", mmwave_df['doppz'].values.shape)
    mmwave_df = mmwave_df[['datetime', 'doppz', 'azimuthz']]
    
    return mmwave_df


mmwave_df = pd.concat([process_mmwave(f) for f in mmwave_files], ignore_index=True)



# mmwave_df['datetime'] = pd.to_datetime(mmwave_df['datetime'])
# mmwave_df.sort_values(by = 'datetime', inplace = True)
# print(mmwave_df['datetime'].min())
# print(mmwave_df['datetime'].max())
# mmwave_df.to_pickle("mmwave_data_day4.pkl")


