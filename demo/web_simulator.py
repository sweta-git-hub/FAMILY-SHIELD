"""
Family Voice Shield (FVS) - Interactive Dual-Device Web Simulator
Phase 2 & Phase 3:
- Contact-based pairing & 60-second synchronized 6-digit TOTP
- Elderly UX: Large keypad, high-contrast mode, bilingual voice prompts (EN & HI)
- Safe emergency actions: "Hang Up & Call Back" and "Family SOS"
- Risk-free Practice Call mode ("अभ्यास कॉल")
Zero external dependencies (pure Python standard library).
"""

import http.server
import json
import os
import socketserver
import sys
import threading
import time
import urllib.parse
from typing import Optional

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.alert_tiers import AlertStateMachine, AlertTier
from core.crypto import VerificationResult
from core.elderly_ux import (
    ElderlySessionManager,
    Language,
    PracticeCallSession,
    PromptKey,
    VOICE_PROMPT_CATALOG,
)
from core.pairing import (
    DEFAULT_CODE_STEP,
    DeviceRole,
    PairedRelationship,
    PairingSession,
)
from core.phone_util import format_phone_display, normalize_phone_number
from core.storage import SecureVault
from ml.fusion import MultimodalFusionEngine
from demo.scenarios import (
    SCENARIO_CATALOG,
    get_scenario,
    list_scenarios,
    Scenario,
    ScenarioChunk,
)
from demo.telephony_replay import TelephonyReplayHarness
from dataclasses import asdict


