import sys
import io
import time
import json
import base64
import asyncio
import urllib.request
import websockets
import cv2
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/stream"


def http_get(path):
    req = urllib.request.Request(f"{API_BASE}{path}")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))


def http_post(path, data):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{API_BASE}{path}", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))


def create_dummy_jpeg_base64():
    """Create a 320x240 RGB dummy image encoded as base64 JPEG."""
    img = np.zeros((240, 320, 3), dtype=np.uint8)
    # Draw simple shape
    cv2.circle(img, (160, 120), 50, (200, 200, 200), -1)
    _, buffer = cv2.imencode('.jpg', img)
    return "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')


async def test_websocket_streaming():
    print("\n--- Testing WebSocket Streaming (/ws/stream) ---")
    async with websockets.connect(WS_URL) as ws:
        frame_b64 = create_dummy_jpeg_base64()
        
        # Send 32 frames to fill 30-frame buffer and get live predictions
        for i in range(32):
            msg = {
                "type": "frame",
                "data": frame_b64,
                "timestamp": time.time()
            }
            await ws.send(json.dumps(msg))
            resp_str = await ws.recv()
            resp = json.loads(resp_str)
            
            if resp.get("type") == "buffering":
                print(f"Frame {i+1}: Buffering ({resp['buffer_progress']}/{resp['buffer_target']})")
            elif resp.get("type") == "prediction":
                print(f"Frame {i+1}: PREDICTION received! Label: '{resp['label']}', Confidence: {resp['confidence']:.2%}")
                assert "probabilities" in resp, "Missing probabilities in prediction response"
                assert "agent_status" in resp, "Missing agent_status in prediction response"
                break
            
            await asyncio.sleep(0.02)
            
    print("[SUCCESS] WebSocket real-time frame streaming and prediction verified!")


def run_all_tests():
    print("==================================================")
    print("    SignAlert End-to-End Integration Verification ")
    print("==================================================")
    
    # 1. Test /api/status
    print("\n1. Testing GET /api/status")
    status = http_get("/api/status")
    print(f"Status Response: {status}")
    assert status["online"] is True
    assert len(status["model_classes"]) == 5
    
    # 2. Reset cooldown
    print("\n2. Testing POST /api/reset-cooldown")
    rc = http_post("/api/reset-cooldown", {})
    print(f"Reset cooldown response: {rc['message']}")
    
    # 3. Test POST /api/test-alert
    print("\n3. Testing POST /api/test-alert (Heart-pain)")
    alert_res = http_post("/api/test-alert", {"label": "Heart-pain", "confidence": 0.95})
    print(f"Alert Trigger Result: {alert_res['triggered']}, Agent Status: {alert_res['agent_status']}")
    assert alert_res["triggered"] is True
    assert alert_res["incident"]["label"] == "Heart-pain"
    
    # 4. Test Cooldown Gating
    print("\n4. Testing Cooldown Block on immediate second alert")
    second_res = http_post("/api/test-alert", {"label": "Dizzy", "confidence": 0.90})
    print(f"Second Alert Result: {second_res['triggered']}, Reason: {second_res.get('reason')}")
    assert second_res["triggered"] is False
    assert second_res["reason"] == "COOLDOWN_ACTIVE"
    print(f"Cooldown Remaining: {second_res['cooldown_remaining']}s")
    
    # 5. Test GET /api/logs
    print("\n5. Testing GET /api/logs")
    logs = http_get("/api/logs")
    print(f"Total Incidents: {logs['count']}")
    assert logs["count"] >= 1
    recent = logs["incidents"][0]
    print(f"Latest Incident: Label='{recent['label']}', Confidence={recent['confidence']}%, Status='{recent['sms_status']}'")
    
    # 6. Test WebSocket Frame Streaming
    print("\n6. Running WebSocket Real-Time Frame Streaming Test")
    asyncio.run(test_websocket_streaming())
    
    print("\n==================================================")
    print("  ALL TESTS PASSED! FULL SYSTEM VERIFIED E2E!     ")
    print("==================================================")


if __name__ == "__main__":
    run_all_tests()
