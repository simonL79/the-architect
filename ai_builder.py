import openai
import os

# Load the OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

def run_gpt_command(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo" if you're using that tier
            messages=[
                {"role": "system", "content": "You are The Architect — a tactical AI command interface."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"[Error]: {str(e)}"

