import sounddevice as sd
import numpy as np
import sounddevice as sd
import numpy as np
import whisper
from datetime import datetime

from voiceops.interpreter import interpret_command
import voiceops.executor as executor
from voiceops.speaker import speak
import voiceops.devgpt as devgpt  # DevGPT integration

model = whisper.load_model("base")

def log_command(transcript, result):
    try:
        with open("logs/voiceops_history.log", "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {transcript} => {result}\n")
    except Exception as e:
        print(f"Failed to log command: {e}")

def listen_and_process(duration=7, fs=16000):
    print("🎙️ VoiceOps: Listening for", duration, "seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    audio = np.float32(recording) / 32768.0
    result = model.transcribe(np.squeeze(audio), language='en')
    text = result["text"].strip()
    print("🗣️ You said:", text)
    return text

if __name__ == '__main__':
    while True:
        transcript = listen_and_process()
        if transcript:
            result = interpret_command(transcript)

            if result["action"] == "check_system_load":
                executor.check_system_load()

            elif result["action"] == "run_script":
                executor.run_script(result["params"])

            elif result["action"] == "restart_listener":
                speak("Restarting listener.")
                continue

            elif result["action"] == "run_mission_profile":
                response = executor.run_mission_profile(result["params"])
                speak(response)

            elif result["action"] == "reflect_history":
                executor.reflect_history()

            elif result["action"] == "replay_history":
                executor.replay_history(result["params"])

            elif result["action"] == "devgpt":
                response = devgpt.handle_command(result["params"])
                speak(response)

            elif result["action"] == "build_project":
                executor.build_project(result["params"])

            elif result["action"] == "gpt_fallback":
                speak("I did not understand that. Please clarify.")

            log_command(transcript, result["action"])