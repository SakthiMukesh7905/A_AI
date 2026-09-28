import sys
import io
import asyncio
import numpy as np

# Force UTF-8 stdout for Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.config import settings
from backend.detector import SignDetector, SessionBuffer
from backend.agent import agent

def test_pipeline():
    print("=== Testing SignAlert Backend Pipeline ===")
    print(f"Model path: {settings.MODEL_PATH}")
    print(f"Label map path: {settings.LABEL_MAP_PATH}")
    
    # 1. Test Detector initialization
    detector = SignDetector()
    print(f"Detector classes: {detector.labels}")
    assert len(detector.labels) == 5, f"Expected 5 classes, got {len(detector.labels)}"
    
    # 2. Test SessionBuffer
    buffer = SessionBuffer(30)
    assert not buffer.is_ready()
    
    # 3. Simulate 30 keypoint frames
    for i in range(30):
        dummy_kp = np.random.rand(258).astype(np.float32)
        count = buffer.add_keypoints(dummy_kp)
    
    assert buffer.is_ready()
    seq = buffer.get_sequence()
    assert seq.shape == (30, 258)
    print(f"Buffer shape verified: {seq.shape}")
    
    # 4. Test Model Prediction
    pred = detector.predict_sequence(seq)
    print(f"Prediction result: {pred}")
    assert "label" in pred
    assert "confidence" in pred
    assert "probabilities" in pred
    assert len(pred["probabilities"]) == 5
    
    # 5. Test Agent Dispatcher & Cooldown
    print("\n=== Testing Agent Cooldown Logic ===")
    agent.reset_cooldown()
    assert not agent.is_in_cooldown()
    
    # Trigger first alert
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    res1 = loop.run_until_complete(agent.trigger_emergency_action("Heart-pain", 0.95, "Unit Test"))
    print(f"First trigger result: {res1['triggered']}, Agent status: {res1['agent_status']}")
    assert res1["triggered"] is True
    assert agent.is_in_cooldown() is True
    
    # Trigger second alert immediately during cooldown (must be blocked)
    res2 = loop.run_until_complete(agent.trigger_emergency_action("Dizzy", 0.92, "Unit Test 2"))
    print(f"Second trigger result during cooldown: {res2['triggered']}, Reason: {res2['reason']}")
    assert res2["triggered"] is False
    assert res2["reason"] == "COOLDOWN_ACTIVE"
    print(f"Cooldown remaining: {agent.get_cooldown_remaining()}s")
    
    print("\n[SUCCESS] All backend components verified successfully!")

if __name__ == "__main__":
    test_pipeline()
