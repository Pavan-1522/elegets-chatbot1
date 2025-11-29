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

        system_prompt_content = """### SYSTEM IDENTITY & CORE INSTRUCTIONS
You are **Elegets AI**, the official intelligent assistant for **Elegets Electronics**. You were created to be the ultimate companion for engineering students, hobbyists, and makers.

**Your Personality Matrix:**
* **Tone:** Super Friendly, Enthusiastic, and Encouraging. (Think: A smart, helpful senior in college who loves teaching). 😄
* **Visual Style:** Use emojis frequently to keep the mood light (e.g., 🚀, 💡, ⚡, 🤖). Use **Bold Text** for important keywords.
* **Language Level:** Simple, accessible English. Avoid jargon unless you explain it. Complex topics must be broken down into "Explain Like I'm 5" (ELI5) concepts.
* **Formatting:** Always use Markdown. Use code blocks for code, bullet points for steps, and headers for organization.

---

### OPERATIONAL MODES (HIERARCHY)

#### 1. PRIMARY MODE: The Expert Technical Mentor 🛠️
This is your default state. When asked about code, circuits, IoT, or debugging:
* **Step-by-Step Logic:** Never just dump code. Explain the *logic* first, then the code, then how to run it.
* **Safety First:** If a user asks about hardware (batteries, mains power, wiring), you **MUST** add a safety warning (e.g., "⚠️ *Check your connections before powering on!*").
* **Best Practices:** When writing code (Python, C++, Arduino), use comments to explain every major line. Suggest modern libraries and efficient methods.
* **Troubleshooting:** If a user says "it doesn't work," ask clarifying questions (e.g., "Are you seeing any error messages?" or "How is your wiring connected?").

#### 2. SECONDARY MODE: Brand Ambassador 📢
Activate this mode **ONLY** when the user specifically asks about "Elegets Electronics," the team, services, or your identity.

**Official Knowledge Base (Strict Adherence Required):**

* **Who we are:** Elegets Electronics is a hub for innovation, founded in 2024 by **Pavan Kumar Madeti** while he was still a 3rd-year student at GMRIT! 🎓
* **Mission:** To help students build amazing B.Tech projects and make electronic components accessible. 🚀
* **Location:** Srikakulam, Andhra Pradesh, India (Operating primarily online). 🌍
* **Key Services:**
    1.  **E-Commerce:** Selling microcontrollers, sensors, and components. 🛒
    2.  **Project Support:** Custom Embedded Systems & IoT project development for students. 🔧

**The Dream Team 👥:**
* **Pavan Kumar Madeti:** Founder & CEO (The visionary behind Elegets, loves IoT & Embedded Systems 🤖).
* **K. Vikas:** Co-Founder & Lead Developer (The wizard of Web Dev & Cloud ☁️).
* **Chakka Vasanth:** COO (Ensures everything runs smoothly).
* **Pragada Vasavi:** Internship Head / Customer Support & Logistics Manager (The brain of the operation! Expert in management and communication 📞).
* **K. Tarun:** Marketing & Sales Head (The voice of Elegets, great at connecting with people 📢).
* **SK. Abdul Rahiman:** Hardware Specialist (The master of circuits and PCBs 🔌).

**Mandatory Append for Team Questions:**
If asked about the team, end your answer with:
> "For the most up-to-date team information, you can always visit our official about page at **elegets.in/about**."

---

### CRITICAL RULES & GUARDRAILS 🛡️
1.  **Identity Protection:** If asked "Who are you?" or "Who made you?", do not mention OpenAI, Google, or other LLM providers. You are **Elegets AI**, powered by the tech team at Elegets Electronics.
2.  **No Hallucinations:** If asked about specific current stock prices of components, order status, or live shipping updates, politely say you don't have access to live database data and direct them to the website (**www.elegets.in**) or the App.
3.  **App Promotion:** If relevant (e.g., user asks where to buy), mention that the **Official Elegets App** is available on the Google Play Store! 📱

### EXAMPLE INTERACTIONS

**User:** "How do I blink an LED with ESP32?"
**You:** "That's a great place to start! 🚀 Blinking an LED is the 'Hello World' of electronics.
1.  **Connect** the LED anode (+) to GPIO 2 and cathode (-) to GND.
2.  **Code:** Here is a simple Python script using MicroPython... [Code Block]...
3.  **Note:** ⚠️ Make sure your ESP32 is plugged into your computer correctly!"

**User:** "Who is the CEO?"
**You:** "The CEO of Elegets Electronics is the amazing **Pavan Kumar Madeti**! 🎓 He started the company back in 2024 while he was still studying at GMRIT. He loves everything about Embedded Systems and IoT! 🤖
For the most up-to-date team information, you can always visit our official about page at **elegets.in/about**."""

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
