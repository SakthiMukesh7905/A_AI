import React from 'react';
import { AlertCircle, Flame, BarChart2 } from 'lucide-react';

const CLASS_DISPLAY_NAMES = {
  "Cant-breathe": "CAN'T BREATHE",
  "Dizzy": "DIZZY",
  "Heart-pain": "HEART PAIN",
  "Help": "HELP",
  "Pain": "PAIN"
};

const CLASS_EMOJIS = {
  "Cant-breathe": "🫁",
  "Dizzy": "💫",
  "Heart-pain": "💔",
  "Help": "🆘",
  "Pain": "⚡"
};

export default function PredictionBadge({ 
  prediction, 
  bufferProgress, 
  isMonitoring, 
  threshold = 0.70 
}) {
  const currentLabel = prediction?.label || "Standby";
  const confidence = prediction?.confidence || 0;
  const probabilities = prediction?.probabilities || {
    "Cant-breathe": 0,
    "Dizzy": 0,
    "Heart-pain": 0,
    "Help": 0,
    "Pain": 0
  };

  const isDistressActive = isMonitoring && bufferProgress >= 30 && confidence >= threshold;
  const displayName = CLASS_DISPLAY_NAMES[currentLabel] || currentLabel.toUpperCase();
  const emoji = CLASS_EMOJIS[currentLabel] || "🤲";

  return (
    <div className="glass-panel prediction-card">
      <div className="section-title">
        <Flame size={20} color="var(--alert-red-600)" />
        <span>Live ISL Emergency Classifier</span>
      </div>

      {/* Prominent Emergency Prediction Badge */}
      <div className={`live-badge-wrapper ${isDistressActive ? 'alert-active' : ''}`}>
        <span className="badge-label-caption">
          {!isMonitoring 
            ? "CAMERA STANDBY" 
            : bufferProgress < 30 
              ? `BUFFERING FRAMES (${bufferProgress}/30)...` 
              : isDistressActive 
                ? "🚨 DISTRESS SIGN DETECTED" 
                : "CURRENT PREDICTED SIGN"}
        </span>

        <div className="badge-sign-name">
          {!isMonitoring ? (
            <span style={{ color: 'var(--text-muted)', fontSize: '1.4rem' }}>Awaiting Stream</span>
          ) : bufferProgress < 30 ? (
            <span style={{ color: 'var(--amber-600)', fontSize: '1.3rem' }}>
              Analyzing Keypoints ({Math.round((bufferProgress / 30) * 100)}%)
            </span>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span>{emoji}</span>
              <span>{displayName}</span>
            </div>
          )}
        </div>

        {/* Confidence Progress Bar */}
        {isMonitoring && bufferProgress >= 30 && (
          <div className="confidence-row">
            <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Confidence
            </span>
            <div className="confidence-bar-bg">
              <div 
                className="confidence-bar-fill" 
                style={{ width: `${Math.min(100, Math.round(confidence * 100))}%` }} 
              />
            </div>
            <span className="confidence-percentage">
              {(confidence * 100).toFixed(1)}%
            </span>
          </div>
        )}
      </div>

      {/* Multi-Class Probability Breakdown */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <BarChart2 size={13} /> Class Probability Distribution
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            Threshold: {(threshold * 100).toFixed(0)}%
          </span>
        </div>

        <div className="probability-breakdown">
          {Object.entries(probabilities).map(([className, prob]) => {
            const isActive = isMonitoring && bufferProgress >= 30 && className === currentLabel;
            const probPct = Math.round(prob * 100);

            return (
              <div 
                key={className} 
                className={`prob-chip ${isActive ? 'active' : ''}`}
              >
                <span className="prob-name" title={CLASS_DISPLAY_NAMES[className] || className}>
                  {CLASS_EMOJIS[className]} {className}
                </span>
                <div className="prob-meter-bg">
                  <div 
                    className="prob-meter-fill" 
                    style={{ width: `${probPct}%` }} 
                  />
                </div>
                <span className="prob-val">{probPct}%</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
