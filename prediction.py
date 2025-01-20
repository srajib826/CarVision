import pickle
from model import combined_model, FRAME_STACK

with open("processed_dataset.pkl", "rb") as f:
    X_train_dop, X_train_azim, X_test_dop, X_test_azim, y_train, y_test = pickle.load(f)

model = combined_model(FRAME_STACK)
model.load_weights("model.h5")  
predictions = model.predict([X_test_dop, X_test_azim])

for i, pred in enumerate(predictions[:10]): 
    print(f"Sample {i+1}: Predicted Speed = {pred}")