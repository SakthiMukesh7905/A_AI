
import os
import cv2
import numpy as np
import mediapipe as mp
 
# ---- CHANGE THESE TWO PATHS IF NEEDED ----
DATASET_DIR = r"D:\Agentic AI\Dataset"
OUTPUT_DIR = r"D:\Agentic AI\ProcessedData"
# -------------------------------------------
 
SEQUENCE_LENGTH = 30  # number of frames we sample from each video
 
mp_holistic = mp.solutions.holistic
 
 
def extract_keypoints(results):
    """Turn one frame's MediaPipe result into a flat number array.
    If a hand or pose is not visible, fill that part with zeros instead of crashing."""
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
 
 
def process_video(video_path, holistic):
    """Read a video, sample 30 evenly spaced frames, return their keypoints."""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        return None
 
    frame_indices = np.linspace(0, total_frames - 1, SEQUENCE_LENGTH).astype(int)
    keypoints_sequence = []
    frame_idx = 0
    pointer = 0
 
    while cap.isOpened() and pointer < len(frame_indices):
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx == frame_indices[pointer]:
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(image)
            keypoints_sequence.append(extract_keypoints(results))
            pointer += 1
        frame_idx += 1
    cap.release()
 
    # Safety net: pad with zeros if the video was too short to get 30 frames
    while len(keypoints_sequence) < SEQUENCE_LENGTH:
        keypoints_sequence.append(np.zeros(258))
 
    return np.array(keypoints_sequence)
 
 
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    labels = sorted([
        d for d in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, d))
    ])
    print("Found sign labels:", labels)
 
    with mp_holistic.Holistic(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as holistic:
 
        for label in labels:
            label_path = os.path.join(DATASET_DIR, label)
            save_dir = os.path.join(OUTPUT_DIR, label)
            os.makedirs(save_dir, exist_ok=True)
 
            videos = [f for f in os.listdir(label_path) if f.lower().endswith(".mp4")]
            print(f"\nProcessing '{label}' — {len(videos)} clips")
 
            for i, video_file in enumerate(videos):
                video_path = os.path.join(label_path, video_file)
                sequence = process_video(video_path, holistic)
                if sequence is None:
                    print(f"  Skipped (unreadable): {video_file}")
                    continue
                save_path = os.path.join(save_dir, f"{i}.npy")
                np.save(save_path, sequence)
                print(f"  Saved {save_path}  shape={sequence.shape}")
 
    print("\nDone. Landmarks saved in:", OUTPUT_DIR)
 
 
if __name__ == "__main__":
    main()