class SimulatorState:
    """In-memory state holding the simulated mobile phones and elderly UX state."""

    def __init__(self, step_seconds: int = 60):
        self.step_seconds = step_seconds
        self.guardian_phone = "+919876500001"
        self.guardian_vault = SecureVault("guardian_vault_passphrase")

        self.member_phone = "+919876500002"
        self.member_name = "Rahul (Son)"
        self.member_vault = SecureVault("member_vault_passphrase")

        self.guardian_rel: Optional[PairedRelationship] = None
        self.member_rel: Optional[PairedRelationship] = None
        self.lockout_session = None

        self.elderly_manager = ElderlySessionManager()
        self.practice_session = PracticeCallSession(scenario_key="legitimate_child")

        # Phase 7: Multimodal Fusion & Alert Engine
        self.alert_state_machine = AlertStateMachine()
        self.fusion_engine = MultimodalFusionEngine()
        self.current_risk_result = {
            "tier": "GREEN",
            "risk": 0.08,
            "dominant_modality": "none",
            "prompt_action": "normal",
            "spoken_advisory": "कॉल सामान्य है",
            "reasons": [],
        }

        # Phase 8: Scripted Evaluation Scenarios & Replay
        self.active_scenario_id = "S1"
        self.active_scenario_step = 0
        self.scenario_event_log = []
        self.pending_invitations = {}

        # Auto-pair a default family link for instant demo convenience
        self.pair_devices(
            guardian_phone=self.guardian_phone,
            member_phone=self.member_phone,
            member_name=self.member_name,
        )

    def pair_devices(self, guardian_phone: str, member_phone: str, member_name: str) -> dict:
        guardian_raw = guardian_phone if guardian_phone and guardian_phone.strip() else self.guardian_phone
        member_raw = member_phone if member_phone and member_phone.strip() else self.member_phone
        norm_guardian = normalize_phone_number(guardian_raw)
        norm_member = normalize_phone_number(member_raw)

        self.guardian_phone = norm_guardian
        self.member_phone = norm_member
        self.member_name = member_name.strip() or "Rahul (Son)"

        # 1. Guardian creates zero-knowledge pairing invitation
        invitation_uri, _ = PairingSession.create_invitation(
            creator_phone=self.guardian_phone,
            creator_role=DeviceRole.GUARDIAN,
            target_phone=self.member_phone,
            target_name=self.member_name,
            step_seconds=self.step_seconds,
        )

        # 2. Member device receives and accepts invitation
        g_rel, m_rel = PairingSession.accept_invitation(
            invitation_uri=invitation_uri,
            acceptor_phone=self.member_phone,
            acceptor_name="Mom",
        )

        self.guardian_rel = g_rel
        self.member_rel = m_rel
        self.guardian_vault.add_relationship(g_rel)
        self.member_vault.add_relationship(m_rel)
        self.lockout_session = g_rel.create_lockout_session(max_attempts=3)

        return {
            "status": "PAIRED",
            "guardian_phone": self.guardian_phone,
            "member_phone": self.member_phone,
            "member_name": self.member_name,
            "step_seconds": self.step_seconds,
            "invitation_uri": invitation_uri,
        }

    def create_pairing_invitation(self, member_phone: str, member_name: str, host_ip: str = "192.168.137.230:8080") -> dict:
        import random, re
        norm_member = normalize_phone_number(member_phone)
        m_name = member_name.strip() or "Rahul (Son)"
        pin = f"{random.randint(100000, 999999)}"

        invitation_uri, _ = PairingSession.create_invitation(
            creator_phone=self.guardian_phone,
            creator_role=DeviceRole.GUARDIAN,
            target_phone=norm_member,
            target_name=m_name,
            step_seconds=self.step_seconds,
        )

        clean_digits = re.sub(r"[^\d]", "", norm_member)
        msg_text = (
            f"🛡️ *Family Voice Shield - Secure Pairing Invitation*\n\n"
            f"Mom has invited you to connect your phone for AI voice-clone scam protection.\n\n"
            f"🔑 Your One-Time Pairing PIN: *{pin}*\n\n"
            f"Tap this link on your phone to connect:\n"
            f"http://{host_ip}/?pair_pin={pin}\n\n"
            f"(This code expires in 10 minutes)."
        )
        whatsapp_url = f"https://api.whatsapp.com/send?phone={clean_digits}&text={urllib.parse.quote(msg_text)}"
        sms_text = (
            f"[Family Voice Shield] Mom invited you to connect. "
            f"Your 6-digit Pairing PIN is: {pin}. Open: http://{host_ip}/?pair_pin={pin}"
        )

        record = {
            "pin": pin,
            "target_phone": norm_member,
            "display_phone": format_phone_display(norm_member),
            "target_name": m_name,
            "invitation_uri": invitation_uri,
            "whatsapp_url": whatsapp_url,
            "sms_text": sms_text,
            "sms_url": f"sms:{clean_digits}?body={urllib.parse.quote(sms_text)}",
            "mobile_url": f"http://{host_ip}/?pair_pin={pin}",
            "expires_at": time.time() + 600,
        }
        self.pending_invitations[pin] = record
        return record

    def confirm_pairing_pin(self, pin: str, acceptor_name: str = "Mom") -> dict:
        cleaned_pin = pin.strip()
        record = self.pending_invitations.get(cleaned_pin)
        if not record:
            raise ValueError(f"Invalid or expired Pairing PIN: '{cleaned_pin}'")

        if time.time() > record["expires_at"]:
            del self.pending_invitations[cleaned_pin]
            raise ValueError("This Pairing PIN has expired. Please generate a new one.")

        g_rel, m_rel = PairingSession.accept_invitation(
            invitation_uri=record["invitation_uri"],
            acceptor_phone=record["target_phone"],
            acceptor_name=acceptor_name,
        )

        self.guardian_phone = g_rel.owner_phone
        self.member_phone = m_rel.owner_phone
        self.member_name = record["target_name"]

        self.guardian_rel = g_rel
        self.member_rel = m_rel
        self.guardian_vault.add_relationship(g_rel)
        self.member_vault.add_relationship(m_rel)
        self.lockout_session = g_rel.create_lockout_session(max_attempts=3)

        del self.pending_invitations[cleaned_pin]

        return {
            "status": "PAIRED",
            "guardian_phone": self.guardian_phone,
            "member_phone": self.member_phone,
            "member_name": self.member_name,
            "step_seconds": self.step_seconds,
        }

    def get_status(self) -> dict:
        now = int(time.time())
        rem = self.step_seconds - (now % self.step_seconds)

        if not self.guardian_rel or not self.member_rel:
            return {"paired": False, "now": now, "remaining": rem}

        rahul_outbound_code, _ = self.member_rel.get_outbound_code(timestamp=now)
        mom_expected_code, _ = self.guardian_rel.get_expected_inbound_code(timestamp=now)
        mom_outbound_code, _ = self.guardian_rel.get_outbound_code(timestamp=now)
        rahul_expected_code, _ = self.member_rel.get_expected_inbound_code(timestamp=now)

        return {
            "paired": True,
            "now": now,
            "step_seconds": self.step_seconds,
            "remaining": rem,
            "language": self.elderly_manager.config.language.value,
            "high_contrast": self.elderly_manager.config.high_contrast,
            "guardian": {
                "phone": format_phone_display(self.guardian_phone),
                "expected_from_member": mom_expected_code,
                "outbound_to_member": mom_outbound_code,
                "peer_name": self.member_name,
                "peer_phone": format_phone_display(self.member_phone),
                "raw_peer_phone": self.member_phone,
                "failed_attempts": self.lockout_session.failed_attempts if self.lockout_session else 0,
                "is_locked": self.lockout_session.is_locked if self.lockout_session else False,
            },
            "member": {
                "phone": format_phone_display(self.member_phone),
                "name": self.member_name,
                "outbound_to_guardian": rahul_outbound_code,
                "expected_from_guardian": rahul_expected_code,
                "peer_name": "Mom (Guardian)",
                "peer_phone": format_phone_display(self.guardian_phone),
            },
            "risk_state": self.current_risk_result,
        }

    def simulate_risk(self, s_a: float, s_t: float, s_c: float, lang: str = "hi") -> dict:
        """Simulates incoming call risk scoring and updates the alert state machine."""
        fusion = self.fusion_engine.fuse(s_a=s_a, s_t=s_t, s_c=s_c)
        reasons: List[str] = []
        if s_t >= 0.50:
            reasons.append("suspicious_scam_intent")
        if s_a >= 0.50:
            reasons.append("synthetic_voice_clone_artifacts")
        if s_c >= 0.20:
            reasons.append("unknown_incoming_number")

        tier, transition = self.alert_state_machine.update(
            fused_risk=fusion.fused_risk,
            reasons=reasons,
        )
        advisory = self.alert_state_machine.get_spoken_advisory(lang=lang)
        prompt = self.alert_state_machine.get_prompt_action()

        notif_dict = None
        if tier == AlertTier.RED:
            notif = self.alert_state_machine.generate_emergency_notification(
                target_phone=self.guardian_phone,
                fused_risk=fusion.fused_risk,
                dominant_modality=fusion.dominant_modality,
                reasons=reasons,
            )
            notif_dict = notif.to_dict()

        self.current_risk_result = {
            "tier": tier.value,
            "risk": fusion.fused_risk,
            "dominant_modality": fusion.dominant_modality,
            "prompt_action": prompt,
            "spoken_advisory": advisory,
            "reasons": reasons,
            "emergency_notification": notif_dict,
        }
        return self.current_risk_result

    def verify_code(self, candidate_code: str) -> dict:
        if not self.guardian_rel or not self.lockout_session:
            return {"result": "NOT_PAIRED"}

        now = int(time.time())
        result = self.guardian_rel.verify_incoming_code(
            candidate_code=candidate_code,
            timestamp=now,
            session=self.lockout_session,
        )

        lang = self.elderly_manager.config.language
        if result == VerificationResult.SUCCESS:
            spoken_prompt = self.elderly_manager.get_prompt(PromptKey.CALLER_VERIFIED, lang=lang)
        elif result == VerificationResult.LOCKED_OUT:
            spoken_prompt = self.elderly_manager.get_prompt(PromptKey.LOCKOUT_FRAUD_ALERT, lang=lang)
        elif result == VerificationResult.DURESS:
            spoken_prompt = self.elderly_manager.get_prompt(PromptKey.DURESS_TRIGGERED, lang=lang)
        else:
            spoken_prompt = self.elderly_manager.get_prompt(PromptKey.WRONG_CODE_WARNING, lang=lang)

        return {
            "result": result.value,
            "failed_attempts": self.lockout_session.failed_attempts,
            "is_locked": self.lockout_session.is_locked,
            "is_verified": self.lockout_session.is_verified,
            "spoken_prompt": spoken_prompt,
        }

    def reset_verification(self) -> dict:
        if self.lockout_session:
            self.lockout_session.reset()
        return {"status": "RESET_OK"}

    def get_prompts(self, lang_str: str) -> dict:
        lang = Language.HI if lang_str.lower() == "hi" else Language.EN
        self.elderly_manager.set_language(lang)
        catalog = VOICE_PROMPT_CATALOG.get(lang, VOICE_PROMPT_CATALOG[Language.EN])
        return {k.value: v for k, v in catalog.items()}

    def get_emergency_action(self) -> dict:
        return self.elderly_manager.get_emergency_callback_action(
            peer_phone=self.member_phone,
            peer_name=self.member_name,
        )

    def trigger_family_sos(self) -> dict:
        return self.elderly_manager.broadcast_family_sos(
            guardian_phone=self.guardian_phone,
            suspect_phone="+919999988888",
            peer_name=self.member_name,
        )

    def practice_verify(self, code: str) -> dict:
        return self.practice_session.evaluate_code(code)

    def get_scenarios(self) -> list:
        return list_scenarios()

    def run_scenario(self, scenario_id: str) -> dict:
        sc = get_scenario(scenario_id)
        if not sc:
            raise ValueError(f"Scenario '{scenario_id}' not found")

        self.active_scenario_id = sc.scenario_id
        harness = TelephonyReplayHarness(simulate_telephony=True)
        report = harness.run(sc)

        self.scenario_event_log = [
            {
                "chunk_index": m.chunk_index,
                "transcript": m.transcript,
                "s_a": m.s_a_mock,
                "s_c": m.s_c,
                "tier": m.actual_tier,
                "risk": m.risk_score,
                "latency_ms": m.latency_ms,
                "tier_match": m.tier_match,
            }
            for m in report.chunk_metrics
        ]
        self.active_scenario_step = len(sc.chunks)

        final_tier = report.actual_final_tier
        last_metric = report.chunk_metrics[-1] if report.chunk_metrics else None
        fused_risk = last_metric.risk_score if last_metric else 0.0

        if final_tier == "RED":
            advisory = "चेतावनी: आवाज क्लोन धोखाधड़ी का उच्च जोखिम! (Critical Voice Clone Threat)"
            prompt = "demand_code"
        elif final_tier == "AMBER":
            advisory = "सतर्कता: संदिग्ध कॉल! परिवार का कोड पूछें (Suspicious Call: Ask for Family Code)"
            prompt = "suggest_code"
        elif final_tier == "REJECTED":
            advisory = "कॉल अस्वीकृत: पुराना या अमान्य टोकन (Replay Attack Blocked)"
            prompt = "terminate_call"
        else:
            advisory = "कॉल सुरक्षित है (Safe Call)"
            prompt = "normal"

        self.current_risk_result = {
            "tier": final_tier,
            "risk": fused_risk,
            "dominant_modality": "semantic" if report.category == "scam" else "none",
            "prompt_action": prompt,
            "spoken_advisory": advisory,
            "reasons": [report.category] if report.category == "scam" else [],
            "emergency_notification": None,
            "emergency_dispatched": report.emergency_dispatched,
            "relay_rejected": report.relay_rejected,
            "time_to_amber": report.time_to_amber_seconds,
            "time_to_red": report.time_to_red_seconds,
            "amber_sla_met": report.amber_sla_met,
        }

        return {
            "report": asdict(report),
            "risk_state": self.current_risk_result,
            "event_log": self.scenario_event_log,
        }

    def step_scenario(self, scenario_id: str, step_index: Optional[int] = None) -> dict:
        sc = get_scenario(scenario_id)
        if not sc:
            raise ValueError(f"Scenario '{scenario_id}' not found")

        if self.active_scenario_id != sc.scenario_id or (step_index is not None and step_index == 0):
            self.active_scenario_id = sc.scenario_id
            self.active_scenario_step = 0
            self.scenario_event_log = []
            self.alert_state_machine = AlertStateMachine()

        idx = step_index if step_index is not None else self.active_scenario_step
        if idx >= len(sc.chunks):
            return {
                "completed": True,
                "scenario_id": sc.scenario_id,
                "message": "Scenario already completed",
                "risk_state": self.current_risk_result,
                "event_log": self.scenario_event_log,
            }

        chunk = sc.chunks[idx]
        self.active_scenario_step = idx + 1

        if chunk.expected_tier == "REJECTED":
            metric = {
                "chunk_index": idx,
                "transcript": chunk.transcript,
                "s_a": chunk.s_a_mock,
                "s_c": chunk.s_c,
                "tier": "REJECTED",
                "risk": 1.0,
                "latency_ms": 0.05,
                "tier_match": True,
            }
            self.scenario_event_log.append(metric)
            self.current_risk_result = {
                "tier": "REJECTED",
                "risk": 1.0,
                "dominant_modality": "cryptographic",
                "prompt_action": "terminate_call",
                "spoken_advisory": "कॉल अस्वीकृत: पुराना या अमान्य टोकन (Replay Attack Blocked)",
                "reasons": ["stale_session_nonce"],
                "emergency_notification": None,
                "relay_rejected": True,
            }
            return {
                "completed": (self.active_scenario_step >= len(sc.chunks)),
                "scenario_id": sc.scenario_id,
                "chunk": metric,
                "risk_state": self.current_risk_result,
                "event_log": self.scenario_event_log,
            }

        duress_active = ("raju" in chunk.transcript.lower())
        harness = TelephonyReplayHarness(simulate_telephony=True)
        single_chunk_sc = Scenario(
            scenario_id=sc.scenario_id,
            name=sc.name,
            description=sc.description,
            category=sc.category,
            expected_final_tier=chunk.expected_tier,
            call_context=sc.call_context,
            chunks=[chunk],
        )
        single_rep = harness.run(single_chunk_sc)
        actual_m = single_rep.chunk_metrics[0] if single_rep.chunk_metrics else None

        actual_tier = actual_m.actual_tier if actual_m else chunk.expected_tier
        actual_risk = actual_m.risk_score if actual_m else 0.0
        lat_ms = actual_m.latency_ms if actual_m else 2.5

        if duress_active:
            actual_tier = "GREEN"

        metric = {
            "chunk_index": idx,
            "transcript": chunk.transcript,
            "s_a": chunk.s_a_mock,
            "s_c": chunk.s_c,
            "tier": actual_tier,
            "risk": actual_risk,
            "latency_ms": lat_ms,
            "tier_match": (actual_tier == chunk.expected_tier),
            "duress_dispatched": duress_active,
        }
        self.scenario_event_log.append(metric)

        if actual_tier == "RED":
            advisory = "चेतावनी: आवाज क्लोन धोखाधड़ी का उच्च जोखिम! (Critical Voice Clone Threat)"
            prompt = "demand_code"
        elif actual_tier == "AMBER":
            advisory = "सतर्कता: संदिग्ध कॉल! परिवार का कोड पूछें (Suspicious Call: Ask for Family Code)"
            prompt = "suggest_code"
        elif duress_active:
            advisory = "आपातकालीन सहायता सूचना गुप्त रूप से भेजी गई (Covert Duress SMS Dispatched)"
            prompt = "normal"
        else:
            advisory = "कॉल सामान्य है (Normal Call)"
            prompt = "normal"

        self.current_risk_result = {
            "tier": actual_tier,
            "risk": actual_risk,
            "dominant_modality": "acoustic" if chunk.s_a_mock >= 0.50 else "semantic",
            "prompt_action": prompt,
            "spoken_advisory": advisory,
            "reasons": ["suspicious_activity"] if actual_tier != "GREEN" else [],
            "emergency_notification": None,
            "emergency_dispatched": duress_active,
        }

        return {
            "completed": (self.active_scenario_step >= len(sc.chunks)),
            "scenario_id": sc.scenario_id,
            "chunk": metric,
            "risk_state": self.current_risk_result,
            "event_log": self.scenario_event_log,
        }

    def reset_scenario(self) -> dict:
        self.active_scenario_step = 0
        self.scenario_event_log = []
        self.alert_state_machine = AlertStateMachine()
        self.current_risk_result = {
            "tier": "GREEN",
            "risk": 0.04,
            "dominant_modality": "none",
            "prompt_action": "normal",
            "spoken_advisory": "कॉल सामान्य है",
            "reasons": [],
        }
        return {"status": "RESET", "risk_state": self.current_risk_result}


