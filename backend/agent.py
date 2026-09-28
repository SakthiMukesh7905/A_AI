import os
import time
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.config import settings

try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    TwilioClient = None


class EmergencyAgent:
    """Autonomous Agent responsible for emergency alert dispatching, multi-tier caregiver escalation, and cooldown management."""
    def __init__(self):
        self.cooldown_seconds = settings.COOLDOWN_SECONDS
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        self.last_trigger_time: float = 0.0
        self.current_state: str = "IDLE"  # IDLE, MONITORING, TRIGGERED, DISPATCHING, ESCALATING, COOLDOWN
        self.incident_history: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        
        # Test client initialization
        self.has_twilio_config = bool(
            settings.TWILIO_ACCOUNT_SID and 
            settings.TWILIO_AUTH_TOKEN and 
            settings.TWILIO_FROM_NUMBER and
            not settings.TWILIO_ACCOUNT_SID.startswith("your_")
        )
        if self.has_twilio_config and TwilioClient:
            print("[EmergencyAgent] Twilio credentials detected. Live Multi-Tier Caregiver Escalation active.")
        else:
            print("[EmergencyAgent] Twilio credentials not set or incomplete. Running in Safe Simulation Mode.")

    def is_in_cooldown(self) -> bool:
        return (time.time() - self.last_trigger_time) < self.cooldown_seconds

    def get_cooldown_remaining(self) -> float:
        remaining = self.cooldown_seconds - (time.time() - self.last_trigger_time)
        return max(0.0, round(remaining, 1))

    def can_trigger(self, label: str, confidence: float) -> bool:
        if confidence < self.confidence_threshold:
            return False
        if self.is_in_cooldown():
            return False
        return True

    def reset_cooldown(self):
        """Force reset cooldown (useful for debugging/testing)."""
        self.last_trigger_time = 0.0
        self.current_state = "IDLE"

    def update_config(
        self, 
        caregiver_phone: Optional[str] = None, 
        secondary_caregiver_phone: Optional[str] = None,
        threshold: Optional[float] = None, 
        cooldown: Optional[int] = None,
        call_timeout: Optional[int] = None
    ):
        if caregiver_phone:
            settings.CAREGIVER_PHONE_NUMBER = caregiver_phone
        if secondary_caregiver_phone is not None:
            settings.SECONDARY_CAREGIVER_PHONE_NUMBER = secondary_caregiver_phone
        if threshold is not None:
            self.confidence_threshold = threshold
            settings.CONFIDENCE_THRESHOLD = threshold
        if cooldown is not None:
            self.cooldown_seconds = cooldown
            settings.COOLDOWN_SECONDS = cooldown
        if call_timeout is not None:
            settings.CALL_TIMEOUT_SECONDS = call_timeout

    async def trigger_emergency_action(self, label: str, confidence: float, source: str = "Live Sign Detection") -> Dict[str, Any]:
        """Trigger emergency multi-tier caregiver dispatch flow with 30s cooldown protection."""
        now = time.time()
        
        # Double-check cooldown
        if self.is_in_cooldown():
            return {
                "triggered": False,
                "reason": "COOLDOWN_ACTIVE",
                "cooldown_remaining": self.get_cooldown_remaining(),
                "agent_status": f"Cooldown active ({self.get_cooldown_remaining()}s remaining)"
            }

        # Activate cooldown immediately
        self.last_trigger_time = now
        self.current_state = "TRIGGERED"
        
        incident_id = f"inc_{uuid.uuid4().hex[:8]}"
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        incident_record: Dict[str, Any] = {
            "id": incident_id,
            "timestamp": timestamp_str,
            "label": label,
            "confidence": round(confidence * 100, 1),
            "source": source,
            "primary_phone": settings.CAREGIVER_PHONE_NUMBER,
            "secondary_phone": settings.SECONDARY_CAREGIVER_PHONE_NUMBER or "Not Configured",
            "caregiver_phone": settings.CAREGIVER_PHONE_NUMBER,  # backward compatibility
            "escalation_state": "CALLING_PRIMARY",
            "primary_sms_status": "QUEUED",
            "primary_sms_sid": None,
            "primary_call_status": "QUEUED" if settings.ENABLE_VOICE_CALL else "DISABLED",
            "primary_call_sid": None,
            "secondary_sms_status": "STANDBY",
            "secondary_sms_sid": None,
            "secondary_call_status": "STANDBY" if settings.ENABLE_VOICE_CALL else "DISABLED",
            "secondary_call_sid": None,
            "sms_status": "QUEUED",
            "call_status": "QUEUED" if settings.ENABLE_VOICE_CALL else "DISABLED",
            "resolved_by": None,
            "is_simulation": not self.has_twilio_config,
            "message": f"🚨 EMERGENCY: Patient sign '{label}' detected with {confidence*100:.1f}% confidence."
        }
        
        self.incident_history.insert(0, incident_record)
        # Keep max 50 items
        if len(self.incident_history) > 50:
            self.incident_history.pop()

        # Dispatch in background task so prediction loop never blocks or stutters
        asyncio.create_task(self._execute_dispatch(incident_record))

        return {
            "triggered": True,
            "incident": incident_record,
            "cooldown_remaining": self.cooldown_seconds,
            "agent_status": f"Alert triggered for {label}. Calling Primary Caregiver..."
        }

    async def _wait_for_call_answered(self, client: Any, call_sid: str, timeout_seconds: int = 15) -> bool:
        """Monitor Twilio Call in background to determine if Primary Caretaker answered."""
        loop = asyncio.get_running_loop()
        start_time = time.time()
        
        # Poll call status every 2 seconds
        while time.time() - start_time < (timeout_seconds + 5):
            try:
                call_obj = await loop.run_in_executor(None, lambda: client.calls(call_sid).fetch())
                status = call_obj.status.lower()
                print(f"[EmergencyAgent] Call ({call_sid}) status: {status}")
                
                # If call is currently answered (in-progress) or completed with speech duration
                if status == "in-progress":
                    return True
                if status == "completed":
                    dur = getattr(call_obj, "duration", None)
                    # If completed with non-zero duration or answered
                    if dur is not None and int(dur) > 0:
                        return True
                    return True
                if status in ("no-answer", "busy", "failed", "canceled"):
                    return False
            except Exception as e:
                print(f"[EmergencyAgent] Error querying call status {call_sid}: {e}")
            
            await asyncio.sleep(2.0)
            
        return False

    async def _execute_dispatch(self, incident: Dict[str, Any]):
        """Execute multi-tier caregiver escalation: Call Primary -> If Unattended -> Escalate to Secondary."""
        self.current_state = "DISPATCHING"
        label = incident["label"]
        conf_pct = incident["confidence"]
        primary_phone = incident["primary_phone"]
        secondary_phone = settings.SECONDARY_CAREGIVER_PHONE_NUMBER
        call_timeout = settings.CALL_TIMEOUT_SECONDS
        
        primary_msg = (
            f"🚨 SignAlert EMERGENCY: Distress sign '{label}' "
            f"(Confidence: {conf_pct}%) detected. Immediate attention required for patient."
        )

        primary_answered = False

        # ==========================================
        # PHASE 1: DISPATCH TO PRIMARY CAREGIVER
        # ==========================================
        print(f"[EmergencyAgent] [Phase 1] Contacting Primary Caregiver: {primary_phone}")
        
        if self.has_twilio_config and TwilioClient:
            client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            loop = asyncio.get_running_loop()

            # 1. Primary SMS
            try:
                msg = await loop.run_in_executor(
                    None,
                    lambda: client.messages.create(
                        body=primary_msg,
                        from_=settings.TWILIO_FROM_NUMBER,
                        to=primary_phone
                    )
                )
                incident["primary_sms_status"] = "SENT"
                incident["primary_sms_sid"] = msg.sid
                incident["sms_status"] = "SENT"
                print(f"[EmergencyAgent] Twilio Primary SMS sent! SID: {msg.sid}")
            except Exception as e:
                clean_err = self._clean_error(str(e))
                incident["primary_sms_status"] = f"ERROR: {clean_err}"
                incident["sms_status"] = incident["primary_sms_status"]
                print(f"[EmergencyAgent] Primary SMS failed: {clean_err}")

            # 2. Primary Voice Call with Timeout & Status Tracking
            if settings.ENABLE_VOICE_CALL:
                twiml_content = (
                    f'<Response><Say voice="alice">'
                    f'Emergency alert from Sign Alert. Distress sign detected: {label}. '
                    f'Please check on your patient immediately.'
                    f'</Say></Response>'
                )
                try:
                    # Place call with ring timeout (e.g. 15s)
                    try:
                        call = await loop.run_in_executor(
                            None,
                            lambda: client.calls.create(
                                twiml=twiml_content,
                                from_=settings.TWILIO_FROM_NUMBER,
                                to=primary_phone,
                                timeout=call_timeout
                            )
                        )
                    except Exception as call_err:
                        err_str = str(call_err).lower()
                        if "disallowed parameters" in err_str or "trial" in err_str:
                            call = await loop.run_in_executor(
                                None,
                                lambda: client.calls.create(
                                    url="http://demo.twilio.com/docs/voice.xml",
                                    from_=settings.TWILIO_FROM_NUMBER,
                                    to=primary_phone,
                                    timeout=call_timeout
                                )
                            )
                        else:
                            raise call_err

                    incident["primary_call_status"] = "RINGING"
                    incident["primary_call_sid"] = call.sid
                    incident["call_status"] = "RINGING"
                    print(f"[EmergencyAgent] Twilio Primary Call ringing ({call_timeout}s timeout)... SID: {call.sid}")

                    # Monitor if primary attends
                    primary_answered = await self._wait_for_call_answered(client, call.sid, timeout_seconds=call_timeout)
                    
                    if primary_answered:
                        incident["primary_call_status"] = "ANSWERED (Attended)"
                        incident["escalation_state"] = "RESOLVED_BY_PRIMARY"
                        incident["resolved_by"] = f"Primary Caregiver ({primary_phone})"
                        incident["call_status"] = "ANSWERED"
                        print(f"[EmergencyAgent] ✅ Primary Caregiver attended call. Alert resolved!")
                    else:
                        incident["primary_call_status"] = "UNANSWERED (No Answer / Busy)"
                        incident["escalation_state"] = "ESCALATING_TO_SECONDARY"
                        incident["call_status"] = "UNANSWERED"
                        print(f"[EmergencyAgent] ⚠️ Primary Caregiver DID NOT answer call. Triggering Secondary Escalation...")

                except Exception as e:
                    clean_err = self._clean_error(str(e))
                    incident["primary_call_status"] = f"ERROR: {clean_err}"
                    incident["call_status"] = incident["primary_call_status"]
                    print(f"[EmergencyAgent] Primary Voice Call failed: {clean_err}")
                    # If call failed to initiate, escalate to secondary
                    primary_answered = False
        else:
            # Safe Simulation Mode Phase 1
            await asyncio.sleep(1.0)
            incident["primary_sms_status"] = "SENT (Simulation)"
            incident["primary_sms_sid"] = f"SM_SIM_{uuid.uuid4().hex[:8]}"
            incident["primary_call_status"] = "RINGING (Simulation - Unattended)"
            incident["primary_call_sid"] = f"CA_SIM_{uuid.uuid4().hex[:8]}"
            incident["sms_status"] = incident["primary_sms_status"]
            incident["call_status"] = incident["primary_call_status"]
            print(f"[EmergencyAgent] [SIMULATION] Primary Alert sent to {primary_phone}. Simulating no-answer...")
            await asyncio.sleep(2.0)
            incident["primary_call_status"] = "UNANSWERED (Simulation: No Answer)"
            incident["escalation_state"] = "ESCALATING_TO_SECONDARY"
            primary_answered = False

        # =======================================================
        # PHASE 2: ESCALATE TO SECONDARY CAREGIVER IF UNANSWERED
        # =======================================================
        if not primary_answered:
            if secondary_phone and secondary_phone.strip() and secondary_phone != "Not Configured":
                self.current_state = "ESCALATING"
                print(f"[EmergencyAgent] [Phase 2] 🚨 Escalating to Secondary Caregiver: {secondary_phone}")
                
                secondary_msg = (
                    f"🚨 SignAlert ESCALATION ALERT: Primary caregiver unreachable! "
                    f"Distress sign '{label}' ({conf_pct}%) detected for patient. Please attend immediately!"
                )

                if self.has_twilio_config and TwilioClient:
                    client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                    loop = asyncio.get_running_loop()

                    # 1. Secondary SMS
                    try:
                        sec_sms = await loop.run_in_executor(
                            None,
                            lambda: client.messages.create(
                                body=secondary_msg,
                                from_=settings.TWILIO_FROM_NUMBER,
                                to=secondary_phone
                            )
                        )
                        incident["secondary_sms_status"] = "SENT (Escalated)"
                        incident["secondary_sms_sid"] = sec_sms.sid
                        print(f"[EmergencyAgent] 🚨 Secondary SMS dispatched! SID: {sec_sms.sid}")
                    except Exception as e:
                        clean_err = self._clean_error(str(e))
                        incident["secondary_sms_status"] = f"ERROR: {clean_err}"
                        print(f"[EmergencyAgent] Secondary SMS failed: {clean_err}")

                    # 2. Secondary Voice Call
                    if settings.ENABLE_VOICE_CALL:
                        sec_twiml = (
                            f'<Response><Say voice="alice">'
                            f'Escalation alert from Sign Alert. Primary caregiver did not respond. '
                            f'Distress sign detected: {label}. Please attend to the patient immediately.'
                            f'</Say></Response>'
                        )
                        try:
                            try:
                                sec_call = await loop.run_in_executor(
                                    None,
                                    lambda: client.calls.create(
                                        twiml=sec_twiml,
                                        from_=settings.TWILIO_FROM_NUMBER,
                                        to=secondary_phone
                                    )
                                )
                            except Exception as sec_call_err:
                                err_str = str(sec_call_err).lower()
                                if "disallowed parameters" in err_str or "trial" in err_str:
                                    sec_call = await loop.run_in_executor(
                                        None,
                                        lambda: client.calls.create(
                                            url="http://demo.twilio.com/docs/voice.xml",
                                            from_=settings.TWILIO_FROM_NUMBER,
                                            to=secondary_phone
                                        )
                                    )
                                else:
                                    raise sec_call_err

                            incident["secondary_call_status"] = "CALLING (Escalated)"
                            incident["secondary_call_sid"] = sec_call.sid
                            incident["escalation_state"] = "SECONDARY_ALERTED"
                            incident["resolved_by"] = f"Secondary Caregiver ({secondary_phone})"
                            print(f"[EmergencyAgent] 🚨 Secondary Voice Call initiated! SID: {sec_call.sid}")
                        except Exception as e:
                            clean_err = self._clean_error(str(e))
                            incident["secondary_call_status"] = f"ERROR: {clean_err}"
                            print(f"[EmergencyAgent] Secondary Voice Call failed: {clean_err}")
                else:
                    # Simulation Mode Phase 2
                    await asyncio.sleep(1.0)
                    incident["secondary_sms_status"] = "SENT (Simulation)"
                    incident["secondary_sms_sid"] = f"SM_SIM_SEC_{uuid.uuid4().hex[:8]}"
                    incident["secondary_call_status"] = "CALLING (Simulation)"
                    incident["secondary_call_sid"] = f"CA_SIM_SEC_{uuid.uuid4().hex[:8]}"
                    incident["escalation_state"] = "SECONDARY_ALERTED"
                    incident["resolved_by"] = f"Secondary Caregiver ({secondary_phone})"
                    print(f"[EmergencyAgent] [SIMULATION] Secondary Alert successfully dispatched to {secondary_phone}")
            else:
                incident["escalation_state"] = "PRIMARY_UNANSWERED (No Secondary Set)"
                print("[EmergencyAgent] ⚠️ Primary did not answer, but no Secondary Caregiver is configured.")

        self.current_state = "COOLDOWN"

    def _clean_error(self, err_text: str) -> str:
        """Clean raw exception text and strip ANSI formatting."""
        if "predefined sms templates" in err_text.lower():
            clean = "Twilio Trial Restriction: Custom SMS body blocked on trial."
        else:
            clean = err_text.split('\n')[0]
        for code in ('\x1b[31m', '\x1b[0m', '\x1b[36m', '\x1b[37m', '\x1b[34m', '\x1b[49m'):
            clean = clean.replace(code, '')
        return clean.strip()

    def get_status(self) -> Dict[str, Any]:
        cooldown_rem = self.get_cooldown_remaining()
        in_cd = self.is_in_cooldown()
        
        status_text = "Idle"
        if in_cd:
            status_text = f"Cooldown ({cooldown_rem}s remaining)"
        elif self.current_state == "ESCALATING":
            status_text = "🚨 Primary Unanswered! Escalating to Secondary Caregiver..."
        elif self.current_state == "DISPATCHING":
            status_text = "Dispatching Primary Emergency Call..."
        elif self.current_state == "MONITORING":
            status_text = "Active & Monitoring"
            
        return {
            "state": "COOLDOWN" if in_cd else self.current_state,
            "status_text": status_text,
            "cooldown_active": in_cd,
            "cooldown_remaining": cooldown_rem,
            "cooldown_total": self.cooldown_seconds,
            "confidence_threshold": self.confidence_threshold,
            "caregiver_phone": settings.CAREGIVER_PHONE_NUMBER,
            "secondary_caregiver_phone": settings.SECONDARY_CAREGIVER_PHONE_NUMBER,
            "call_timeout_seconds": settings.CALL_TIMEOUT_SECONDS,
            "twilio_configured": self.has_twilio_config,
            "voice_call_enabled": settings.ENABLE_VOICE_CALL,
            "total_incidents": len(self.incident_history)
        }


# Singleton Agent instance
agent = EmergencyAgent()
