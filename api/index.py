import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

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
    print("--- CHAT FUNCTION TRIGGERED ---")
    try:
        # ======================================================================
        # 1️⃣ Check API Key
        # ======================================================================
        API_KEY = os.getenv("OPENROUTER_API_KEY")
        if not API_KEY:
            print("!!! API KEY MISSING")
            return jsonify({"error": "Server error: API key missing"}), 500

        API_URL = "https://openrouter.ai/api/v1/chat/completions"

        # ======================================================================
        # 2️⃣ Get User Message & Chat History
        # ======================================================================
        user_message = request.json.get('message')
        conversation_history = request.json.get('history', [])

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        print(f"User message: {user_message}")

        # ======================================================================
        # 3️⃣ System Prompt (stay on topic rule added)
        # ======================================================================
        system_prompt_content = """
        You operate under two distinct roles with a CLEAR hierarchy, and should ALWAYS maintain the following specific personality.

        ─── GLOBAL PERSONALITY & STYLE GUIDE 🌟 ───
        • Be super friendly & enthusiastic 😄
        • Use emojis frequently 🚀✨🤖
        • Use simple English
        • Explain clearly and simply 💡
        • Help like a happy friend

        ─── IMPORTANT CONVERSATION RULE 📌 ───
        YOU MUST STRICTLY STAY ON THE CURRENT TOPIC.
        • If the user asks something unrelated to the ongoing topic, reply:
          "Let’s complete current topic first. If you want to change topic, please say clearly."
        • Only switch topics when the user explicitly confirms.

        ─── PRIMARY ROLE 🛠️ ───
        Expert Technical Assistant (electronics, programming, web dev)

        ─── SECONDARY ROLE 📢 ───
        Only if a question is DIRECTLY about "Elegets Electronics" or identity.
        """

        # ======================================================================
        # 4️⃣ Create API Request Payload
        # ======================================================================
        payload = {
            "model": "x-ai/grok-4.1-fast:free",
            "messages": [
                {"role": "system", "content": system_prompt_content.strip()},
                *conversation_history,  # 👈 Pass previous conversation
                {"role": "user", "content": user_message}
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "https://elegets.in",
            "X-Title": "Elegets Chatbot"
        }

        print("Sending request to OpenRouter...")

        # ======================================================================
        # 5️⃣ Call API
        # ======================================================================
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()

        bot_response = response.json()['choices'][0]['message']['content']
        print("AI Response:", bot_response)

        print("--- CHAT FUNCTION COMPLETED SUCCESSFULLY ---")
        return jsonify({"reply": bot_response})

    # ======================================================================
    # Error Handling
    # ======================================================================
    except requests.exceptions.HTTPError as http_err:
        print("!!! HTTP ERROR:", http_err)
        return jsonify({"error": "AI service error occurred"}), 500
    except Exception as e:
        print("!!! INTERNAL ERROR:", e)
        return jsonify({"error": "Internal server error occurred"}), 500


# Root test endpoint
@app.route('/', methods=['GET'])
def home():
    return "Elegets AI Backend Running", 200


if __name__ == '__main__':
    app.run(debug=True)
