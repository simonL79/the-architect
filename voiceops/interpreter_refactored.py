Here's the refactored code:

```python
import json
import re

# Load mission profiles
with open("missions/mission_profile.json") as f:
    mission_profiles = json.load(f)


def match_transcript(patterns):
    return any(pattern in transcript for pattern in patterns)


def process_devgpt(transcript):
    pattern = r"(refactor|summarize).*?([\w\-_]+\.py)"
    match = re.search(pattern, transcript)
    if match:
        return {"action": "devgpt", "params": transcript}
    return None


def process_reflection(transcript):
    return {"action": "reflect_history", "params": None}


def process_replay(transcript):
    words = transcript.split()
    num = next((int(word) for word in words if word.isdigit()), 1)
    return {"action": "replay_history", "params": num}


def process_execution(transcript):
    matches = [profile for profile in mission_profiles if profile.replace("_", " ") in transcript]
    if matches:
        profile = matches[0]
        return {"action": "run_mission_profile", "params": profile}
    return None


action_matchers = {
    ("refactor", "summarize"): process_devgpt,
    ("what did i do", "history"): process_reflection,
    ("rerun last",): process_replay,
    ("execute", "launch profile", "architect"): process_execution,
    ("check system load",): {"action": "check_system_load"},
    ("restart interface",): {"action": "restart_listener"},
    ("run last script",): {"action": "run_script", "params": "scripts\\last_used_script.ps1"},
}


def interpret_command(transcript):
    transcript = transcript.lower().strip()

    # Iterate all the matchers until it finds a match
    for patterns, matcher in action_matchers.items():
        if match_transcript(patterns):
            result = matcher(transcript)
            if result:
                return result
            
    # Fallback
    return {"action": "gpt_fallback", "params": transcript}

```

This refactoring version isolates the behavior of each command into individual functions, making the code easier to read and maintain. Each command behavior is mapped in a dictionary `action_matchers` so that the main function `interpret_command` becomes simplified and clearer. This is especially helpful if you were to add more commands in the future.