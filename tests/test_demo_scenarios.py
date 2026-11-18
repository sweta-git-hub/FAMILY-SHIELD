"""
tests/test_demo_scenarios.py — Comprehensive automated test suite for Phase 8 demo path

Verifies:
1. Scenario catalog schema, completeness, and metadata integrity (S1-S5).
2. End-to-end replay harness execution with G.711 telephony degradation.
3. Time-to-AMBER detection speed SLA (<= 8s for scam scenarios).
4. Replay attack rejection at the cryptographic gateway (Scenario 4).
5. Covert duress keyword emergency notification dispatch (Scenario 5).
6. Benign call stability (zero false alarms throughout conversation).
7. Web simulator backend scenario runner, stepping engine, and event logger.
8. CLI entry point options (--list, --scenario, --all, --json).

Rule 7 Compliance: No raw audio bytes or plain transcripts are ever persisted to disk.

Copyright © 2024 Family Voice Shield Project
"""

import io
import json
import unittest
from contextlib import redirect_stdout

from demo.scenarios import (
    SCENARIO_CATALOG,
    SCENARIO_BY_ID,
    get_scenario,
    list_scenarios,
    FAKE_ACCIDENT,
    DIGITAL_ARREST,
    BENIGN_FAMILY_CALL,
    RELAY_ATTACK,
    DURESS_CALL,
)
from demo.telephony_replay import TelephonyReplayHarness, main as replay_main
from demo.web_simulator import SimulatorState


class TestScenarioCatalog(unittest.TestCase):
    """Validates structure, metadata, and consistency of the scripted scenario catalog."""

    def test_catalog_contains_five_scenarios(self):
        self.assertEqual(len(SCENARIO_CATALOG), 5)
        expected_ids = {"S1", "S2", "S3", "S4", "S5"}
        actual_ids = {s.scenario_id for s in SCENARIO_CATALOG}
        self.assertEqual(expected_ids, actual_ids)

    def test_get_scenario_by_id_and_name(self):
        self.assertIsNotNone(get_scenario("S1"))
        self.assertIsNotNone(get_scenario("s1"))
        self.assertIsNotNone(get_scenario("Fake Accident"))
        self.assertIsNotNone(get_scenario("cbi"))
        self.assertIsNotNone(get_scenario("Benign"))
        self.assertIsNotNone(get_scenario("Relay"))
        self.assertIsNotNone(get_scenario("Duress"))
        self.assertIsNone(get_scenario("NonExistentXYZ"))

    def test_list_scenarios_json_serializable(self):
        summary = list_scenarios()
        self.assertEqual(len(summary), 5)
        # Verify valid JSON serialization
        dumped = json.dumps(summary)
        loaded = json.loads(dumped)
        self.assertEqual(len(loaded), 5)
        for entry in loaded:
            self.assertIn("id", entry)
            self.assertIn("name", entry)
            self.assertIn("category", entry)
            self.assertIn("expected_final_tier", entry)
            self.assertIn("num_chunks", entry)

    def test_scenario_chunk_integrity(self):
        for sc in SCENARIO_CATALOG:
            self.assertGreater(len(sc.chunks), 0, f"{sc.scenario_id} has no chunks")
            for i, chunk in enumerate(sc.chunks):
                self.assertEqual(chunk.chunk_index, i)
                self.assertIsInstance(chunk.transcript, str)
                self.assertGreater(len(chunk.transcript), 0)
                self.assertGreaterEqual(chunk.s_a_mock, 0.0)
                self.assertLessEqual(chunk.s_a_mock, 1.0)
                self.assertIn(chunk.expected_tier, {"GREEN", "AMBER", "RED", "REJECTED"})


