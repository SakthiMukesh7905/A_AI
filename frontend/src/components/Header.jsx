import React from 'react';
import { Activity, ShieldAlert, Wifi, WifiOff, Camera, PhoneCall, Sliders } from 'lucide-react';

export default function Header({ 
  wsConnected, 
  isMonitoring, 
  agentStatus, 
  onOpenSettings,
  onOpenEvaluation
}) {
  const isCooldown = agentStatus?.cooldown_active;
  const cooldownRemaining = agentStatus?.cooldown_remaining || 0;

  return (
    <header className="glass-panel header-container">
      <div className="brand-section">
        <div className="brand-icon-wrapper">
          <ShieldAlert size={26} />
        </div>
        <div className="brand-titles">
          <h1>
            SignAlert
            <span className="course-badge">Foundations of Agentic AI</span>
          </h1>
          <p className="brand-subtitle">
            Autonomous ISL Medical Emergency Recognition & Caregiver Dispatcher
          </p>
        </div>
      </div>

      <div className="status-pills-group">
        {/* WebSocket Backend Status */}
        <div className={`status-pill ${wsConnected ? 'online' : 'offline'}`}>
          {wsConnected ? <Wifi size={14} /> : <WifiOff size={14} />}
          <span>{wsConnected ? 'Backend Connected' : 'Server Offline'}</span>
        </div>

        {/* Camera Monitoring Status */}
        <div className={`status-pill ${isMonitoring ? 'online' : ''}`}>
          <Camera size={14} />
          <span>{isMonitoring ? 'Live Feed Active' : 'Camera Standby'}</span>
          {isMonitoring && <span className="status-dot pulse" />}
        </div>

        {/* Agent Cooldown Status */}
        {isCooldown ? (
          <div className="status-pill cooldown">
            <span className="status-dot pulse" />
            <span>Cooldown: {cooldownRemaining}s</span>
          </div>
        ) : (
          <div className="status-pill online">
            <Activity size={14} />
            <span>Agent Armed</span>
          </div>
        )}

        {/* Agent Evaluation Metrics Button */}
        {onOpenEvaluation && (
          <button 
            className="btn-icon" 
            onClick={onOpenEvaluation}
            title="Agentic Evaluation Benchmark (arXiv:2602.22953v2)"
            style={{ color: '#4F46E5', borderColor: 'rgba(99, 102, 241, 0.3)' }}
          >
            <Activity size={18} />
          </button>
        )}

        {/* Settings button */}
        <button 
          className="btn-icon" 
          onClick={onOpenSettings}
          title="System Settings"
        >
          <Sliders size={18} />
        </button>
      </div>
    </header>
  );
}
