
import os
import json
import importlib
import numpy as np
from sklearn.model_selection import train_test_split

try:
    keras_models = importlib.import_module("tensorflow.keras.models")
    keras_layers = importlib.import_module("tensorflow.keras.layers")
    keras_utils = importlib.import_module("tensorflow.keras.utils")
    keras_callbacks = importlib.import_module("tensorflow.keras.callbacks")
except ModuleNotFoundError:
    try:
        keras_models = importlib.import_module("keras.models")
        keras_layers = importlib.import_module("keras.layers")
        keras_utils = importlib.import_module("keras.utils")
        keras_callbacks = importlib.import_module("keras.callbacks")
    except ModuleNotFoundError as exc:
        raise ImportError(
            "TensorFlow/Keras is required to run this training script. "
            "Install it with: pip install tensorflow"
        ) from exc

Sequential = keras_models.Sequential
LSTM = keras_layers.LSTM
Dense = keras_layers.Dense
Dropout = keras_layers.Dropout
to_categorical = keras_utils.to_categorical
EarlyStopping = keras_callbacks.EarlyStopping
 
# ---- CHANGE THESE PATHS IF NEEDED ----
DATA_DIR = r"D:\Agentic AI\ProcessedData"
MODEL_SAVE_PATH = r"D:\Agentic AI\sign_model.h5"
LABEL_MAP_PATH = r"D:\Agentic AI\label_map.json"
# ----------------------------------------
 
# 1. Load all the .npy files into one big array
labels = sorted(os.listdir(DATA_DIR))
label_map = {label: idx for idx, label in enumerate(labels)}
print("Label map:", label_map)
 
X, y = [], []
for label in labels:
    label_dir = os.path.join(DATA_DIR, label)
    for file in os.listdir(label_dir):
        if file.endswith(".npy"):
            sequence = np.load(os.path.join(label_dir, file))
            X.append(sequence)
            y.append(label_map[label])
 
X = np.array(X)                       # shape: (num_clips, 30, 258)
y = to_categorical(y).astype(int)     # one-hot labels
 
print("X shape:", X.shape)
print("y shape:", y.shape)
 
# 2. Split into train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
 
# 3. Build a small LSTM model
model = Sequential([
    LSTM(64, return_sequences=True, activation='relu', input_shape=(X.shape[1], X.shape[2])),
    Dropout(0.3),
    LSTM(128, return_sequences=False, activation='relu'),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dense(len(labels), activation='softmax'),
])
 
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
model.summary()
 
# 4. Train (stops automatically once it stops improving, so it won't overfit forever)
early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True)
 
model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=200,
    batch_size=8,
    callbacks=[early_stop],
)
 
# 5. Check final accuracy
loss, acc = model.evaluate(X_test, y_test)
print(f"\nFinal Test Accuracy: {acc * 100:.2f}%")
 
# 6. Save the model and label map
model.save(MODEL_SAVE_PATH)
with open(LABEL_MAP_PATH, "w") as f:
    json.dump(label_map, f)
 
print(f"\nModel saved to: {MODEL_SAVE_PATH}")
print(f"Label map saved to: {LABEL_MAP_PATH}")