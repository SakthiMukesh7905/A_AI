import React, { useRef, useEffect, useState } from 'react';
import { Camera, CameraOff, Play, Square, Cpu, Eye } from 'lucide-react';

export default function CameraFeed({
  isMonitoring,
  onStartMonitoring,
  onStopMonitoring,
  wsConnected,
  sendFrame,
  bufferProgress,
  featuresDetected,
  cooldownActive
}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  
  const [fps, setFps] = useState(0);
  const frameCountRef = useRef(0);
  const lastFpsTimeRef = useRef(Date.now());

  // Handle Start & Stop Monitoring
  useEffect(() => {
    let active = true;

    async function startWebcam() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            frameRate: { ideal: 20 }
          },
          audio: false
        });

        if (!active) {
          stream.getTracks().forEach(track => track.stop());
          return;
        }

        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play().catch(err => console.error("Video play error:", err));
        }

        // Start frame capture loop at ~15 FPS (66ms interval)
        intervalRef.current = setInterval(() => {
          if (!videoRef.current || !canvasRef.current || !wsConnected) return;

          const video = videoRef.current;
          const canvas = canvasRef.current;
          
          if (video.readyState < 2) return; // HAVE_CURRENT_DATA

          const ctx = canvas.getContext('2d');
          canvas.width = 320; // 320x240 is optimal for fast MediaPipe real-time inference
          canvas.height = 240;
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

          const frameBase64 = canvas.toDataURL('image/jpeg', 0.6);
          sendFrame(frameBase64);

          // Calculate FPS
          frameCountRef.current++;
          const now = Date.now();
          if (now - lastFpsTimeRef.current >= 1000) {
            setFps(frameCountRef.current);
            frameCountRef.current = 0;
            lastFpsTimeRef.current = now;
          }
        }, 66);

      } catch (err) {
        console.error("Failed to access webcam:", err);
        alert("Camera Access Error: " + err.message + ". Please ensure camera permissions are allowed.");
        onStopMonitoring();
      }
    }

    if (isMonitoring) {
      startWebcam();
    } else {
      // Clean up camera stream and interval
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
      setFps(0);
    }

    return () => {
      active = false;
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [isMonitoring, wsConnected, sendFrame, onStopMonitoring]);

  return (
    <div className="glass-panel camera-card">
      <div className="camera-header">
        <div className="section-title">
          <Eye size={20} color="var(--alert-red-600)" />
          <span>Real-Time Camera Stream</span>
        </div>
        {isMonitoring && (
          <div className="hud-pill">
            <Cpu size={12} color="var(--emerald-500)" />
            <span>{fps} FPS | Buffer: {bufferProgress}/30</span>
          </div>
        )}
      </div>

      <div className="video-container">
        {/* Hidden Canvas for Frame Downsampling & Base64 Encoding */}
        <canvas ref={canvasRef} style={{ display: 'none' }} />

        {isMonitoring ? (
          <>
            <video 
              ref={videoRef} 
              className="video-element" 
              autoPlay 
              playsInline 
              muted 
            />
            {/* Real-time HUD and visual scan overlay */}
            <div className="hud-overlay">
              <div className="hud-top">
                <div className="hud-pill">
                  <span className="status-dot pulse" style={{ color: 'var(--alert-red-500)' }} />
                  <span>LIVE ISL RECOGNITION</span>
                </div>
                <div className="hud-pill">
                  <span>Pose: {featuresDetected?.pose ? '✓' : '—'}</span>
                  <span style={{ margin: '0 2px' }}>|</span>
                  <span>Hands: {featuresDetected?.left_hand || featuresDetected?.right_hand ? '✓' : '—'}</span>
                </div>
              </div>
              <div className="hud-scanner" />
            </div>
          </>
        ) : (
          <div className="camera-idle-placeholder">
            <div className="camera-idle-icon">
              <CameraOff size={28} />
            </div>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#EFE8DE' }}>Camera Stream Paused</h3>
              <p style={{ fontSize: '0.78rem', color: '#9E928A', marginTop: '4px' }}>
                Click "Start Monitoring" to activate the camera and real-time ISL emergency recognition.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Primary Control Buttons */}
      <div className="camera-controls-bar">
        {!isMonitoring ? (
          <button 
            id="start-monitoring-btn"
            className="btn-primary-start" 
            onClick={onStartMonitoring}
            disabled={!wsConnected}
          >
            <Play size={18} />
            <span>Start Monitoring</span>
          </button>
        ) : (
          <button 
            id="stop-monitoring-btn"
            className="btn-primary-stop" 
            onClick={onStopMonitoring}
          >
            <Square size={16} fill="currentColor" />
            <span>Stop Monitoring</span>
          </button>
        )}
      </div>
    </div>
  );
}
