import React from 'react';
import { Sparkles, RotateCcw } from 'lucide-react';

const TEST_SIGNS = [
  { label: "Heart-pain", name: "💔 Heart-pain" },
  { label: "Cant-breathe", name: "🫁 Cant-breathe" },
  { label: "Help", name: "🆘 Help" },
  { label: "Dizzy", name: "💫 Dizzy" },
  { label: "Pain", name: "⚡ Pain" }
];

export default function QuickTestBar({ 
  onTriggerTestAlert, 
  onResetCooldown, 
  cooldownActive 
}) {
  return (
    <div className="glass-panel quick-test-panel">
      <div className="quick-test-label">
        <Sparkles size={16} color="var(--alert-red-600)" />
        <span>Evaluator Quick Test:</span>
      </div>

      <div className="quick-test-buttons">
        {TEST_SIGNS.map(({ label, name }) => (
          <button
            key={label}
            className="btn-demo-trigger"
            onClick={() => onTriggerTestAlert(label)}
            title={`Simulate instant recognition for "${label}" to trigger Twilio dispatch`}
          >
            <span>{name}</span>
          </button>
        ))}

        {cooldownActive && (
          <button
            className="btn-demo-trigger"
            onClick={onResetCooldown}
            style={{ background: 'var(--amber-bg)', borderColor: 'var(--amber-500)', color: 'var(--amber-600)' }}
            title="Reset 30-second cooldown"
          >
            <RotateCcw size={13} />
            <span>Reset 30s Cooldown</span>
          </button>
        )}
      </div>
    </div>
  );
}
