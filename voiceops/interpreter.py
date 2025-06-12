import json
import re

# Load mission profiles
with open("missions/mission_profile.json") as f:
    mission_profiles = json.load(f)

def interpret_command(transcript):
    transcript = transcript.lower().strip()

    # === DevGPT Natural Command Recognition ===
    if "refactor" in transcript or "summarize" in transcript:
        match = re.search(r"(refactor|summarize).*?([\\w\\-_]+\\.py)", transcript)
        return {"action": "devgpt", "params": transcript}

    # === Natural language project build command ===
    if "build ar.i.a" in transcript or "build the system" in transcript or "deploy ar.i.a" in transcript:
        return {"action": "build_project", "params": "aria-sigma"}

    # === Reflection ===
    if "what did i do" in transcript or "history" in transcript:
        return {"action": "reflect_history", "params": None}

    # === Replay ===
    if "rerun last" in transcript:
        words = transcript.split()
        num = next((int(w) for w in words if w.isdigit()), 1)
        return {"action": "replay_history", "params": num}

    # === Mission profile execution ===
    if transcript.startswith("execute") or "launch profile" in transcript or "architect" in transcript:
        for profile in mission_profiles:
            if profile.replace("_", " ") in transcript or profile in transcript:
                return {"action": "run_mission_profile", "params": profile}

    # === Direct system commands ===
    if "check system load" in transcript:
        return {"action": "check_system_load"}

    if "restart interface" in transcript:
        return {"action": "restart_listener"}

    if "run last script" in transcript:
        return {"action": "run_script", "params": "scripts\\last_used_script.ps1"}

    # === Fallback ===
    return {"action": "gpt_fallback", "params": transcript}