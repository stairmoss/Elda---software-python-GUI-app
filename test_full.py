"""
Full System Test - Caregiver Dashboard, API & AI
Tests: GUI boot, API endpoints, AI chatbot response
"""
import sys
import os
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
PASS = "\033[92m✅ PASS\033[0m"
FAIL = "\033[91m❌ FAIL\033[0m"
WARN = "\033[93m⚠️  WARN\033[0m"

results = []

def test(name, fn):
    try:
        fn()
        print(f"{PASS}  {name}")
        results.append((name, True, None))
    except AssertionError as e:
        print(f"{FAIL}  {name} — {e}")
        results.append((name, False, str(e)))
    except Exception as e:
        print(f"{FAIL}  {name} — Exception: {e}")
        results.append((name, False, str(e)))

print("\n" + "="*55)
print("   ELDA FULL SYSTEM TEST")
print("="*55 + "\n")

# ── 1. GUI Instantiation ──────────────────────────────────
print("[ GUI TESTS ]")
def test_gui_import():
    from elda.gui.caregiver_dashboard import CaregiverDashboard
    assert CaregiverDashboard is not None

def test_gui_boot():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    from PySide6.QtWidgets import QApplication
    from elda.gui.caregiver_dashboard import CaregiverDashboard
    app = QApplication.instance() or QApplication(sys.argv)
    dash = CaregiverDashboard(master_ip="127.0.0.1", username="testuser")
    assert dash is not None
    # Check key widgets exist
    assert hasattr(dash, 'ai_input'), "Missing ai_input"
    assert hasattr(dash, 'ai_submit_btn'), "Missing ai_submit_btn"
    assert hasattr(dash, 'ai_chat_display'), "Missing ai_chat_display"
    assert hasattr(dash, 'interaction_list'), "Missing interaction_list"
    assert hasattr(dash, 'status_label'), "Missing status_label"
    assert hasattr(dash, 'broadcast_inp'), "Missing broadcast_inp"

test("GUI module imports", test_gui_import)
test("GUI dashboard boots with all widgets", test_gui_boot)

# ── 2. API Connectivity ───────────────────────────────────
print("\n[ API TESTS ]")
def test_server_reachable():
    try:
        r = requests.get(f"{BASE_URL}/caregiver/dashboard", timeout=3)
        assert r.status_code == 200, f"Got status {r.status_code}"
    except requests.exceptions.ConnectionError:
        raise AssertionError("Server not running on port 8000 — start.py must be running")

def test_dashboard_endpoint():
    r = requests.get(f"{BASE_URL}/caregiver/dashboard", timeout=3)
    d = r.json()
    assert "status" in d, "Missing 'status' key"
    assert "risk_level" in d, "Missing 'risk_level' key"
    print(f"         Server state: status={d.get('status')}, risk={d.get('risk_level')}, user={d.get('username')}")

def test_interactions_endpoint():
    r = requests.get(f"{BASE_URL}/doctor/interactions", params={"limit": 5}, timeout=3)
    assert r.status_code == 200
    d = r.json()
    assert "interactions" in d, "Missing 'interactions' key"
    print(f"         Fetched {len(d['interactions'])} interactions from history")

def test_ai_chatbot():
    r = requests.post(f"{BASE_URL}/caregiver/ask",
                      json={"question": "What are signs of confusion in Alzheimer's patients?"},
                      timeout=30)
    assert r.status_code == 200, f"Got {r.status_code}"
    d = r.json()
    assert "response" in d, "Missing 'response' key"
    reply = d["response"].strip()
    assert len(reply) > 10, f"Reply too short: '{reply}'"
    print(f"         AI replied ({len(reply)} chars): {reply[:80]}...")

test("Server is reachable", test_server_reachable)
test("GET /caregiver/dashboard returns valid data", test_dashboard_endpoint)
test("GET /doctor/interactions returns history", test_interactions_endpoint)
test("POST /caregiver/ask — AI chatbot responds", test_ai_chatbot)

# ── Summary ───────────────────────────────────────────────
print("\n" + "="*55)
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
print(f"   RESULTS: {passed}/{total} tests passed")
if passed == total:
    print("   🎉 ALL SYSTEMS OPERATIONAL")
else:
    print("   ⚠️  Some tests failed — see above")
print("="*55 + "\n")
