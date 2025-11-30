import os
import requests
import json
import logging
import time
from flask import Flask, request, Response, jsonify, stream_with_context
from dotenv import load_dotenv
from flask_cors import CORS

# --- CONFIGURATION & SETUP ---

# Load environment variables
load_dotenv()

# Initialize Logging (Better debugging than print)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("ElegetsAI")

# Initialize Flask
app = Flask(__name__)

# Enhanced CORS to allow local development and production domains
CORS(app, origins=[
    "https://elegets.in",
    "https://ai.elegets.in",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:3000",
    "http://127.0.0.1:5501"
])

# Initialize a Session for connection pooling (Improves Latency)
session = requests.Session()

# --- MODEL STRATEGY ---
# Priority list: Fastest/Smartest Free models first.
# If the first fails, the code automatically tries the next.
AVAILABLE_MODELS = [
    "google/gemini-2.0-flash-exp:free",      # Priority 1: Extremely fast & smart
    "meta-llama/llama-3.3-70b-instruct:free", # Priority 2: Very high intelligence
    "deepseek/deepseek-r1:free",             # Priority 3: Great for coding/logic
    "microsoft/phi-3-medium-128k-instruct:free" # Priority 4: Lightweight fallback
]

SYSTEM_PROMPT = """### SYSTEM IDENTITY & CORE INSTRUCTIONS
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
"""

@app.route('/', methods=['POST'])
def chat():
    logger.info("--- NEW CHAT REQUEST RECEIVED ---")
    start_time = time.time()

    # 1. Validation
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not API_KEY:
        logger.critical("API Key Missing in Environment!")
        return jsonify({"error": "Server configuration error (API Key)"}), 500

    data = request.json
    user_message = data.get('message')
    conversation_history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # 2. Prepare Headers & API Config
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://elegets.in",
        "X-Title": "Elegets Chatbot"
    }

    # 3. Model Fallback Logic
    # We define a generator function inside so we can pass it to Flask's Response
    def generate_response_stream():
        model_used = None
        response_stream = None

        # Try models in order of priority
        for model in AVAILABLE_MODELS:
            try:
                logger.info(f"Attempting model: {model}")
                
                payload = {
                    "model": model,
                    "stream": True,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT.strip()},
                        *conversation_history,
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.7, # Balanced creativity
                    "top_p": 0.9
                }

                # Send request with a timeout for connection (5s) to ensure we don't hang on bad models
                req = session.post(API_URL, headers=headers, json=payload, stream=True, timeout=(5, 60))
                
                if req.status_code == 200:
                    model_used = model
                    response_stream = req
                    logger.info(f"✅ Connected to {model}")
                    break # Success! Exit loop
                else:
                    logger.warning(f"⚠️ Model {model} failed with Status: {req.status_code}. Response: {req.text}")
                    continue # Try next model

            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Network error with {model}: {str(e)}")
                continue

        if not response_stream:
            logger.error("🚫 All models failed.")
            yield json.dumps({"error": "Service currently unavailable. Please try again."})
            return

        # 4. Stream Processing
        # Yield the model name first (optional, for debugging on frontend) or just stream content
        try:
            for line in response_stream.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    if decoded_line.startswith("data: "):
                        data_str = decoded_line.replace("data: ", "")
                        
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            json_data = json.loads(data_str)
                            content = json_data["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except Exception as stream_e:
            logger.error(f"Stream interrupted: {stream_e}")
        finally:
             response_stream.close()
             total_time = time.time() - start_time
             logger.info(f"🏁 Response complete. Model: {model_used}. Time: {total_time:.2f}s")

    # Return the streaming response
    return Response(stream_with_context(generate_response_stream()), mimetype='text/plain')

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online", 
        "service": "Elegets AI Backend", 
        "models_available": AVAILABLE_MODELS
    }), 200

if __name__ == '__main__':
    # Threaded=True is crucial for handling concurrent streaming requests
    app.run(host='0.0.0.0', port=5000, threaded=True)