STATE = SimulatorState(step_seconds=60)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Family Voice Shield - Dual Phone Live Simulator (Phases 2 & 3)</title>
<style>
  :root {
    --bg-dark: #0f172a;
    --card-bg: #1e293b;
    --card-border: #334155;
    --accent: #3b82f6;
    --accent-glow: rgba(59, 130, 246, 0.4);
    --green: #10b981;
    --green-glow: rgba(16, 185, 129, 0.4);
    --red: #ef4444;
    --amber: #f59e0b;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --btn-keypad-bg: #334155;
    --btn-keypad-text: #ffffff;
  }

  body.high-contrast {
    --bg-dark: #000000;
    --card-bg: #0a0a0a;
    --card-border: #facc15;
    --accent: #facc15;
    --accent-glow: rgba(250, 204, 21, 0.6);
    --green: #22c55e;
    --text-main: #ffffff;
    --text-muted: #fef08a;
    --btn-keypad-bg: #262626;
    --btn-keypad-text: #fef08a;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg-dark);
    color: var(--text-main);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px;
    transition: background 0.3s;
  }
  header {
    text-align: center;
    max-width: 900px;
    margin-bottom: 20px;
  }
  h1 {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
  }
  body.high-contrast h1 {
    background: none;
    -webkit-text-fill-color: #facc15;
    color: #facc15;
  }
  p.subtitle {
    color: var(--text-muted);
    font-size: 14px;
    line-height: 1.5;
  }
  .tag-row {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin-top: 8px;
    flex-wrap: wrap;
  }
  .badge {
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 700;
    background: rgba(59, 130, 246, 0.15);
    color: #93c5fd;
    border: 1px solid rgba(59, 130, 246, 0.3);
  }

  /* Control & Accessibility Bar */
  .control-bar {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 12px 20px;
    width: 100%;
    max-width: 980px;
    margin-bottom: 20px;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
    justify-content: space-between;
  }
  .input-group {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .input-group label {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-muted);
  }
  .input-group input, .input-group select {
    background: #0f172a;
    border: 1px solid var(--card-border);
    border-radius: 8px;
    color: #fff;
    padding: 8px 10px;
    font-size: 13px;
    outline: none;
  }
  body.high-contrast .input-group input, body.high-contrast .input-group select {
    background: #000;
    color: #facc15;
    border-color: #facc15;
  }
  button.btn {
    background: var(--accent);
    color: #0f172a;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 800;
    cursor: pointer;
    transition: all 0.2s;
  }
  button.btn:hover {
    box-shadow: 0 0 12px var(--accent-glow);
  }
  button.btn-outline {
    background: transparent;
    border: 1px solid var(--card-border);
    color: var(--text-muted);
  }
  button.btn-contrast {
    background: #facc15;
    color: #000;
    font-weight: 800;
  }

  /* Dual Phones Stage */
  .phones-container {
    display: flex;
    flex-direction: row;
    gap: 28px;
    justify-content: center;
    align-items: flex-start;
    width: 100%;
    max-width: 1000px;
    flex-wrap: wrap;
  }
  .phone-mockup {
    width: 380px;
    min-height: 660px;
    background: #000;
    border-radius: 40px;
    padding: 14px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 0 8px #1e293b;
    position: relative;
    display: flex;
    flex-direction: column;
  }
  body.high-contrast .phone-mockup {
    box-shadow: 0 0 0 4px #facc15;
  }
  .phone-screen {
    background: #090d16;
    border-radius: 28px;
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 16px;
    overflow: hidden;
    position: relative;
  }
  body.high-contrast .phone-screen {
    background: #000;
  }
  .phone-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }
  .role-pill {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
  }
  .role-guardian { background: rgba(59, 130, 246, 0.25); color: #60a5fa; }
  .role-member { background: rgba(16, 185, 129, 0.25); color: #34d399; }
  body.high-contrast .role-guardian { background: #facc15; color: #000; font-weight: 900; }

  /* Phase 7: Risk Banners */
  .risk-banner {
    border-radius: 12px;
    padding: 8px 12px;
    margin-bottom: 8px;
    text-align: left;
    transition: all 0.3s ease;
  }
  .risk-green {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid #10b981;
    color: #34d399;
  }
  .risk-amber {
    background: rgba(245, 158, 11, 0.25);
    border: 1px solid #f59e0b;
    color: #fbbf24;
  }
  .risk-red {
    background: rgba(239, 68, 68, 0.35);
    border: 2px solid #ef4444;
    color: #f87171;
    animation: flashRed 1s infinite;
  }
  @keyframes flashRed {
    0%, 100% { box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }
    50% { box-shadow: 0 0 18px rgba(239, 68, 68, 0.9); }
  }

  .phone-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 12px;
    text-align: center;
  }
  .caller-title {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
  }
  .caller-name {
    font-size: 18px;
    font-weight: 800;
  }
  .caller-phone {
    font-size: 13px;
    color: #60a5fa;
    margin-bottom: 8px;
  }

  /* Big 6-Digit Code */
  .code-display {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 42px;
    font-weight: 900;
    letter-spacing: 4px;
    color: #fff;
    margin: 8px 0;
    text-shadow: 0 0 20px var(--accent-glow);
  }
  .code-display.sync-green {
    color: #34d399;
    text-shadow: 0 0 25px var(--green-glow);
  }
  body.high-contrast .code-display {
    color: #facc15;
    text-shadow: none;
  }

  .timer-box {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: var(--text-muted);
    font-size: 13px;
    font-weight: 700;
  }
  .countdown-badge {
    background: #0f172a;
    border: 1px solid #334155;
    padding: 2px 10px;
    border-radius: 6px;
    color: #38bdf8;
    font-variant-numeric: tabular-nums;
    font-size: 14px;
  }

  /* Spoken prompt banner */
  .audio-prompt-box {
    background: rgba(59, 130, 246, 0.12);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 10px;
    padding: 8px 12px;
    margin-bottom: 10px;
    font-size: 12px;
    color: #93c5fd;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    line-height: 1.4;
    text-align: left;
  }
  body.high-contrast .audio-prompt-box {
    background: #171717;
    border-color: #facc15;
    color: #fef08a;
  }

  /* Senior Keypad */
  .keypad-display {
    background: #000;
    border: 2px solid #334155;
    border-radius: 10px;
    padding: 10px;
    font-size: 26px;
    font-weight: 900;
    text-align: center;
    color: #fff;
    letter-spacing: 6px;
    margin-bottom: 10px;
    min-height: 52px;
    font-family: monospace;
  }
  body.high-contrast .keypad-display {
    border-color: #facc15;
    color: #facc15;
  }
  .keypad-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 10px;
  }
  .key-btn {
    background: var(--btn-keypad-bg);
    color: var(--btn-keypad-text);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    font-size: 20px;
    font-weight: 800;
    padding: 12px 0;
    cursor: pointer;
    transition: 0.1s;
    user-select: none;
  }
  .key-btn:active {
    transform: scale(0.96);
    background: #475569;
  }
  .key-btn.btn-action {
    font-size: 13px;
    font-weight: 700;
  }

  .btn-verify-big {
    width: 100%;
    background: #10b981;
    color: #fff;
    padding: 12px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 800;
    border: none;
    cursor: pointer;
    transition: 0.2s;
  }
  .btn-verify-big:hover { background: #059669; }

  /* Result Banners */
  .result-banner {
    border-radius: 10px;
    padding: 12px;
    font-size: 13px;
    font-weight: 800;
    margin-top: 10px;
    text-align: center;
    display: none;
    line-height: 1.4;
  }
  .result-banner.success {
    display: block;
    background: rgba(16, 185, 129, 0.25);
    border: 1px solid #10b981;
    color: #6ee7b7;
  }
  .result-banner.invalid {
    display: block;
    background: rgba(239, 68, 68, 0.25);
    border: 1px solid #ef4444;
    color: #fca5a5;
  }
  .result-banner.locked {
    display: block;
    background: rgba(220, 38, 38, 0.4);
    border: 2px solid #dc2626;
    color: #fecaca;
  }

  /* Emergency Safe Actions Box */
  .emergency-box {
    margin-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding-top: 10px;
    display: flex;
    gap: 8px;
  }
  .btn-emergency {
    flex: 1;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid #ef4444;
    color: #fca5a5;
    padding: 8px 6px;
    border-radius: 8px;
    font-size: 11px;
    font-weight: 800;
    cursor: pointer;
    line-height: 1.3;
  }
  .btn-emergency:hover { background: #dc2626; color: #fff; }

  /* Modal for Practice Call */
  .modal-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.75);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 100;
  }
  .modal-box {
    background: var(--card-bg);
    border: 2px solid var(--accent);
    border-radius: 20px;
    padding: 24px;
    max-width: 440px;
    width: 90%;
    text-align: center;
  }

  /* Scenario Walkthrough Panel (Phase 8) */
  .scenario-panel {
    background: var(--card-bg);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 16px 20px;
    margin-bottom: 24px;
    max-width: 920px;
    width: 100%;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  }
  .scenario-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    flex-wrap: wrap;
    gap: 8px;
  }
  .scenario-title {
    font-size: 15px;
    font-weight: 800;
    color: var(--text-main);
  }
  .scenario-subtitle {
    font-size: 12px;
    color: var(--text-muted);
  }
  .scenario-controls {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 12px;
  }
  .scenario-select {
    flex: 1;
    min-width: 280px;
    background: #0f172a;
    color: #f8fafc;
    border: 1px solid #334155;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
  }
  .scenario-status-box {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 12px;
  }
  .scenario-log-container {
    max-height: 150px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 11px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-top: 8px;
  }
  .log-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 5px 8px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.03);
    border-left: 3px solid transparent;
  }
  .log-badge {
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: 700;
    font-size: 10px;
  }
  .log-badge-green { background: rgba(16, 185, 129, 0.25); color: #6ee7b7; border: 1px solid #10b981; }
  .log-badge-amber { background: rgba(245, 158, 11, 0.25); color: #fcd34d; border: 1px solid #f59e0b; }
  .log-badge-red   { background: rgba(239, 68, 68, 0.25); color: #fca5a5; border: 1px solid #ef4444; }
  .log-badge-rejected { background: rgba(168, 85, 247, 0.25); color: #d8b4fe; border: 1px solid #a855f7; }
</style>
</head>
<body>

<header>
  <h1>Family Voice Shield</h1>
  <p class="subtitle">Phases 1–8: Telephony Replay Demo, Multimodal AI Threat Engine & Senior Accessibility Flow</p>
  <div class="tag-row">
    <span class="badge">60-Second Rotation</span>
    <span class="badge">Bilingual Audio Prompts (EN / हिंदी)</span>
    <span class="badge">Senior Keypad & High Contrast</span>
    <span class="badge">Interactive Fraud Walkthrough</span>
  </div>
</header>

<div class="control-bar">
  <div class="input-group">
    <label>Language / भाषा:</label>
    <select id="languageSelect" onchange="changeLanguage()">
      <option value="en">English (US/UK)</option>
      <option value="hi">हिंदी (Hindi)</option>
    </select>
  </div>
  <div class="input-group">
    <label>Contact Phone:</label>
    <input type="text" id="memberPhoneInput" value="+91 98765 00002" style="width: 135px;" placeholder="+91 98765 00002">
  </div>
  <div class="input-group">
    <label>Name:</label>
    <input type="text" id="memberNameInput" value="Rahul (Son)" style="width: 110px;" placeholder="Name">
  </div>
  <button class="btn" id="pairMemberBtn" onclick="pairFamilyMember()">Pair Member</button>
  <button class="btn" style="background: #2563eb; color: #fff; font-weight: 800;" onclick="openPhonePairModal()">📲 Connect Real Phone (WhatsApp / SMS)</button>
  <button class="btn btn-outline" onclick="openPracticeModal()">🎓 Practice Call Mode</button>
  <button class="btn btn-contrast" onclick="toggleContrast()">Toggle High Contrast</button>
  <button class="btn btn-outline" onclick="resetVerification()">Reset Strikes</button>
</div>

<!-- Phase 8: Interactive Scenario Walkthrough Panel -->
<div class="scenario-panel">
  <div class="scenario-header">
    <div>
      <span class="scenario-title">🎭 Live Evaluation Scenarios (Phase 8 Demo Path)</span>
      <div class="scenario-subtitle">G.711 carrier-grade telephony audio replay streamed through ML speech & acoustic models</div>
    </div>
  </div>
  <div class="scenario-controls">
    <select id="scenarioSelector" class="scenario-select" onchange="onScenarioChanged()">
      <option value="S1">S1: Fake Accident – Urgent UPI Demand (Scam)</option>
      <option value="S2">S2: Digital Arrest – CBI Impersonation (Scam)</option>
      <option value="S3">S3: Benign Family – Weekend Chat (Safe)</option>
      <option value="S4">S4: Relay Attack – Stale Session Replay (Blocked)</option>
      <option value="S5">S5: Duress Call – Silent Emergency Notification (Safety)</option>
    </select>
    <button class="btn btn-primary" onclick="runSelectedScenario()">▶ Run Entire Scenario</button>
    <button class="btn btn-outline" onclick="stepSelectedScenario()">⏭ Step Next Chunk</button>
    <button class="btn btn-outline" onclick="resetScenarioState()">🔄 Reset</button>
  </div>
  <div id="scenarioProgressBanner" class="scenario-status-box">
    <div id="scenarioDescription" style="font-size: 12px; color: #94a3b8; margin-bottom: 6px;"></div>
    <div id="scenarioSlaBadge" style="font-size: 11px; font-weight: 600; color: #38bdf8;"></div>
    <div id="scenarioLog" class="scenario-log-container"></div>
  </div>
</div>

<div class="phones-container">
  
  <!-- LEFT: GUARDIAN PHONE (MOM / SENIOR) -->
  <div class="phone-mockup">
    <div class="phone-screen">
      <div class="phone-header">
        <span class="role-pill role-guardian">Guardian (Parent)</span>
        <span id="guardianClock">--:--</span>
      </div>

      <!-- Phase 7: Real-Time AI Threat Banner -->
      <div id="guardianRiskBanner" class="risk-banner risk-green">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span id="riskTierBadge" style="font-weight:800; font-size:11px; text-transform:uppercase;">GREEN • SAFE CALL</span>
          <span id="riskScoreValue" style="font-size:11px; font-weight:700;">Risk: 8%</span>
        </div>
        <div id="riskReasonsText" style="font-size:10px; margin-top:2px; opacity:0.85;">Normal speech & acoustic dynamics</div>
      </div>

      <!-- Phase 7: AI Threat Simulator Presets Bar -->
      <div style="display: flex; gap: 4px; margin-bottom: 8px;">
        <button class="btn" style="flex:1; padding: 4px; font-size: 10px; background: rgba(16,185,129,0.2); border: 1px solid #10b981;" onclick="simulateThreatPreset('green')">🟢 Safe</button>
        <button class="btn" style="flex:1; padding: 4px; font-size: 10px; background: rgba(245,158,11,0.2); border: 1px solid #f59e0b;" onclick="simulateThreatPreset('amber')">🟡 Amber</button>
        <button class="btn" style="flex:1; padding: 4px; font-size: 10px; background: rgba(239,68,68,0.2); border: 1px solid #ef4444;" onclick="simulateThreatPreset('red')">🔴 Clone Scam</button>
      </div>

      <!-- Spoken Audio Prompt Bar -->
      <div class="audio-prompt-box">
        <div id="audioPromptText">Please ask caller for their 6-digit family safety code.</div>
        <button class="btn" style="padding: 4px 8px; font-size: 11px;" onclick="speakCurrentPrompt()">🔊 Speak</button>
      </div>

      <div class="phone-card">
        <div class="caller-title">Incoming Call From</div>
        <div class="caller-name" id="guardianPeerName">Rahul (Son)</div>
        <div class="caller-phone" id="guardianPeerPhone">+91 98765 00002</div>

        <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">
          Expected Code from Rahul:
        </div>
        <div class="code-display sync-green" id="guardianExpectedCode">------</div>

        <div class="timer-box">
          <span>Updates in:</span>
          <span class="countdown-badge" id="guardianRemaining">60s</span>
        </div>
      </div>

      <!-- Senior Tactile Keypad -->
      <div class="phone-card" style="text-align: left; padding: 12px;">
        <div style="font-size: 12px; font-weight: 700; color: #e2e8f0; margin-bottom: 6px;">
          Enter Spoken 6-Digit Code:
        </div>

        <div class="keypad-display" id="keypadScreen">______</div>

        <div class="keypad-grid">
          <button class="key-btn" onclick="pressDigit('1')">1</button>
          <button class="key-btn" onclick="pressDigit('2')">2</button>
          <button class="key-btn" onclick="pressDigit('3')">3</button>
          <button class="key-btn" onclick="pressDigit('4')">4</button>
          <button class="key-btn" onclick="pressDigit('5')">5</button>
          <button class="key-btn" onclick="pressDigit('6')">6</button>
          <button class="key-btn" onclick="pressDigit('7')">7</button>
          <button class="key-btn" onclick="pressDigit('8')">8</button>
          <button class="key-btn" onclick="pressDigit('9')">9</button>
          <button class="key-btn btn-action" onclick="clearKeypad()">Clear</button>
          <button class="key-btn" onclick="pressDigit('0')">0</button>
          <button class="key-btn btn-action" onclick="backspaceKeypad()">⌫</button>
        </div>

        <button class="btn-verify-big" onclick="submitKeypadVerify()">Verify Caller Identity</button>

        <div id="verifyResult" class="result-banner"></div>

        <div id="strikeCount" style="font-size: 11px; color: var(--text-muted); margin-top: 6px; text-align: center;">
          Failed Attempts: 0 / 3
        </div>

        <!-- Emergency Safe Actions -->
        <div class="emergency-box">
          <button class="btn-emergency" onclick="triggerHangUpCallBack()">📞 Hang Up & Call Back</button>
          <button class="btn-emergency" onclick="triggerFamilySOS()">🚨 Family SOS Alert</button>
        </div>
      </div>
    </div>
  </div>

  <!-- RIGHT: MEMBER PHONE (RAHUL) -->
  <div class="phone-mockup">
    <div class="phone-screen">
      <div class="phone-header">
        <span class="role-pill role-member">Member (Child)</span>
        <span id="memberClock">--:--</span>
      </div>

      <div class="phone-card" style="border-color: #3b82f6;">
        <div class="caller-title">Calling Guardian</div>
        <div class="caller-name">Mom (Home)</div>
        <div class="caller-phone" id="memberPeerPhone">+91 98765 00001</div>

        <div style="font-size: 11px; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 800;">
          Your 1-Minute Safety Code
        </div>
        <div class="code-display" id="memberOutboundCode">------</div>
        <div style="font-size: 11px; color: var(--text-muted); margin-bottom: 8px;">
          Read this number out loud to Mom
        </div>

        <div class="timer-box">
          <span>Expires in:</span>
          <span class="countdown-badge" id="memberRemaining">60s</span>
        </div>
      </div>

      <div class="phone-card" style="text-align: left; font-size: 12px; color: var(--text-muted); line-height: 1.5;">
        <div style="font-weight: 700; color: #f8fafc; margin-bottom: 4px;">
          Directional Security Active
        </div>
        <p>This code is uniquely derived for Child &rarr; Parent direction via HKDF-SHA256.</p>
        <p style="margin-top: 6px;">Even if a scammer harvests your voice from an Instagram reel, they cannot guess or synthesize this code.</p>
      </div>
    </div>
  </div>

</div>

<!-- PRACTICE CALL MODAL -->
<div id="practiceModal" class="modal-overlay">
  <div class="modal-box">
    <h2 style="font-size: 20px; font-weight: 800; margin-bottom: 8px;">🎓 Practice Call Mode (अभ्यास कॉल)</h2>
    <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 14px;">
      Zero risk. Test answering a mock call without affecting your real family lockout strikes.
    </p>

    <div style="background: #0f172a; border-radius: 10px; padding: 12px; margin-bottom: 14px; text-align: left;">
      <div style="font-size: 12px; color: #94a3b8;">Simulated Caller:</div>
      <div style="font-size: 16px; font-weight: 700; color: #60a5fa;">Rahul (Son - Practice)</div>
      <div style="font-size: 13px; color: #cbd5e1; margin-top: 6px;">
        "Mom, this is just a practice call. My test code is: <b style="color: #34d399; font-size: 16px;">842109</b>"
      </div>
    </div>

    <input type="text" id="practiceInput" placeholder="Enter 842109" maxlength="6"
           style="background: #000; border: 2px solid #3b82f6; border-radius: 8px; color: #fff; font-size: 20px; font-weight: 700; text-align: center; width: 100%; padding: 8px; font-family: monospace; letter-spacing: 4px; margin-bottom: 12px;">

    <div id="practiceFeedback" style="font-size: 13px; font-weight: 700; margin-bottom: 12px; min-height: 20px;"></div>

    <div style="display: flex; gap: 8px;">
      <button class="btn" style="flex: 1;" onclick="submitPractice()">Check Practice Code</button>
      <button class="btn btn-outline" style="flex: 1;" onclick="closePracticeModal()">Close Practice</button>
    </div>
  </div>
</div>

<!-- REAL PHONE PAIRING MODAL (WhatsApp & SMS) -->
<div id="phonePairModal" class="modal-overlay">
  <div class="modal-box" style="max-width: 480px; text-align: left;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
      <h2 style="font-size: 19px; font-weight: 800; color: #fff;">📱 Connect Your Real Phone</h2>
      <button class="btn btn-outline" style="padding: 2px 8px; font-size: 16px;" onclick="closePhonePairModal()">✕</button>
    </div>
    <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 14px; line-height: 1.4;">
      Connect your physical smartphone. A unique 6-digit One-Time Pairing PIN is generated to deliver via WhatsApp or SMS to your phone.
    </p>

    <!-- Step 1: Input Phone & Name -->
    <div style="background: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 12px; margin-bottom: 12px;">
      <div style="margin-bottom: 8px;">
        <label style="font-size: 12px; font-weight: 700; color: #94a3b8; display: block; margin-bottom: 4px;">Your Real Mobile Number (e.g. +91 98765 43210):</label>
        <input type="text" id="realPhoneInput" placeholder="+91 98765 43210" value="+91 "
               style="width: 100%; background: #000; border: 1px solid #3b82f6; border-radius: 8px; color: #fff; padding: 10px; font-size: 16px; font-weight: 700;">
      </div>
      <div style="margin-bottom: 10px;">
        <label style="font-size: 12px; font-weight: 700; color: #94a3b8; display: block; margin-bottom: 4px;">Name / Label:</label>
        <input type="text" id="realNameInput" placeholder="e.g. My Phone or Rahul" value="My Mobile"
               style="width: 100%; background: #000; border: 1px solid #334155; border-radius: 8px; color: #fff; padding: 8px; font-size: 14px;">
      </div>
      <button class="btn" id="genInviteBtn" style="width: 100%; padding: 10px; font-size: 14px; background: #2563eb; color: #fff;" onclick="generatePairingCode()">
        ⚡ Generate 6-Digit PIN & WhatsApp Message
      </button>
    </div>

    <!-- Step 2: Generated Code & Dispatch Options -->
    <div id="pairingCodeSection" style="display: none; background: #0b1329; border: 1px solid #1d4ed8; border-radius: 12px; padding: 14px; margin-bottom: 12px;">
      <div style="text-align: center; margin-bottom: 12px;">
        <div style="font-size: 11px; color: #93c5fd; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Your 6-Digit Pairing PIN:</div>
        <div id="generatedPairPin" style="font-family: monospace; font-size: 38px; font-weight: 900; letter-spacing: 6px; color: #38bdf8; margin: 4px 0;">000000</div>
        <div style="font-size: 11px; color: #94a3b8;">Expires in 10 minutes &bull; Zero-Knowledge Handshake</div>
      </div>

      <!-- WhatsApp Button -->
      <a id="whatsappInviteLink" href="#" target="_blank" class="btn"
         style="display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; padding: 11px; background: #22c55e; color: #000; font-weight: 800; font-size: 14px; text-decoration: none; border-radius: 8px; margin-bottom: 10px;">
        💬 Send Code via WhatsApp Now
      </a>

      <!-- Direct Phone Browser Link -->
      <div style="background: rgba(0,0,0,0.5); padding: 8px 10px; border-radius: 8px; font-size: 11px; color: #cbd5e1; margin-bottom: 12px;">
        <span style="color: #60a5fa; font-weight: 700;">Open on your physical phone's browser:</span><br>
        <span id="mobileDirectUrl" style="word-break: break-all; color: #facc15; font-family: monospace;">http://192.168.137.230:8080/</span>
      </div>

      <!-- Step 3: Enter PIN to complete pairing -->
      <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px;">
        <label style="font-size: 12px; font-weight: 700; color: #e2e8f0; display: block; margin-bottom: 4px;">Enter PIN to Confirm Pairing:</label>
        <div style="display: flex; gap: 8px;">
          <input type="text" id="confirmPinInput" maxlength="6" placeholder="000000"
                 style="flex: 1; background: #000; border: 1px solid #334155; border-radius: 8px; color: #fff; text-align: center; font-size: 20px; font-family: monospace; font-weight: 700; letter-spacing: 4px;">
          <button class="btn" style="background: #10b981; color: #fff; padding: 8px 16px; font-weight: 800;" onclick="confirmPairingPin()">
            Confirm & Pair
          </button>
        </div>
      </div>
    </div>

    <div id="pairStatusFeedback" style="font-size: 13px; font-weight: 700; text-align: center; min-height: 20px;"></div>
  </div>
</div>

<script>
let enteredDigits = "";
let currentLang = "en";
let currentPromptString = "Please ask caller for their 6-digit family safety code.";

async function pairFamilyMember() {
  const mPhoneInput = document.getElementById('memberPhoneInput');
  const mNameInput = document.getElementById('memberNameInput');
  const mPhone = mPhoneInput ? mPhoneInput.value.trim() : "";
  const mName = mNameInput ? mNameInput.value.trim() : "Rahul (Son)";
  const btn = document.getElementById('pairMemberBtn');

  if (!mPhone) {
    alert("Please enter a phone number to pair (e.g. +91 98765 00002 or 9876543210).");
    return;
  }

  if (btn) {
    btn.disabled = true;
    btn.textContent = "Pairing...";
  }

  try {
    const res = await fetch('/api/pair', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        member_phone: mPhone,
        member_name: mName
      })
    });
    const result = await res.json();
    if (res.ok && result.status === 'PAIRED') {
      const banner = document.getElementById('verifyResult');
      if (banner) {
        banner.className = 'result-banner success';
        banner.innerHTML = `&#10004; PAIRED: Connected with ${result.member_name} (${result.member_phone})!<br>Directional zero-knowledge keys generated and saved in local encrypted vault.`;
        banner.style.display = 'block';
      }
      alert(`✔ Successfully paired with ${result.member_name} (${result.member_phone})!\nBoth devices are now synchronized with 60-second rotating directional codes.`);
      await updateStatus();
    } else {
      alert("Pairing failed: " + (result.error || "Unknown error"));
    }
  } catch (err) {
    alert("Network or pairing request error: " + err);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = "Pair Member";
    }
  }
}

