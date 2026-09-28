import time
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import cv2
import mediapipe as mp
import numpy as np

from backend.config import settings
from backend.detector import SignDetector, SessionBuffer, extract_keypoints, mp_holistic
from backend.agent import agent
from backend.evaluate_agent import get_or_run_cached_benchmark, run_agent_benchmark

app = FastAPI(
    title="SignAlert API",
    description="Real-time ISL Medical Emergency Recognition and Autonomous Caregiver Dispatch System",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite runs on port 5173 by default)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Global Shared Model Detector
print("[Main] Initializing SignDetector...")
sign_detector = SignDetector()
print("[Main] SignDetector initialized successfully.")


# Pydantic Schemas for REST API
class ConfigUpdateRequest(BaseModel):
    caregiver_phone: Optional[str] = None
    secondary_caregiver_phone: Optional[str] = None
    confidence_threshold: Optional[float] = Field(default=None, ge=0.1, le=1.0)
    cooldown_seconds: Optional[int] = Field(default=None, ge=5, le=300)
    call_timeout_seconds: Optional[int] = Field(default=None, ge=5, le=60)

class TestAlertRequest(BaseModel):
    label: str = "Heart-pain"
    confidence: float = 0.95


@app.get("/")
def root():
    return {
        "app": "SignAlert",
        "status": "online",
        "classes": sign_detector.labels,
        "cooldown_seconds": settings.COOLDOWN_SECONDS,
        "threshold": settings.CONFIDENCE_THRESHOLD,
        "primary_caregiver": settings.CAREGIVER_PHONE_NUMBER,
        "secondary_caregiver": settings.SECONDARY_CAREGIVER_PHONE_NUMBER
    }


@app.get("/api/status")
def get_status():
    """Return backend status, model info, agent state, escalation status, and cooldown."""
    agent_info = agent.get_status()
    return {
        "online": True,
        "model_classes": sign_detector.labels,
        "sequence_length": settings.SEQUENCE_LENGTH,
        "agent": agent_info
    }


@app.get("/api/logs")
def get_incident_logs():
    """Return recent emergency incident logs."""
    return {
        "incidents": agent.incident_history,
        "count": len(agent.incident_history)
    }


@app.post("/api/test-alert")
async def trigger_test_alert(req: TestAlertRequest):
    """Trigger a simulated or live emergency alert directly for evaluation/testing."""
    if req.label not in sign_detector.labels:
        raise HTTPException(status_code=400, detail=f"Invalid label. Must be one of {sign_detector.labels}")
    
    result = await agent.trigger_emergency_action(
        label=req.label,
        confidence=req.confidence,
        source="Manual Evaluation Demo"
    )
    return result


@app.post("/api/reset-cooldown")
def reset_cooldown():
    """Reset the 30-second cooldown immediately."""
    agent.reset_cooldown()
    return {"message": "Cooldown reset successfully", "agent_status": agent.get_status()}


@app.post("/api/config")
def update_config(req: ConfigUpdateRequest):
    """Update runtime configuration."""
    agent.update_config(
        caregiver_phone=req.caregiver_phone,
        secondary_caregiver_phone=req.secondary_caregiver_phone,
        threshold=req.confidence_threshold,
        cooldown=req.cooldown_seconds,
        call_timeout=req.call_timeout_seconds
    )
    return {
        "message": "Config updated successfully",
        "config": {
            "caregiver_phone": settings.CAREGIVER_PHONE_NUMBER,
            "secondary_caregiver_phone": settings.SECONDARY_CAREGIVER_PHONE_NUMBER,
            "confidence_threshold": agent.confidence_threshold,
            "cooldown_seconds": agent.cooldown_seconds,
            "call_timeout_seconds": settings.CALL_TIMEOUT_SECONDS
        }
    }


@app.get("/api/agent-metrics")
async def get_agent_metrics():
    """Return latest agentic evaluation metrics based on arXiv:2602.22953v2 Section 3.3."""
    metrics = await get_or_run_cached_benchmark()
    return metrics


@app.post("/api/agent-metrics/run")
async def execute_agent_metrics_run():
    """Trigger a live agent evaluation run (50 episodes) and return updated metrics."""
    metrics = await get_or_run_cached_benchmark(force_refresh=True)
    return metrics


@app.websocket("/ws/stream")
async def websocket_stream_endpoint(websocket: WebSocket):
    """Real-time WebSocket endpoint for continuous frame streaming and live prediction."""
    await websocket.accept()
    print("[WebSocket] Client connected for live sign monitoring.")
    
    session_buffer = SessionBuffer(sequence_length=settings.SEQUENCE_LENGTH)
    
    # Per-connection MediaPipe Holistic instance for thread-safety and smooth processing
    holistic_instance = mp_holistic.Holistic(
        static_image_mode=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=1
    )
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "frame")
            
            if msg_type == "reset":
                session_buffer.reset()
                await websocket.send_json({
                    "type": "buffer_reset",
                    "buffer_progress": 0,
                    "agent_status": agent.get_status()
                })
                continue
                
            if msg_type == "ping":
                await websocket.send_json({"type": "pong", "time": time.time()})
                continue
                
            if msg_type == "frame":
                frame_data = data.get("data")
                if not frame_data:
                    continue
                
                # Decode BGR image
                frame = sign_detector.decode_frame(frame_data)
                if frame is None:
                    continue
                
                # MediaPipe Holistic keypoint extraction
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_rgb.flags.writeable = False
                results = holistic_instance.process(image_rgb)
                image_rgb.flags.writeable = True
                
                keypoints = extract_keypoints(results)
                features = {
                    "pose": results.pose_landmarks is not None,
                    "left_hand": results.left_hand_landmarks is not None,
                    "right_hand": results.right_hand_landmarks is not None
                }
                
                # Push into rolling buffer
                buf_len = session_buffer.add_keypoints(keypoints)
                
                if buf_len < settings.SEQUENCE_LENGTH:
                    # Still buffering initial 30 frames
                    await websocket.send_json({
                        "type": "buffering",
                        "buffer_progress": buf_len,
                        "buffer_target": settings.SEQUENCE_LENGTH,
                        "features": features,
                        "agent_status": agent.get_status()
                    })
                else:
                    # Buffer has 30 frames: run inference
                    sequence = session_buffer.get_sequence()
                    pred = sign_detector.predict_sequence(sequence)
                    
                    label = pred["label"]
                    confidence = pred["confidence"]
                    probabilities = pred["probabilities"]
                    
                    # Check agent trigger condition
                    alert_result = None
                    if agent.can_trigger(label, confidence):
                        alert_result = await agent.trigger_emergency_action(
                            label=label,
                            confidence=confidence,
                            source="Live Camera Detection"
                        )
                    
                    await websocket.send_json({
                        "type": "prediction",
                        "label": label,
                        "confidence": confidence,
                        "probabilities": probabilities,
                        "buffer_progress": settings.SEQUENCE_LENGTH,
                        "features": features,
                        "agent_status": agent.get_status(),
                        "alert_triggered": alert_result is not None and alert_result.get("triggered", False),
                        "incident": alert_result.get("incident") if alert_result else None,
                        "timestamp": time.time()
                    })
                    
    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected from monitoring stream.")
    except Exception as e:
        print(f"[WebSocket] Error during session: {e}")
    finally:
        holistic_instance.close()
        session_buffer.reset()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
