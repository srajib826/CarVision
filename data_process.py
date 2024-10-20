import pandas as pd 
import numpy as np
import sys
import pickle

FRAME_STACK = int(sys.argv[1])

fd3 = pd.read_pickle('dataset.pickle')

def StackFrames(data, labels, frame_stack=None):
    max_index = data.shape[0] - frame_stack
    stacked_data = np.array([data[i:i + frame_stack] for i in range(max_index)])
    new_labels = np.array([labels[i:i + frame_stack] for i in range(max_index)]).reshape(-1,frame_stack)
    return stacked_data, new_labels

data_dop = np.array(fd3['doppz'].values.tolist())
data_azim = np.array(fd3['azimuthz'].values.tolist())
data_azim[data_azim==None]=0
print(data_dop.shape, data_azim.shape)
data_dop = data_dop.astype(dtype=np.float32)
data_azim = data_azim.astype(dtype=np.float32)
label = fd3['rel_speed_obd'].values.reshape(-1,1)
data_dop, label_dop = StackFrames(data_dop, label,frame_stack=FRAME_STACK)
data_azim, label_azim = StackFrames(data_azim, label,frame_stack=FRAME_STACK)
split_len = np.ceil(len(data_dop)*0.9).astype(np.int32)
X_train_dop, X_test_dop = data_dop[:split_len,:,:], data_dop[split_len:,:,:]
print(X_train_dop.shape, X_test_dop.shape)
X_train_azim, X_test_azim = data_azim[:split_len,:,:], data_azim[split_len:,:,:]
print(X_train_azim.shape, X_test_azim.shape)
y_train_dop, y_test_dop = label_dop[:split_len], label_dop[split_len:] 
print(f"after frame stacking X_train_dop: {X_train_dop.shape}, X_test_dop: {X_test_dop.shape}")
print(f"shape of y_train_dop: {y_train_dop.shape}, y_test_dop: {y_test_dop.shape}")


maxx=X_train_dop.max();minn=X_train_dop.min()
X_train_dop=(X_train_dop-minn)/(maxx-minn)
X_test_dop=(X_test_dop-minn)/(maxx-minn)

maxx=X_train_azim.max();minn=X_train_azim.min()
X_train_azim=(X_train_azim-minn)/(maxx-minn)
X_test_azim=(X_test_azim-minn)/(maxx-minn)

maxx=y_train_dop.max();minn=y_train_dop.min()
y_train=((y_train_dop-minn)/(maxx-minn))*100
y_test=((y_test_dop-minn)/(maxx-minn))*100

X_train_dop=X_train_dop.transpose(0,2,3,1)
X_test_dop=X_test_dop.transpose(0,2,3,1)
X_train_azim=X_train_azim.transpose(0,2,3,1)
X_test_azim=X_test_azim.transpose(0,2,3,1)


with open("processed_dataset.pkl", "wb") as f:
    pickle.dump((X_train_dop, X_train_azim, X_test_dop, X_test_azim, y_train, y_test), f)
