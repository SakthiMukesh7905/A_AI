import os
import json
import base64
import numpy as np
import cv2
import mediapipe as mp
import tensorflow as tf
from collections import deque
from typing import Dict, Any, Optional, Tuple

from backend.config import settings

mp_holistic = mp.solutions.holistic


def extract_keypoints(results) -> np.ndarray:
    """Turn one frame's MediaPipe result into a flat 258-length number array,
    matching the exact training pipeline in processs.py."""
    pose = (
        np.array([[p.x, p.y, p.z, p.visibility] for p in results.pose_landmarks.landmark]).flatten()
        if results.pose_landmarks else np.zeros(33 * 4)
    )
    left_hand = (
        np.array([[p.x, p.y, p.z] for p in results.left_hand_landmarks.landmark]).flatten()
        if results.left_hand_landmarks else np.zeros(21 * 3)
    )
    right_hand = (
        np.array([[p.x, p.y, p.z] for p in results.right_hand_landmarks.landmark]).flatten()
        if results.right_hand_landmarks else np.zeros(21 * 3)
    )
    return np.concatenate([pose, left_hand, right_hand])  # total length = 258


class SignDetector:
    def __init__(self, model_path: str = settings.MODEL_PATH, label_map_path: str = settings.LABEL_MAP_PATH):
        self.model_path = model_path
        self.label_map_path = label_map_path
        
        # Load label map
        if not os.path.exists(label_map_path):
            raise FileNotFoundError(f"Label map not found at: {label_map_path}")
        with open(label_map_path, "r") as f:
            self.label_map = json.load(f)
        
        # Reverse map: index -> label name
        self.index_to_label = {v: k for k, v in self.label_map.items()}
        self.labels = [self.index_to_label[i] for i in range(len(self.index_to_label))]
        
        print(f"[SignDetector] Loaded {len(self.labels)} classes: {self.labels}")
        
        # Load TensorFlow/Keras LSTM model
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Sign model not found at: {model_path}")
        print(f"[SignDetector] Loading LSTM model from {model_path}...")
        self.model = tf.keras.models.load_model(model_path)
        print("[SignDetector] Model loaded successfully.")
        
        # Warm-up inference
        dummy_input = np.zeros((1, settings.SEQUENCE_LENGTH, 258), dtype=np.float32)
        _ = self.model.predict(dummy_input, verbose=0)
        print("[SignDetector] Model warmup complete.")
        
        # MediaPipe Holistic instance
        self.holistic = mp_holistic.Holistic(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1
        )

    def decode_frame(self, frame_data: str) -> Optional[np.ndarray]:
        """Decode base64 JPEG/PNG string or binary bytes into BGR OpenCV image."""
        try:
            if "," in frame_data:
                frame_data = frame_data.split(",", 1)[1]
            image_bytes = base64.b64decode(frame_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            print(f"[SignDetector] Error decoding frame: {e}")
            return None

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Dict[str, bool]]:
        """Process a BGR frame through MediaPipe Holistic, returning the 258 keypoint vector."""
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.holistic.process(image)
        image.flags.writeable = True
        
        keypoints = extract_keypoints(results)
        features = {
            "pose": results.pose_landmarks is not None,
            "left_hand": results.left_hand_landmarks is not None,
            "right_hand": results.right_hand_landmarks is not None
        }
        return keypoints, features

    def predict_sequence(self, sequence: np.ndarray) -> Dict[str, Any]:
        """Run LSTM inference on a 30x258 sequence."""
        # Shape: (1, 30, 258)
        input_data = np.expand_dims(sequence, axis=0).astype(np.float32)
        probs = self.model.predict(input_data, verbose=0)[0]
        
        best_idx = int(np.argmax(probs))
        best_label = self.index_to_label.get(best_idx, "Unknown")
        confidence = float(probs[best_idx])
        
        prob_dict = {
            self.index_to_label.get(i, f"Class_{i}"): float(probs[i])
            for i in range(len(probs))
        }
        
        return {
            "label": best_label,
            "confidence": confidence,
            "probabilities": prob_dict,
            "class_index": best_idx
        }


class SessionBuffer:
    """Manages rolling 30-frame keypoints window for an active client connection."""
    def __init__(self, sequence_length: int = settings.SEQUENCE_LENGTH):
        self.sequence_length = sequence_length
        self.buffer = deque(maxlen=sequence_length)

    def add_keypoints(self, keypoints: np.ndarray) -> int:
        self.buffer.append(keypoints)
        return len(self.buffer)

    def is_ready(self) -> bool:
        return len(self.buffer) == self.sequence_length

    def get_sequence(self) -> np.ndarray:
        return np.array(list(self.buffer))

    def reset(self):
        self.buffer.clear()