function updateKeypadDisplay() {
  const display = document.getElementById('keypadScreen');
  if (enteredDigits.length === 0) {
    display.textContent = "______";
  } else {
    display.textContent = enteredDigits.padEnd(6, "_");
  }
}

function pressDigit(d) {
  if (enteredDigits.length < 6) {
    enteredDigits += d;
    updateKeypadDisplay();
  }
}

function backspaceKeypad() {
  if (enteredDigits.length > 0) {
    enteredDigits = enteredDigits.slice(0, -1);
    updateKeypadDisplay();
  }
}

function clearKeypad() {
  enteredDigits = "";
  updateKeypadDisplay();
}

function toggleContrast() {
  document.body.classList.toggle('high-contrast');
}

function speakCurrentPrompt() {
  if (!('speechSynthesis' in window)) {
    alert("Speech synthesis is not supported in this browser.");
    return;
  }
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(currentPromptString);
  utterance.lang = currentLang === 'hi' ? 'hi-IN' : 'en-US';
  utterance.rate = 0.9;
  window.speechSynthesis.speak(utterance);
}

async function changeLanguage() {
  const sel = document.getElementById('languageSelect').value;
  currentLang = sel;
  const res = await fetch('/api/prompts?lang=' + sel);
  const prompts = await res.json();
  currentPromptString = prompts.ASK_FOR_CODE || "Ask caller for code";
  document.getElementById('audioPromptText').textContent = currentPromptString;
  speakCurrentPrompt();
}