class TestTelephonyReplayHarness(unittest.TestCase):
    """Evaluates the telephony streaming replay pipeline on all scenarios."""

    def setUp(self):
        self.harness = TelephonyReplayHarness(simulate_telephony=True)

    def test_s1_fake_accident_progression_and_sla(self):
        report = self.harness.run(FAKE_ACCIDENT)
        self.assertEqual(report.scenario_id, "S1")
        self.assertEqual(report.expected_final_tier, "RED")
        self.assertEqual(report.actual_final_tier, "RED")
        self.assertTrue(report.all_tiers_matched)

        # SLA verification: Time-to-AMBER must be <= 4.0s (well below 8.0s limit)
        self.assertIsNotNone(report.time_to_amber_seconds)
        self.assertLessEqual(report.time_to_amber_seconds, 4.0)
        self.assertTrue(report.amber_sla_met)

        # Time-to-RED verification
        self.assertIsNotNone(report.time_to_red_seconds)
        self.assertLessEqual(report.time_to_red_seconds, 6.0)

        # Latency check: p50 should be well under 50ms in-memory
        self.assertLess(report.latency_p50_ms, 50.0)

    def test_s2_digital_arrest_progression_and_sla(self):
        report = self.harness.run(DIGITAL_ARREST)
        self.assertEqual(report.scenario_id, "S2")
        self.assertEqual(report.expected_final_tier, "RED")
        self.assertEqual(report.actual_final_tier, "RED")
        self.assertTrue(report.all_tiers_matched)

        # Immediate escalation check: AMBER at 0.0s, RED by 2.0s
        self.assertEqual(report.time_to_amber_seconds, 0.0)
        self.assertEqual(report.time_to_red_seconds, 2.0)
        self.assertTrue(report.amber_sla_met)

    def test_s3_benign_family_call_stability(self):
        report = self.harness.run(BENIGN_FAMILY_CALL)
        self.assertEqual(report.scenario_id, "S3")
        self.assertEqual(report.actual_final_tier, "GREEN")
        self.assertTrue(report.all_tiers_matched)

        # Zero false alarms: must NEVER reach AMBER or RED
        self.assertIsNone(report.time_to_amber_seconds)
        self.assertIsNone(report.time_to_red_seconds)
        for m in report.chunk_metrics:
            self.assertEqual(m.actual_tier, "GREEN")
            self.assertLess(m.risk_score, 0.35)

    def test_s4_relay_attack_defense(self):
        report = self.harness.run(RELAY_ATTACK)
        self.assertEqual(report.scenario_id, "S4")
        self.assertEqual(report.actual_final_tier, "REJECTED")
        self.assertTrue(report.relay_rejected)
        self.assertTrue(report.all_tiers_matched)
        self.assertEqual(report.chunk_metrics[0].actual_tier, "REJECTED")

    def test_s5_covert_duress_call(self):
        report = self.harness.run(DURESS_CALL)
        self.assertEqual(report.scenario_id, "S5")
        # Visual/display tier stays GREEN to protect victim from nearby aggressor
        self.assertEqual(report.actual_final_tier, "GREEN")
        self.assertTrue(report.all_tiers_matched)
        # Background emergency notification must be dispatched
        self.assertTrue(report.emergency_dispatched)

    def test_run_without_telephony_codec(self):
        raw_harness = TelephonyReplayHarness(simulate_telephony=False)
        rep = raw_harness.run(FAKE_ACCIDENT)
        self.assertEqual(rep.actual_final_tier, "RED")
        self.assertFalse(rep.codec_applied)


