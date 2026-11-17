"""
Family Voice Shield (FVS) - Interactive Dual-Device Web Simulator
Demonstrates Phase 2 contact-based pairing and live 60-second synchronized 6-digit TOTP codes.
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

# Ensure repository root is on Python sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.crypto import VerificationResult
from core.pairing import (
    DEFAULT_CODE_STEP,
    DeviceRole,
    PairedRelationship,
    PairingSession,
)
from core.phone_util import format_phone_display, normalize_phone_number
from core.storage import SecureVault


class SimulatorState:
    """In-memory state holding the two simulated mobile phones."""

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

        # Auto-pair a default family link for instant demo convenience
        self.pair_devices(
            guardian_phone=self.guardian_phone,
            member_phone=self.member_phone,
            member_name=self.member_name,
        )

    def pair_devices(self, guardian_phone: str, member_phone: str, member_name: str) -> dict:
        norm_guardian = normalize_phone_number(guardian_phone)
        norm_member = normalize_phone_number(member_phone)

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

    def get_status(self) -> dict:
        now = int(time.time())
        rem = self.step_seconds - (now % self.step_seconds)

        if not self.guardian_rel or not self.member_rel:
            return {"paired": False, "now": now, "remaining": rem}

        # Code Rahul reads to Mom
        rahul_outbound_code, _ = self.member_rel.get_outbound_code(timestamp=now)
        # Code Mom expects Rahul to say
        mom_expected_code, _ = self.guardian_rel.get_expected_inbound_code(timestamp=now)

        # Directional isolation check: Code Mom would say if SHE called Rahul
        mom_outbound_code, _ = self.guardian_rel.get_outbound_code(timestamp=now)
        rahul_expected_code, _ = self.member_rel.get_expected_inbound_code(timestamp=now)

        return {
            "paired": True,
            "now": now,
            "step_seconds": self.step_seconds,
            "remaining": rem,
            "guardian": {
                "phone": format_phone_display(self.guardian_phone),
                "expected_from_member": mom_expected_code,
                "outbound_to_member": mom_outbound_code,
                "peer_name": self.member_name,
                "peer_phone": format_phone_display(self.member_phone),
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
        }

    def verify_code(self, candidate_code: str) -> dict:
        if not self.guardian_rel or not self.lockout_session:
            return {"result": "NOT_PAIRED"}

        now = int(time.time())
        result = self.guardian_rel.verify_incoming_code(
            candidate_code=candidate_code,
            timestamp=now,
            session=self.lockout_session,
        )

        return {
            "result": result.value,
            "failed_attempts": self.lockout_session.failed_attempts,
            "is_locked": self.lockout_session.is_locked,
            "is_verified": self.lockout_session.is_verified,
        }

    def reset_verification(self) -> dict:
        if self.lockout_session:
            self.lockout_session.reset()
        return {"status": "RESET_OK"}


# Global simulator instance
STATE = SimulatorState(step_seconds=60)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Family Voice Shield - Dual Phone Live Simulator</title>
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
    padding: 24px;
  }
  header {
    text-align: center;
    max-width: 860px;
    margin-bottom: 24px;
  }
  h1 {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
  }
  p.subtitle {
    color: var(--text-muted);
    font-size: 14px;
    line-height: 1.5;
  }
  .badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
    background: rgba(59, 130, 246, 0.15);
    color: #93c5fd;
    border: 1px solid rgba(59, 130, 246, 0.3);
    margin-top: 6px;
  }

  /* Setup / Pairing Bar */
  .control-bar {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 14px 20px;
    width: 100%;
    max-width: 900px;
    margin-bottom: 24px;
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
  .input-group input {
    background: #0f172a;
    border: 1px solid var(--card-border);
    border-radius: 8px;
    color: #fff;
    padding: 8px 12px;
    font-size: 14px;
    outline: none;
  }
  .input-group input:focus {
    border-color: var(--accent);
  }
  button.btn {
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
  }
  button.btn:hover {
    background: #2563eb;
    box-shadow: 0 0 12px var(--accent-glow);
  }
  button.btn-outline {
    background: transparent;
    border: 1px solid var(--card-border);
    color: var(--text-muted);
  }
  button.btn-outline:hover {
    background: rgba(255, 255, 255, 0.05);
    color: #fff;
  }

  /* Dual Phones Stage */
  .phones-container {
    display: flex;
    flex-direction: row;
    gap: 32px;
    justify-content: center;
    align-items: flex-start;
    width: 100%;
    max-width: 960px;
    flex-wrap: wrap;
  }
  .phone-mockup {
    width: 360px;
    min-height: 600px;
    background: #000;
    border-radius: 40px;
    padding: 14px;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 0 8px #1e293b;
    position: relative;
    display: flex;
    flex-direction: column;
  }
  .phone-screen {
    background: #090d16;
    border-radius: 28px;
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 20px 16px;
    overflow: hidden;
    position: relative;
  }
  .phone-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  }
  .role-pill {
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .role-guardian { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
  .role-member { background: rgba(16, 185, 129, 0.2); color: #34d399; }

  .phone-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 14px;
    text-align: center;
  }
  .phone-card.active-call {
    border-color: #3b82f6;
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.15);
  }

  .caller-title {
    font-size: 12px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }
  .caller-name {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 2px;
  }
  .caller-phone {
    font-size: 12px;
    color: #60a5fa;
    margin-bottom: 12px;
  }

  /* Synchronized 6-Digit Code Display */
  .code-display {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 38px;
    font-weight: 800;
    letter-spacing: 4px;
    color: #fff;
    margin: 12px 0;
    text-shadow: 0 0 20px var(--accent-glow);
  }
  .code-display.sync-green {
    color: #34d399;
    text-shadow: 0 0 25px var(--green-glow);
  }

  /* Countdown Ring */
  .timer-box {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-top: 8px;
    color: var(--text-muted);
    font-size: 13px;
    font-weight: 600;
  }
  .countdown-badge {
    background: #0f172a;
    border: 1px solid #334155;
    padding: 2px 8px;
    border-radius: 6px;
    color: #38bdf8;
    font-variant-numeric: tabular-nums;
  }

  /* Verification Input */
  .verify-form {
    margin-top: 14px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .verify-input {
    background: #0f172a;
    border: 2px solid #334155;
    border-radius: 10px;
    padding: 10px;
    font-size: 20px;
    font-weight: 700;
    text-align: center;
    color: #fff;
    letter-spacing: 3px;
    outline: none;
    font-family: monospace;
  }
  .verify-input:focus { border-color: var(--accent); }
  .btn-verify {
    background: #10b981;
    color: #fff;
    padding: 10px;
    border-radius: 8px;
    font-weight: 700;
    border: none;
    cursor: pointer;
    font-size: 14px;
    transition: 0.2s;
  }
  .btn-verify:hover { background: #059669; }

  /* Verification Result Banner */
  .result-banner {
    border-radius: 10px;
    padding: 12px;
    font-size: 13px;
    font-weight: 700;
    margin-top: 10px;
    text-align: center;
    display: none;
  }
  .result-banner.success {
    display: block;
    background: rgba(16, 185, 129, 0.2);
    border: 1px solid #10b981;
    color: #6ee7b7;
  }
  .result-banner.invalid {
    display: block;
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid #ef4444;
    color: #fca5a5;
  }
  .result-banner.locked {
    display: block;
    background: rgba(220, 38, 38, 0.35);
    border: 2px solid #dc2626;
    color: #fecaca;
  }

  /* Quick action helper buttons */
  .action-row {
    display: flex;
    gap: 6px;
    margin-top: 8px;
  }
  .btn-tiny {
    flex: 1;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--text-muted);
    font-size: 11px;
    padding: 6px 4px;
    border-radius: 6px;
    cursor: pointer;
  }
  .btn-tiny:hover { background: rgba(255, 255, 255, 0.12); color: #fff; }

  footer {
    margin-top: 32px;
    color: var(--text-muted);
    font-size: 12px;
    text-align: center;
  }
</style>
</head>
<body>

<header>
  <h1>Family Voice Shield</h1>
  <p class="subtitle">Phase 2: Contact-Based Phone Pairing & Synchronized 60-Second Directional TOTP</p>
  <span class="badge">1-Minute Rotation Active</span>
</header>

<div class="control-bar">
  <div class="input-group">
    <label>Guardian (Mom):</label>
    <input type="text" id="guardianPhoneInput" value="+91 98765 00001">
  </div>
  <div class="input-group">
    <label>Add Contact (Son):</label>
    <input type="text" id="memberPhoneInput" value="+91 98765 00002">
  </div>
  <div class="input-group">
    <label>Name:</label>
    <input type="text" id="memberNameInput" value="Rahul (Son)">
  </div>
  <button class="btn" onclick="pairFamilyMember()">Pair Now</button>
  <button class="btn btn-outline" onclick="resetVerification()">Reset Strikes</button>
</div>

<div class="phones-container">
  
  <!-- LEFT: GUARDIAN PHONE (MOM) -->
  <div class="phone-mockup">
    <div class="phone-screen">
      <div class="phone-header">
        <span class="role-pill role-guardian">Guardian (Parent)</span>
        <span id="guardianClock">--:--</span>
      </div>

      <div class="phone-card active-call">
        <div class="caller-title">Incoming Call From</div>
        <div class="caller-name" id="guardianPeerName">Rahul (Son)</div>
        <div class="caller-phone" id="guardianPeerPhone">+91 98765 00002</div>

        <div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">
          Expected Code from Rahul:
        </div>
        <div class="code-display sync-green" id="guardianExpectedCode">------</div>

        <div class="timer-box">
          <span>Updates in:</span>
          <span class="countdown-badge" id="guardianRemaining">60s</span>
        </div>
      </div>

      <!-- Verification Pad for Guardian -->
      <div class="phone-card" style="text-align: left;">
        <div style="font-size: 12px; font-weight: 700; color: #e2e8f0; margin-bottom: 4px;">
          Verify Rahul's Spoken Code
        </div>
        <div style="font-size: 11px; color: #94a3b8; margin-bottom: 8px;">
          Ask Rahul to read his 6-digit code aloud. Cloned voices cannot produce this code.
        </div>

        <div class="verify-form">
          <input type="text" id="guardianCodeInput" class="verify-input" maxlength="6" placeholder="000 000">
          <button class="btn-verify" onclick="submitVerify()">Verify Caller Identity</button>
        </div>

        <div class="action-row">
          <button class="btn-tiny" onclick="autoFillCode()">Auto-Fill Rahul's Code</button>
          <button class="btn-tiny" onclick="fillFakeCode()">Test Fake/Wrong Code</button>
        </div>

        <div id="verifyResult" class="result-banner"></div>
        <div id="strikeCount" style="font-size: 11px; color: #94a3b8; margin-top: 6px; text-align: center;">
          Failed Attempts: 0 / 3
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

      <div class="phone-card active-call">
        <div class="caller-title">Calling Guardian</div>
        <div class="caller-name">Mom (Home)</div>
        <div class="caller-phone" id="memberPeerPhone">+91 98765 00001</div>

        <div style="font-size: 11px; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 700;">
          Your 1-Minute Safety Code
        </div>
        <div class="code-display" id="memberOutboundCode">------</div>
        <div style="font-size: 11px; color: #94a3b8; margin-top: -6px; margin-bottom: 8px;">
          Read this number out loud to Mom
        </div>

        <div class="timer-box">
          <span>Expires in:</span>
          <span class="countdown-badge" id="memberRemaining">60s</span>
        </div>
      </div>

      <div class="phone-card" style="text-align: left; font-size: 12px; color: #94a3b8; line-height: 1.5;">
        <div style="font-weight: 700; color: #f8fafc; margin-bottom: 4px;">
          Security Status: Safe
        </div>
        <p>Your directional secret (HKDF-SHA256) is secured in your phone's encrypted vault.</p>
        <p style="margin-top: 6px;">Even if a scammer records your voice, they cannot generate or predict this 6-digit code.</p>
      </div>
    </div>
  </div>

</div>

<footer>
  Family Voice Shield &bull; Zero-Knowledge Cryptographic Identity Verification &bull; RFC 6238 TOTP
</footer>

<script>
let lastRahulCode = "";

async function updateStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    if (!data.paired) return;

    // Time clocks
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    document.getElementById('guardianClock').textContent = timeStr;
    document.getElementById('memberClock').textContent = timeStr;

    // Codes & sync
    const rahulCode = data.member.outbound_to_guardian;
    lastRahulCode = rahulCode;
    const momExpected = data.guardian.expected_from_member;

    document.getElementById('memberOutboundCode').textContent = rahulCode;
    document.getElementById('guardianExpectedCode').textContent = momExpected;

    // Remaining countdown
    const remStr = data.remaining + 's';
    document.getElementById('guardianRemaining').textContent = remStr;
    document.getElementById('memberRemaining').textContent = remStr;

    // Names & phones
    document.getElementById('guardianPeerName').textContent = data.guardian.peer_name;
    document.getElementById('guardianPeerPhone').textContent = data.guardian.peer_phone;
    document.getElementById('memberPeerPhone').textContent = data.member.peer_phone;

    // Lockout strikes
    const strikes = data.guardian.failed_attempts;
    const isLocked = data.guardian.is_locked;
    document.getElementById('strikeCount').textContent = `Failed Attempts: ${strikes} / 3`;

    if (isLocked) {
      const banner = document.getElementById('verifyResult');
      banner.className = 'result-banner locked';
      banner.innerHTML = '&#9888; LOCKOUT TRIGGERED: 3 Failed Attempts!<br>High probability of AI Voice Clone scam. Hang up immediately!';
    }
  } catch (err) {
    console.error("Status polling error:", err);
  }
}

async function pairFamilyMember() {
  const gPhone = document.getElementById('guardianPhoneInput').value;
  const mPhone = document.getElementById('memberPhoneInput').value;
  const mName = document.getElementById('memberNameInput').value;

  try {
    const res = await fetch('/api/pair', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ guardian_phone: gPhone, member_phone: mPhone, member_name: mName })
    });
    const result = await res.json();
    if (result.status === 'PAIRED') {
      alert("Family member successfully paired! Both devices are now synchronized.");
      updateStatus();
    } else {
      alert("Pairing failed: " + (result.error || "Unknown error"));
    }
  } catch (err) {
    alert("Pairing request error: " + err);
  }
}

async function submitVerify() {
  const code = document.getElementById('guardianCodeInput').value.trim();
  if (!code) return;

  try {
    const res = await fetch('/api/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: code })
    });
    const data = await res.json();
    const banner = document.getElementById('verifyResult');

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
  } catch (err) {
    alert("Verification error: " + err);
  }
}

async function resetVerification() {
  await fetch('/api/reset', { method: 'POST' });
  const banner = document.getElementById('verifyResult');
  banner.style.display = 'none';
  document.getElementById('guardianCodeInput').value = '';
  updateStatus();
}

function autoFillCode() {
  document.getElementById('guardianCodeInput').value = lastRahulCode;
}

function fillFakeCode() {
  document.getElementById('guardianCodeInput').value = "999888";
}

// Initial poll and recurring 1-second ticker
updateStatus();
setInterval(updateStatus, 1000);
</script>
</body>
</html>
"""


class FVSRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence default request logging to avoid terminal clutter
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
        if url.path == "/" or url.path == "/index.html":
            body = HTML_TEMPLATE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif url.path == "/api/status":
            self._send_json(200, STATE.get_status())
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
                g_phone = req_data.get("guardian_phone", "")
                m_phone = req_data.get("member_phone", "")
                m_name = req_data.get("member_name", "Rahul (Son)")
                res = STATE.pair_devices(g_phone, m_phone, m_name)
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
