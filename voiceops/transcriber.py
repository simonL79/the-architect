import whisper
import tempfile

model = whisper.load_model("base")  # You can change to "medium" or "large" if needed

def transcribe_audio(audio_data):
    with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as tmp_file:
        tmp_file.write(audio_data.get_wav_data())
        tmp_file.flush()

        result = model.transcribe(tmp_file.name)
        return result["text"]