class TestWebSimulatorScenarioWalkthrough(unittest.TestCase):
    """Tests the interactive scenario selector and step replay engine in web_simulator."""

    def setUp(self):
        self.state = SimulatorState(step_seconds=60)

    def test_get_scenarios_returns_five(self):
        scenarios = self.state.get_scenarios()
        self.assertEqual(len(scenarios), 5)
        ids = [s["id"] for s in scenarios]
        self.assertIn("S1", ids)
        self.assertIn("S5", ids)

    def test_run_scenario_s1(self):
        res = self.state.run_scenario("S1")
        self.assertIn("report", res)
        self.assertIn("risk_state", res)
        self.assertIn("event_log", res)

        rep = res["report"]
        self.assertEqual(rep["actual_final_tier"], "RED")
        self.assertTrue(rep["amber_sla_met"])
        self.assertEqual(res["risk_state"]["tier"], "RED")
        self.assertEqual(len(res["event_log"]), 6)

    def test_step_scenario_progression(self):
        # Step 0
        s0 = self.state.step_scenario("S1", step_index=0)
        self.assertFalse(s0["completed"])
        self.assertEqual(s0["chunk"]["tier"], "GREEN")

        # Step 1
        s1 = self.state.step_scenario("S1", step_index=1)
        self.assertFalse(s1["completed"])
        self.assertEqual(s1["chunk"]["tier"], "GREEN")

        # Step 2 — Escalation to AMBER
        s2 = self.state.step_scenario("S1", step_index=2)
        self.assertFalse(s2["completed"])
        self.assertEqual(s2["chunk"]["tier"], "AMBER")

        # Step 3 — Escalation to RED
        s3 = self.state.step_scenario("S1", step_index=3)
        self.assertFalse(s3["completed"])
        self.assertEqual(s3["chunk"]["tier"], "RED")

    def test_step_scenario_duress_alert(self):
        # Step through S5
        s0 = self.state.step_scenario("S5", step_index=0)
        self.assertEqual(s0["chunk"]["tier"], "GREEN")

        s1 = self.state.step_scenario("S5", step_index=1)
        # Contains keyword "Raju"
        self.assertEqual(s1["chunk"]["tier"], "GREEN")
        self.assertTrue(s1["chunk"]["duress_dispatched"])
        self.assertTrue(s1["risk_state"]["emergency_dispatched"])

    def test_step_scenario_relay_rejected(self):
        s0 = self.state.step_scenario("S4", step_index=0)
        self.assertEqual(s0["chunk"]["tier"], "REJECTED")
        self.assertEqual(s0["risk_state"]["tier"], "REJECTED")
        self.assertTrue(s0["risk_state"]["relay_rejected"])

    def test_reset_scenario(self):
        self.state.run_scenario("S1")
        self.assertEqual(self.state.current_risk_result["tier"], "RED")

        res = self.state.reset_scenario()
        self.assertEqual(res["status"], "RESET")
        self.assertEqual(res["risk_state"]["tier"], "GREEN")
        self.assertEqual(self.state.active_scenario_step, 0)
        self.assertEqual(len(self.state.scenario_event_log), 0)


class TestTelephonyReplayCLI(unittest.TestCase):
    """Tests the CLI entry point of telephony_replay."""

    def test_cli_list(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = replay_main(["--list"])
        self.assertEqual(ret, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(len(data), 5)

    def test_cli_single_scenario_json(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = replay_main(["--scenario", "S1", "--json"])
        self.assertEqual(ret, 0)
        data = json.loads(buf.getvalue())
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["scenario_id"], "S1")
        self.assertEqual(data[0]["actual_final_tier"], "RED")

    def test_cli_all_scenarios(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = replay_main(["--all"])
        self.assertEqual(ret, 0)
        out = buf.getvalue()
        self.assertIn("Scenario S1", out)
        self.assertIn("Scenario S2", out)
        self.assertIn("Scenario S3", out)
        self.assertIn("Scenario S4", out)
        self.assertIn("Scenario S5", out)
        self.assertIn("✅ SLA MET", out)


class TestSystemEvaluationRunner(unittest.TestCase):
    """Validates the 30-case empirical evaluation runner."""

    def test_evaluate_system_metrics(self) -> None:
        from demo.evaluate_system import evaluate_system
        res = evaluate_system()
        self.assertIn("summary", res)
        s = res["summary"]
        self.assertEqual(s["total_cases"], 30)
        self.assertGreaterEqual(s["precision"], 0.90)
        self.assertGreaterEqual(s["recall"], 0.90)
        self.assertLessEqual(s["false_positive_rate"], 0.05)
        self.assertGreater(s["latency_p50_ms"], 0.0)


if __name__ == "__main__":
    unittest.main()
