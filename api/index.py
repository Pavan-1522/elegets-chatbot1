import os
import requests
from flask import Flask, request, Response, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import json

# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)
CORS(app, origins=[
    "https://elegets.in",
    "http://127.0.0.1:5500",
    "http://localhost:5500"
])

@app.route('/', methods=['POST'])
def chat():
    print("--- CHAT FUNCTION TRIGGERED (STREAM MODE) ---")
    try:
        API_KEY = os.getenv("OPENROUTER_API_KEY")
        if not API_KEY:
            return jsonify({"error": "API key missing"}), 500

        API_URL = "https://openrouter.ai/api/v1/chat/completions"

        user_message = request.json.get('message')
        conversation_history = request.json.get('history', [])

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        system_prompt_content = """
        You operate under two roles with a clear hierarchy.

        🎯 GLOBAL PERSONALITY
        • Friendly, enthusiastic 😄
        • Use emojis 🚀✨🤖
        • Simple English
        • Explain clearly 💡

        📌 IMPORTANT
        Stay on the current topic. If unrelated:
        "Let’s complete current topic first. If you want to change topic, please say clearly."

        🛠 PRIMARY: Technical Assistant
        📢 SECONDARY: Elegets info (only if asked directly)
        """

        # Enable streaming!
        payload = {
            "model": "x-ai/grok-4.1-fast:free",
            "stream": True,
            "messages": [
                {"role": "system", "content": system_prompt_content.strip()},
                *conversation_history,
                {"role": "user", "content": user_message}
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "https://elegets.in",
            "X-Title": "Elegets Chatbot"
        }

        def generate():
            with requests.post(API_URL, headers=headers, json=payload, stream=True) as r:
                for line in r.iter_lines():
                    if line:
                        decoded = line.decode("utf-8").replace("data: ", "")
                        if decoded.strip() == "[DONE]":
                            break
                        try:
                            content = json.loads(decoded)["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except:
                            pass

        return Response(generate(), mimetype='text/plain')

    except Exception as e:
        print("🚨 ERROR:", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/', methods=['GET'])
def home():
    return "Elegets AI Streaming Backend Running 🚀", 200


if __name__ == '__main__':
    app.run(threaded=True)  # Remove debug=True in production!
