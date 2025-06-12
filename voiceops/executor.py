import os
import json
import subprocess
import psutil
from datetime import datetime

from voiceops.speaker import speak
from voiceops.interpreter import interpret_command

def check_system_load():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    status = f"CPU usage is at {cpu} percent. Memory usage is at {mem} percent."
    print(status)
    speak(status)

def run_script(script_path):
    try:
        result = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", script_path], capture_output=True, text=True)
        print(f"[SCRIPT OUTPUT]: {result.stdout}")
        speak("Script executed successfully.")
    except Exception as e:
        error_msg = f"Error running script: {str(e)}"
        print(error_msg)
        speak(error_msg)

def run_mission_profile(profile_name):
    try:
        with open("missions/mission_profile.json") as f:
            profiles = json.load(f)

        if profile_name not in profiles:
            msg = f"Mission profile '{profile_name}' not found."
            print(msg)
            speak(msg)
            return msg

        steps = profiles[profile_name]["steps"]
        print(f"Executing mission profile: {profile_name}")

        for step in steps:
            action = step["action"]
            params = step.get("params")

            if action == "check_system_load":
                check_system_load()
            elif action == "run_script":
                run_script(params)
            elif action == "speak":
                speak(params)
            else:
                print(f"Unknown action in profile: {action}")

        return f"Mission '{profile_name}' completed."
    except Exception as e:
        error_msg = f"Error executing mission profile: {str(e)}"
        print(error_msg)
        speak(error_msg)
        return error_msg

def reflect_history():
    try:
        with open("logs/voiceops_history.log", "r") as f:
            lines = f.readlines()[-5:]
        summary = "\n".join([line.strip() for line in lines])
        print("=== REFLECTED COMMANDS ===")
        print(summary)
        speak("Here's what you did recently.")
        speak(summary)
    except Exception as e:
        print(f"[Reflection error] {e}")
        speak(f"Unable to read history. {e}")

def replay_history(n=1):
    try:
        with open("logs/voiceops_history.log", "r") as f:
            lines = [l.strip() for l in f.readlines() if "=>" in l]
        commands = [l.split("=>")[0].split("] ")[1] for l in lines][-n:]
        speak(f"Rerunning last {n} command{'s' if n > 1 else ''}.")
        for command in commands:
            result = interpret_command(command)
            if result["action"] == "run_mission_profile":
                run_mission_profile(result["params"])
            elif result["action"] == "check_system_load":
                check_system_load()
            elif result["action"] == "run_script":
                run_script(result["params"])
    except Exception as e:
        print(f"[Replay error] {e}")
        speak(f"Error replaying commands. {e}")

def build_project(project_name):
    try:
        if project_name != "aria-sigma":
            speak("Unknown project. Only A.R.I.A. SIGMA is configured for build.")
            return

        project_path = os.path.join(os.getcwd(), "aria-sigma")

        if not os.path.exists(project_path):
            speak("A.R.I.A. SIGMA directory not found. Build aborted.")
            return

        speak("Initializing build for A.R.I.A. SIGMA.")

        subprocess.run(["npm", "install"], cwd=project_path, shell=True)
        subprocess.run(["npm", "run", "build"], cwd=project_path, shell=True)

        speak("Build process complete.")
        return "Build successful."

    except Exception as e:
        error_msg = f"Build failed: {e}"
        print(error_msg)
        speak(error_msg)