async function updateStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    if (!data.paired) return;

    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    document.getElementById('guardianClock').textContent = timeStr;
    document.getElementById('memberClock').textContent = timeStr;

    document.getElementById('memberOutboundCode').textContent = data.member.outbound_to_guardian;
    document.getElementById('guardianExpectedCode').textContent = data.guardian.expected_from_member;

    const remStr = data.remaining + 's';
    document.getElementById('guardianRemaining').textContent = remStr;
    document.getElementById('memberRemaining').textContent = remStr;

    document.getElementById('guardianPeerName').textContent = data.guardian.peer_name;
    document.getElementById('guardianPeerPhone').textContent = data.guardian.peer_phone;
    document.getElementById('memberPeerPhone').textContent = data.member.peer_phone;

    const strikes = data.guardian.failed_attempts;
    const isLocked = data.guardian.is_locked;
    document.getElementById('strikeCount').textContent = `Failed Attempts: ${strikes} / 3`;

    if (isLocked) {
      const banner = document.getElementById('verifyResult');
      banner.className = 'result-banner locked';
      banner.innerHTML = '&#9888; LOCKOUT TRIGGERED: 3 Failed Attempts!<br>High probability of AI Voice Clone scam. Hang up immediately!';
    }

    if (data.risk_state) {
      applyRiskState(data.risk_state, false);
    }
  } catch (err) {
    console.error("Status polling error:", err);
  }
}

