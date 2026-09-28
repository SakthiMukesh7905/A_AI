import React, { useState } from 'react';
import { X, Save, ShieldAlert, Phone, Sliders, Users, Clock } from 'lucide-react';

export default function SettingsModal({ 
  isOpen, 
  onClose, 
  currentPhone,
  currentSecondaryPhone,
  currentThreshold, 
  currentCallTimeout,
  onSaveConfig 
}) {
  if (!isOpen) return null;

  const [phone, setPhone] = useState(currentPhone || "+917539949899");
  const [secondaryPhone, setSecondaryPhone] = useState(currentSecondaryPhone || "");
  const [threshold, setThreshold] = useState(currentThreshold || 0.70);
  const [callTimeout, setCallTimeout] = useState(currentCallTimeout || 15);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSaveConfig({ 
      caregiver_phone: phone, 
      secondary_caregiver_phone: secondaryPhone,
      confidence_threshold: parseFloat(threshold),
      call_timeout_seconds: parseInt(callTimeout)
    });
    onClose();
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={20} color="var(--alert-red-600)" />
            <h2 className="modal-title">SignAlert Caretaker Escalation Settings</h2>
          </div>
          <button className="btn-icon" onClick={onClose} style={{ width: '32px', height: '32px' }}>
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Primary Caregiver */}
          <div className="form-group">
            <label className="form-label" style={{ fontWeight: 700, color: 'var(--alert-red-700)' }}>
              <Phone size={14} style={{ display: 'inline', marginRight: '4px' }} />
              1️⃣ Primary Caretaker Phone Number
            </label>
            <input
              type="text"
              className="form-input"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+91XXXXXXXXXX"
              required
            />
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              First contact to receive the emergency phone call and SMS alert.
            </span>
          </div>

          {/* Secondary Caregiver */}
          <div className="form-group">
            <label className="form-label" style={{ fontWeight: 700, color: '#4F46E5' }}>
              <Users size={14} style={{ display: 'inline', marginRight: '4px' }} />
              2️⃣ Secondary Caretaker Phone Number (Failover)
            </label>
            <input
              type="text"
              className="form-input"
              value={secondaryPhone}
              onChange={(e) => setSecondaryPhone(e.target.value)}
              placeholder="+91XXXXXXXXXX (Optional/Recommended)"
            />
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Called automatically if the Primary Caretaker does not attend the call.
            </span>
          </div>

          {/* Call Ring Timeout */}
          <div className="form-group">
            <label className="form-label">
              <Clock size={14} style={{ display: 'inline', marginRight: '4px' }} />
              Primary Call Ring Timeout: {callTimeout} seconds
            </label>
            <input
              type="range"
              min="10"
              max="35"
              step="5"
              value={callTimeout}
              onChange={(e) => setCallTimeout(e.target.value)}
              style={{ accentColor: '#4F46E5' }}
            />
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Time allowed for Primary Caretaker to attend before automatic escalation begins.
            </span>
          </div>

          {/* Emergency Trigger Confidence Threshold */}
          <div className="form-group">
            <label className="form-label">
              Emergency Trigger Confidence Threshold: {Math.round(threshold * 100)}%
            </label>
            <input
              type="range"
              min="0.4"
              max="0.95"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(e.target.value)}
              style={{ accentColor: 'var(--alert-red-600)' }}
            />
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Signs recognized above this confidence percentage will trigger the autonomous escalation flow.
            </span>
          </div>

          <div style={{ background: 'var(--bg-sand-50)', padding: '12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-light)', fontSize: '0.76rem', color: 'var(--text-secondary)' }}>
            <strong>💡 Twilio Console Reminder:</strong> Ensure both Primary and Secondary numbers are added in Twilio under <strong>Verified Caller IDs</strong> with OTP verification.
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
            <button type="button" className="btn-primary-stop" onClick={onClose} style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
              Cancel
            </button>
            <button type="submit" className="btn-primary-start" style={{ padding: '8px 20px', fontSize: '0.85rem' }}>
              <Save size={14} />
              <span>Save Configuration</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
