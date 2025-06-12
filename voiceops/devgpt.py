
import os
import openai

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def handle_command(transcript):
    try:
        # Extract target filename
        tokens = transcript.lower().split()
        filename = None
        for token in tokens:
            if token.endswith(".py"):
                filename = token
                break

        if not filename or not os.path.isfile(f"voiceops/{filename}"):
            return f"File '{filename}' not found."

        with open(f"voiceops/{filename}", "r") as f:
            original_code = f.read()

        if "refactor" in transcript:
            prompt = (
                "Refactor the following Python code for readability. "
                "Do not change its behavior:\n\n" + original_code
            )
            save_suffix = "_refactored"
        elif "summarize" in transcript:
            prompt = (
                "Summarize the following Python code in plain English:\n\n" + original_code
            )
            save_suffix = "_summary"
        else:
            return "Command understood, but could not identify task."

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Python developer."},
                {"role": "user", "content": prompt}
            ]
        )

        output = response.choices[0].message.content.strip()

        if "refactor" in transcript:
            new_path = f"voiceops/{filename.replace('.py', save_suffix + '.py')}"
            with open(new_path, "w") as f:
                f.write(output)
            return f"Refactored file saved as {os.path.basename(new_path)}."

        elif "summarize" in transcript:
            print("=== SUMMARY ===")
            print(output)
            return "Summary complete. See terminal output."

    except Exception as e:
        return f"DevGPT error: {e}"