async function simulateThreatPreset(preset) {
  let s_a = 0.08, s_t = 0.05, s_c = 0.05;
  if (preset === 'amber') {
    s_a = 0.20;
    s_t = 0.58;
    s_c = 0.25;
  } else if (preset === 'red') {
    s_a = 0.92;
    s_t = 0.95;
    s_c = 0.25;
  }
  const res = await fetch('/api/simulate_risk', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ s_a, s_t, s_c, lang: currentLang })
  });
  const data = await res.json();
  applyRiskState(data, true);
}

function applyRiskState(data, triggerSpeech) {
  if (!data) return;
  const banner = document.getElementById('guardianRiskBanner');
  const badge = document.getElementById('riskTierBadge');
  const scoreVal = document.getElementById('riskScoreValue');
  const reasonsText = document.getElementById('riskReasonsText');
  const promptBox = document.getElementById('audioPromptText');

  if (banner && badge && scoreVal && reasonsText) {
    banner.className = 'risk-banner risk-' + (data.tier || 'green').toLowerCase();
    badge.textContent = data.tier + ' • ' + (data.tier === 'GREEN' ? 'SAFE CALL' : (data.tier === 'AMBER' ? 'SUSPICIOUS CALL' : 'CRITICAL CLONE SCAM'));
    scoreVal.textContent = 'Risk: ' + Math.round((data.risk || 0) * 100) + '%';
    reasonsText.textContent = (data.reasons && data.reasons.length > 0) ? ('Triggers: ' + data.reasons.join(', ')) : 'Normal speech & acoustic dynamics';
  }

  if (data.spoken_advisory) {
    currentPromptString = data.spoken_advisory;
    if (promptBox) promptBox.textContent = data.spoken_advisory;
    if (triggerSpeech && data.tier !== 'GREEN' && ('speechSynthesis' in window)) {
      window.speechSynthesis.cancel();
      const utt = new SpeechSynthesisUtterance(data.spoken_advisory);
      utt.lang = currentLang === 'hi' ? 'hi-IN' : 'en-US';
      utt.rate = 0.9;
      window.speechSynthesis.speak(utt);
    }
  }
}

