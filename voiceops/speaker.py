import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 185)   # Speed of speech
engine.setProperty('volume', 1.0) # Max volume

def speak(text):
    print(f"🗣️ {text}")
    engine.say(text)
    engine.runAndWait()
