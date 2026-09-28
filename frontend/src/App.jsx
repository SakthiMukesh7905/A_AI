import React, { useState, useEffect, useRef, useCallback } from 'react';
import confetti from 'canvas-confetti';

import Header from './components/Header';
import CameraFeed from './components/CameraFeed';
import PredictionBadge from './components/PredictionBadge';
import AgentActionPanel from './components/AgentActionPanel';
import QuickTestBar from './components/QuickTestBar';
import SettingsModal from './components/SettingsModal';
import AgentEvaluationModal from './components/AgentEvaluationModal';

const API_BASE = "http://localhost:8000";
const WS_URL = "ws://localhost:8000/ws/stream";

export default function App() {
  const [wsConnected, setWsConnected] = useState(false);
  const [isMonitoring, setIsMonitoring] = useState(false);
  
  // Real-time Prediction State
  const [prediction, setPrediction] = useState(null);
  const [bufferProgress, setBufferProgress] = useState(0);
  const [featuresDetected, setFeaturesDetected] = useState({ pose: false, left_hand: false, right_hand: false });
  
  // Agent & Cooldown State
  const [agentStatus, setAgentStatus] = useState({
    state: "IDLE",
    status_text: "Standby",
    cooldown_active: false,
    cooldown_remaining: 0,
    cooldown_total: 30,
    caregiver_phone: "+1234567890",
    confidence_threshold: 0.70,
    twilio_configured: false,
    voice_call_enabled: true
  });
  
  const [incidents, setIncidents] = useState([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isEvaluationOpen, setIsEvaluationOpen] = useState(false);

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Fetch initial status and logs from REST API
  const fetchStatusAndLogs = useCallback(async () => {
    try {
      const [statusRes, logsRes] = await Promise.all([
        fetch(`${API_BASE}/api/status`),
        fetch(`${API_BASE}/api/logs`)
      ]);
      
      if (statusRes.ok) {
        const data = await statusRes.json();
        if (data.agent) setAgentStatus(data.agent);
      }
      
      if (logsRes.ok) {
        const data = await logsRes.json();
        if (data.incidents) setIncidents(data.incidents);
      }
    } catch (err) {
      console.warn("Backend status polling:", err.message);
    }
  }, []);

  // Poll backend status every 1.5 seconds so cooldowns and dispatch states update seamlessly
  useEffect(() => {
    fetchStatusAndLogs();
    const interval = setInterval(fetchStatusAndLogs, 1500);
    return () => clearInterval(interval);
  }, [fetchStatusAndLogs]);

  // WebSocket Connection Management
  const connectWebSocket = useCallback(() => {
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("[SignAlert WS] Connected to backend.");
        setWsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          
          if (msg.type === "buffering") {
            setBufferProgress(msg.buffer_progress || 0);
            if (msg.features) setFeaturesDetected(msg.features);
            if (msg.agent_status) setAgentStatus(msg.agent_status);
          } else if (msg.type === "prediction") {
            setPrediction(msg);
            setBufferProgress(msg.buffer_progress || 30);
            if (msg.features) setFeaturesDetected(msg.features);
            if (msg.agent_status) setAgentStatus(msg.agent_status);

            // If alert triggered autonomously
            if (msg.alert_triggered) {
              triggerAlertVisualEffect(msg.label);
              if (msg.incident) {
                setIncidents(prev => [msg.incident, ...prev.filter(i => i.id !== msg.incident.id)]);
              }
            }
          }
        } catch (e) {
          console.error("Error parsing WS message:", e);
        }
      };

      ws.onclose = () => {
        console.log("[SignAlert WS] Disconnected. Reconnecting in 2s...");
        setWsConnected(false);
        wsRef.current = null;
        reconnectTimeoutRef.current = setTimeout(connectWebSocket, 2000);
      };

      ws.onerror = (err) => {
        console.warn("[SignAlert WS] Connection error:", err);
        ws.close();
      };
    } catch (e) {
      console.error("WS initialization error:", e);
      reconnectTimeoutRef.current = setTimeout(connectWebSocket, 2000);
    }
  }, []);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connectWebSocket]);

  // Send Frame to WebSocket
  const sendFrame = useCallback((base64Data) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: "frame",
        data: base64Data
      }));
    }
  }, []);

  // Visual Alert Effect
  const triggerAlertVisualEffect = (label) => {
    try {
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.6 },
        colors: ['#E11D48', '#DC2626', '#F59E0B', '#FFFFFF']
      });
    } catch (e) {
      // safe fallback
    }
  };

  // Start & Stop Monitoring Actions
  const handleStartMonitoring = () => {
    setIsMonitoring(true);
    setBufferProgress(0);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "reset" }));
    }
  };

  const handleStopMonitoring = () => {
    setIsMonitoring(false);
    setBufferProgress(0);
    setPrediction(null);
  };

  // Trigger Quick Test Alert
  const handleTriggerTestAlert = async (label) => {
    try {
      const res = await fetch(`${API_BASE}/api/test-alert`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ label, confidence: 0.95 })
      });
      const data = await res.json();
      
      if (data.triggered) {
        triggerAlertVisualEffect(label);
        if (data.incident) {
          setIncidents(prev => [data.incident, ...prev.filter(i => i.id !== data.incident.id)]);
        }
      }
      fetchStatusAndLogs();
    } catch (err) {
      alert("Error triggering test alert: " + err.message);
    }
  };

  // Reset 30s Cooldown
  const handleResetCooldown = async () => {
    try {
      await fetch(`${API_BASE}/api/reset-cooldown`, { method: "POST" });
      fetchStatusAndLogs();
    } catch (err) {
      console.error("Error resetting cooldown:", err);
    }
  };

  // Save Settings
  const handleSaveConfig = async (newConfig) => {
    try {
      await fetch(`${API_BASE}/api/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newConfig)
      });
      fetchStatusAndLogs();
    } catch (err) {
      alert("Failed to save config: " + err.message);
    }
  };

  return (
    <div className="app-container">
      {/* Top Navigation Header */}
      <Header
        wsConnected={wsConnected}
        isMonitoring={isMonitoring}
        agentStatus={agentStatus}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenEvaluation={() => setIsEvaluationOpen(true)}
      />

      {/* Main Single-Screen Dashboard Grid */}
      <main className="dashboard-grid">
        {/* Left Column: Camera Feed & Live Sign Prediction */}
        <section className="camera-column">
          <CameraFeed
            isMonitoring={isMonitoring}
            onStartMonitoring={handleStartMonitoring}
            onStopMonitoring={handleStopMonitoring}
            wsConnected={wsConnected}
            sendFrame={sendFrame}
            bufferProgress={bufferProgress}
            featuresDetected={featuresDetected}
            cooldownActive={agentStatus.cooldown_active}
          />

          <PredictionBadge
            prediction={prediction}
            bufferProgress={bufferProgress}
            isMonitoring={isMonitoring}
            threshold={agentStatus.confidence_threshold}
          />
        </section>

        {/* Right Column: Agent Action & Caregiver Dispatch Hub */}
        <section className="agent-column">
          <AgentActionPanel
            agentStatus={agentStatus}
            incidents={incidents}
            onResetCooldown={handleResetCooldown}
            onOpenEvaluation={() => setIsEvaluationOpen(true)}
          />
        </section>
      </main>

      {/* Evaluator Quick Test Bar */}
      <QuickTestBar
        onTriggerTestAlert={handleTriggerTestAlert}
        onResetCooldown={handleResetCooldown}
        cooldownActive={agentStatus.cooldown_active}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        currentPhone={agentStatus.caregiver_phone}
        currentSecondaryPhone={agentStatus.secondary_caregiver_phone}
        currentThreshold={agentStatus.confidence_threshold}
        currentCallTimeout={agentStatus.call_timeout_seconds}
        onSaveConfig={handleSaveConfig}
      />

      {/* Agentic Evaluation Benchmark Modal (arXiv:2602.22953v2) */}
      <AgentEvaluationModal
        isOpen={isEvaluationOpen}
        onClose={() => setIsEvaluationOpen(false)}
      />
    </div>
  );
}