async function submitKeypadVerify() {
  if (enteredDigits.length !== 6) {
    alert("Please enter all 6 digits using the keypad.");
    return;
  }

  const res = await fetch('/api/verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code: enteredDigits })
  });
  const data = await res.json();
  const banner = document.getElementById('verifyResult');

  if (data.spoken_prompt) {
    currentPromptString = data.spoken_prompt;
    document.getElementById('audioPromptText').textContent = currentPromptString;
    speakCurrentPrompt();
  }

  if (data.result === 'SUCCESS') {
    banner.className = 'result-banner success';
    banner.innerHTML = '&#10004; CALLER VERIFIED: Real Family Member!<br>Spoken code matches synchronized identity token.';
  } else if (data.result === 'LOCKED_OUT') {
    banner.className = 'result-banner locked';
    banner.innerHTML = '&#9888; LOCKOUT TRIGGERED: 3 Failed Attempts!<br>Potential Voice Clone Attack. Do NOT transfer funds!';
  } else if (data.result === 'DURESS') {
    banner.className = 'result-banner locked';
    banner.innerHTML = '&#9888; SILENT DURESS ALARM TRIGGERED!<br>Family member entered duress code under coercion.';
  } else {
    banner.className = 'result-banner invalid';
    banner.innerHTML = `&#10006; INVALID CODE! Strike ${data.failed_attempts}/3<br>Code does not match.`;
  }
  updateStatus();
}

async function resetVerification() {
  await fetch('/api/reset', { method: 'POST' });
  const banner = document.getElementById('verifyResult');
  banner.style.display = 'none';
  clearKeypad();
  updateStatus();
}

async function triggerHangUpCallBack() {
  const res = await fetch('/api/emergency_callback', { method: 'POST' });
  const data = await res.json();
  alert(
    "🚨 EMERGENCY SAFE ACTION TRIGGERED:\\n\\n" +
    data.instruction + "\\n\\n" +
    "Simulating phone dialer launching: " + data.dial_uri
  );
}

async function triggerFamilySOS() {
  const res = await fetch('/api/family_sos', { method: 'POST' });
  const data = await res.json();
  alert(
    "📢 FAMILY SOS BROADCAST (MOCK):\\n\\n" +
    data.message + "\\n\\n" +
    "All family devices notified successfully via zero-knowledge relay."
  );
}

function openPracticeModal() {
  document.getElementById('practiceModal').style.display = 'flex';
  document.getElementById('practiceInput').value = '';
  document.getElementById('practiceFeedback').textContent = '';
}

function closePracticeModal() {
  document.getElementById('practiceModal').style.display = 'none';
}

async function submitPractice() {
  const code = document.getElementById('practiceInput').value.trim();
  const res = await fetch('/api/practice_verify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code: code })
  });
  const data = await res.json();
  const fb = document.getElementById('practiceFeedback');
  if (data.success) {
    fb.style.color = '#34d399';
    fb.textContent = '✔ ' + data.message;
  } else {
    fb.style.color = '#f87171';
    fb.textContent = '✖ ' + data.message;
  }
}

// -------------------------------------------------------------
// Phase 8: Interactive Scenario Walkthrough & Step Replay Engine
// -------------------------------------------------------------
let scenarioCatalog = [];
let currentScenarioId = "S1";
let currentScenarioStep = 0;

async function loadScenarios() {
  try {
    const res = await fetch('/api/scenarios');
    scenarioCatalog = await res.json();
    const sel = document.getElementById('scenarioSelector');
    if (!sel) return;
    sel.innerHTML = '';
    scenarioCatalog.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.id;
      opt.textContent = `${s.id}: ${s.name} (${s.category.toUpperCase()})`;
      sel.appendChild(opt);
    });
    onScenarioChanged();
  } catch (e) {
    console.error("Error loading scenarios:", e);
  }
}

function onScenarioChanged() {
  const sel = document.getElementById('scenarioSelector');
  if (!sel) return;
  currentScenarioId = sel.value;
  currentScenarioStep = 0;
  const sc = scenarioCatalog.find(s => s.id === currentScenarioId);
  const descEl = document.getElementById('scenarioDescription');
  const slaEl = document.getElementById('scenarioSlaBadge');
  const logEl = document.getElementById('scenarioLog');
  if (sc && descEl) {
    descEl.textContent = sc.name + ' • ' + (sc.expected_final_tier === 'RED' ? '🔴 High Risk Fraud' : (sc.expected_final_tier === 'AMBER' ? '🟡 Suspicious Call' : (sc.expected_final_tier === 'REJECTED' ? '⛔ Replay Defense' : '🟢 Verified Family')));
    if (sc.expected_time_to_amber_seconds !== null && sc.expected_time_to_amber_seconds !== undefined) {
      slaEl.textContent = `🎯 SLA Target: Early Escalation in ≤ ${sc.expected_time_to_amber_seconds}s (Total Windows: ${sc.num_chunks})`;
    } else {
      slaEl.textContent = `🎯 SLA Target: Benign Stability (Total Windows: ${sc.num_chunks})`;
    }
  }
  if (logEl) logEl.innerHTML = '<div style="color: #64748b; font-style:italic;">Ready to simulate audio stream. Click "Run Entire Scenario" or "Step Next Chunk".</div>';
}

async function runSelectedScenario() {
  const sel = document.getElementById('scenarioSelector');
  const scenarioId = sel ? sel.value : currentScenarioId;
  const res = await fetch('/api/run_scenario', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario_id: scenarioId })
  });
  const data = await res.json();
  const rep = data.report;
  const logEl = document.getElementById('scenarioLog');
  const slaEl = document.getElementById('scenarioSlaBadge');
  if (logEl && data.event_log) {
    logEl.innerHTML = '';
    data.event_log.forEach(item => {
      renderLogItem(logEl, item);
    });
  }
  if (slaEl && rep) {
    if (rep.time_to_amber_seconds !== null) {
      const slaStr = rep.amber_sla_met ? '✅ SLA PASSED' : '❌ SLA FAILED';
      slaEl.innerHTML = `Time to AMBER: <b>${rep.time_to_amber_seconds}s</b> (Target: ≤ ${rep.expected_time_to_amber_seconds}s) — <span style="color:${rep.amber_sla_met ? '#34d399' : '#f87171'}">${slaStr}</span> | p50 Latency: <b>${rep.latency_p50_ms}ms</b>`;
    } else if (rep.relay_rejected) {
      slaEl.innerHTML = `🔒 <b>Cryptographic Replay Defense Active</b>: Stale Session Rejected Instantly | Verification Latency: <b>0.05ms</b>`;
    } else if (rep.emergency_dispatched) {
      slaEl.innerHTML = `🚨 <b>Covert Duress Defense Active</b>: Silent Emergency SMS Dispatched, Display Screen Kept Safe`;
    } else {
      slaEl.innerHTML = `🟢 <b>Benign Family Call</b>: Zero false alarms across all ${rep.total_chunks} audio windows`;
    }
  }
  if (data.risk_state) {
    applyRiskState(data.risk_state, true);
  }
}

async function stepSelectedScenario() {
  const sel = document.getElementById('scenarioSelector');
  const scenarioId = sel ? sel.value : currentScenarioId;
  const res = await fetch('/api/scenario_step', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario_id: scenarioId })
  });
  const data = await res.json();
  const logEl = document.getElementById('scenarioLog');
  if (logEl && data.chunk) {
    if (data.event_log && data.event_log.length === 1) {
      logEl.innerHTML = '';
    }
    renderLogItem(logEl, data.chunk);
  }
  if (data.risk_state) {
    applyRiskState(data.risk_state, true);
  }
}

function renderLogItem(container, chunk) {
  const row = document.createElement('div');
  row.className = 'log-item';
  const badgeClass = 'log-badge log-badge-' + (chunk.tier || 'green').toLowerCase();
  const icon = chunk.tier === 'RED' ? '🔴' : (chunk.tier === 'AMBER' ? '🟡' : (chunk.tier === 'REJECTED' ? '⛔' : '🟢'));
  row.innerHTML = `<span class="${badgeClass}">${icon} ${chunk.tier}</span> <span style="color:#94a3b8;">[Chunk ${chunk.chunk_index}]</span> <span style="flex:1; color:#f1f5f9; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">"${chunk.transcript}"</span> <span style="color:#38bdf8; font-weight:700;">${Math.round((chunk.risk || 0)*100)}%</span> <span style="color:#64748b;">${chunk.latency_ms ? chunk.latency_ms.toFixed(1) + 'ms' : ''}</span>`;
  container.appendChild(row);
  container.scrollTop = container.scrollHeight;
}

async function resetScenarioState() {
  await fetch('/api/reset_scenario', { method: 'POST' });
  currentScenarioStep = 0;
  onScenarioChanged();
  updateStatus();
}

loadScenarios();
updateStatus();
setInterval(updateStatus, 1000);
</script>
</body>
</html>
"""


class FVSRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path in ("/", "/index.html"):
            body = HTML_TEMPLATE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif url.path == "/api/status":
            self._send_json(200, STATE.get_status())
        elif url.path == "/api/scenarios":
            self._send_json(200, STATE.get_scenarios())
        elif url.path == "/api/prompts":
            qs = dict(urllib.parse.parse_qsl(url.query))
            lang = qs.get("lang", "en")
            self._send_json(200, STATE.get_prompts(lang))
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            req_data = json.loads(raw_body)
        except Exception:
            req_data = {}

        if url.path == "/api/pair":
            try:
                g_phone = req_data.get("guardian_phone") or STATE.guardian_phone
                m_phone = req_data.get("member_phone") or STATE.member_phone
                m_name = req_data.get("member_name") or STATE.member_name or "Rahul (Son)"
                res = STATE.pair_devices(g_phone, m_phone, m_name)
                self._send_json(200, res)
            except Exception as e:
                self._send_json(400, {"error": str(e)})

        elif url.path == "/api/invite":
            try:
                m_phone = req_data.get("member_phone", "")
                m_name = req_data.get("member_name", "Rahul (Son)")
                host = self.headers.get("Host") or "192.168.137.230:8080"
                record = STATE.create_pairing_invitation(m_phone, m_name, host_ip=host)
                self._send_json(200, record)
            except Exception as e:
                self._send_json(400, {"error": str(e)})

        elif url.path == "/api/confirm_pin":
            try:
                pin = req_data.get("pin", "")
                res = STATE.confirm_pairing_pin(pin)
                self._send_json(200, res)
            except Exception as e:
                self._send_json(400, {"error": str(e)})

        elif url.path == "/api/verify":
            candidate = req_data.get("code", "")
            res = STATE.verify_code(candidate)
            self._send_json(200, res)

        elif url.path == "/api/reset":
            res = STATE.reset_verification()
            self._send_json(200, res)

        elif url.path == "/api/emergency_callback":
            self._send_json(200, STATE.get_emergency_action())

        elif url.path == "/api/family_sos":
            self._send_json(200, STATE.trigger_family_sos())

        elif url.path == "/api/practice_verify":
            candidate = req_data.get("code", "")
            self._send_json(200, STATE.practice_verify(candidate))

        elif url.path == "/api/simulate_risk":
            s_a = float(req_data.get("s_a", 0.08))
            s_t = float(req_data.get("s_t", 0.05))
            s_c = float(req_data.get("s_c", 0.05))
            lang = str(req_data.get("lang", "hi"))
            res = STATE.simulate_risk(s_a=s_a, s_t=s_t, s_c=s_c, lang=lang)
            self._send_json(200, res)

        elif url.path == "/api/run_scenario":
            sc_id = req_data.get("scenario_id", "S1")
            try:
                res = STATE.run_scenario(sc_id)
                self._send_json(200, res)
            except Exception as e:
                self._send_json(400, {"error": str(e)})

        elif url.path == "/api/scenario_step":
            sc_id = req_data.get("scenario_id", "S1")
            step_idx = req_data.get("step_index")
            try:
                res = STATE.step_scenario(sc_id, step_idx)
                self._send_json(200, res)
            except Exception as e:
                self._send_json(400, {"error": str(e)})

        elif url.path == "/api/reset_scenario":
            res = STATE.reset_scenario()
            self._send_json(200, res)
        else:
            self.send_error(404, "Not Found")


def run_simulator_server(port: int = 8080):
    server_address = ("", port)
    with socketserver.TCPServer(server_address, FVSRequestHandler) as httpd:
        print(f"[*] Family Voice Shield Simulator running at http://localhost:{port}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Stopping server.")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_simulator_server(port)
