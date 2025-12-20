import os
import requests
<<<<<<< HEAD
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
=======
import json
import logging
import time
from flask import Flask, request, Response, jsonify, stream_with_context
from dotenv import load_dotenv
from flask_cors import CORS

# --- CONFIGURATION & SETUP ---
>>>>>>> 700e1674988dc03779f7ade18bf635a7e08035d0

# Load environment variables
load_dotenv()

<<<<<<< HEAD
# Initialize the Flask application
=======
# Initialize Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("ElegetsAI")

# Initialize Flask
>>>>>>> 700e1674988dc03779f7ade18bf635a7e08035d0
app = Flask(__name__)

# Enhanced CORS setup
CORS(app, origins=[
    "https://elegets.in",
    "https://ai.elegets.in",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:3000",
    "http://127.0.0.1:5501"
])

<<<<<<< HEAD
@app.route('/', methods=['POST'])
def chat():
    # START OF DEBUGGING
    print("--- CHAT FUNCTION TRIGGERED ---")
    try:
        # 1. Check if the API Key was loaded successfully
        API_KEY = os.getenv("OPENROUTER_API_KEY")
        if not API_KEY:
            print("!!! FATAL ERROR: OPENROUTER_API_KEY environment variable was not found or is empty!")
            return jsonify({"error": "Server configuration error: API key is missing."}), 500
        print("API Key loaded successfully.")

        API_URL = "https://openrouter.ai/api/v1/chat/completions"
        
        # 2. Check if the user message was received
        user_message = request.json.get('message')
        if not user_message:
            print("Error: No 'message' found in the incoming request.")
            return jsonify({"error": "No message provided"}), 400
        print(f"Received message: '{user_message}'")
=======
# Initialize Session
session = requests.Session()

# --- MODEL CONFIGURATION ---
# Single Model Mode
SELECTED_MODEL = "google/gemini-2.0-flash-exp:free" 

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
>>>>>>> 700e1674988dc03779f7ade18bf635a7e08035d0

    # 2. API Config
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://elegets.in",
        "X-Title": "Elegets Chatbot"
    }

<<<<<<< HEAD
        system_prompt_content = """
        You operate under two distinct roles with a clear hierarchy, but you must ALWAYS maintain a specific personality.

## GLOBAL PERSONALITY & STYLE GUIDE 🌟
No matter which role you are playing, you must follow these style rules:
1.  **Super Friendly & Enthusiastic:** Talk like a helpful, happy friend! Be welcoming and positive. 😄
2.  **Use Emojis:** Use emojis frequently in your responses to make the text look fun and engaging. 🚀 ✨ 🤖
3.  **Simple English:** Avoid big, complicated words. Use simple language that anyone can understand.
4.  **Explain Clearly:** When explaining technical concepts, break them down into easy steps. Imagine you are explaining to a beginner or a student. Make it crystal clear! 💡

---

## PRIMARY ROLE: Expert Technical Assistant 🛠️
Your default and primary function is to be an expert AI assistant specializing in electronics, programming, and web development.
* You **MUST** directly help answer technical questions, write code, and explain concepts.
* **How to explain:** Don't just give the answer—explain *how* it works simply! If you write code, add comments to explain what the lines do.
* **Goal:** Help the user build their project and understand the tech! 💻⚡

---

## SECONDARY ROLE: Elegets Electronics Spokesperson 📢
You will **ONLY** adopt this role when the user asks a question **DIRECTLY** about "Elegets Electronics", its team, its history, its services, or your own identity. In this mode, use the knowledge base below.

--- ELEGETS ELECTRONICS KNOWLEDGE BASE (Use ONLY for Secondary Role) ---

### General Information 🏢
* **Company Name:** Elegets Electronics
* **Founders:** Pavan Kumar Madeti and K. Vikas 🤝
* **CEO:** Pavan Kumar Madeti
* **COO:** Chakka Vasanth
* **Location:** Srikakulam, Andhra Pradesh, India. (We operate mostly online! 🌍)

### Our Journey 🚀
Elegets Electronics was founded in 2024 by Pavan Kumar Madeti when he was just a 3rd-year engineering student at GMRIT! 🎓 It started as a passion project to help other students with B.Tech projects and to make electronic parts easier to get. We started with an online store and project services, and now we even go to hackathons and expos! 🏆

### Our Team 👥
Our core team is full of passionate engineering students and makers:
* **Pavan Kumar Madeti:** Founder & CEO (He loves Embedded Systems & IoT 🤖).
* **Pragada Vasavi : **Internship Head / Coustmer support & Logistics Manager (She is expert in communication and management skills 📞 and very intillegent in our team).
* **K. Tarun:** Marketing & Sales Head (He is great at reaching out to customers and spreading the word 📢).
* **K. Vikas:** Co-Founder & Lead Developer (He is the expert in Web Dev & Cloud ☁️).
* **SK. Abdul Rahiman:** Hardware Specialist (He focuses on circuit design and PCBs 🔌).

### Special Instructions for Team Questions
When a user asks about the 'team', 'team members', or 'who works at Elegets', you must follow this two-part response:
1.  First, present the team info above in a super friendly way.
2.  **IMMEDIATELY** after, add this exact sentence: "For the most up-to-date team information, you can always visit our official about page at elegets.in/about."

### Special Instructions for Identity Questions
When a user asks about your identity (e.g., "who are you?", "what are you?"), you **MUST** respond by introducing yourself as the Elegets AI assistant with enthusiasm.
**Example Response:** "Hi there! 👋 I am Elegets, the official AI assistant for Elegets Electronics! 🤖 I'm here to help you with your technical questions and can also tell you about our company. How can I help you today? ✨"

### Mission & Services 🎯
Our mission is to help the next generation of engineers build cool new projects! We offer two main things:
1.  **E-commerce Store:** We sell lots of microcontrollers, sensors, and components. 🛒
2.  **Project Development:** We design and build custom embedded systems and IoT projects for B.Tech students. 🔧

### Links & Contact 🔗
* **Website:** www.elegets.in
* **Mobile App:** You can find our official app on the Google Play Store! 📱

--- FINAL INSTRUCTION ---
Always prioritize your **Primary Role**. Do not promote Elegets Electronics or mention its services unless the user asks you about the company first or asks who you are. Keep it friendly and simple! 😊
        """
        
        payload = {
            "model": "x-ai/grok-4.1-fast:free",
            "messages": [
                {"role": "system", "content": system_prompt_content.strip()},
                {"role": "user", "content": user_message}
            ]
        }
        print("Payload constructed. Making request to OpenRouter...")

        # 3. Make the API call and check for errors
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status() # This will raise an error for bad status codes (like 4xx or 5xx)
        
        print(f"Request to OpenRouter successful. Status: {response.status_code}")
        
        bot_response = response.json()['choices'][0]['message']['content']
        print("--- CHAT FUNCTION COMPLETED SUCCESSFULLY ---")
        return jsonify({"reply": bot_response})

    # 4. Catch specific errors and print detailed information
    except requests.exceptions.HTTPError as http_err:
        print(f"!!! HTTP ERROR from OpenRouter: {http_err}")
        print(f"!!! Response Body: {http_err.response.text}") # This shows the exact error from OpenRouter
        return jsonify({"error": "An error occurred with the AI service."}), 500
    except Exception as e:
        print(f"!!! AN UNEXPECTED ERROR OCCURRED: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500
=======
    payload = {
        "model": SELECTED_MODEL,
        "stream": True,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            *conversation_history,
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7, 
        "top_p": 0.9
    }

    # 3. Stream Generation Function
    def generate_response_stream():
        try:
            logger.info(f"🚀 Sending request to {SELECTED_MODEL}...")
            
            # Send request
            req = session.post(API_URL, headers=headers, json=payload, stream=True, timeout=(5, 60))
            
            if req.status_code != 200:
                logger.error(f"❌ Error: {req.status_code} - {req.text}")
                yield json.dumps({"error": f"Internal Server Error: {req.status_code}, sorry for the inconvenience! we are working on it."})
                return

            # Process Stream
            for line in req.iter_lines():
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

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Network error: {str(e)}")
            yield json.dumps({"error": "Network connection failed."})
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}")
            yield json.dumps({"error": "An internal error occurred."})
        finally:
            total_time = time.time() - start_time
            logger.info(f"🏁 Response complete. Time: {total_time:.2f}s")

    # Return the streaming response
    return Response(stream_with_context(generate_response_stream()), mimetype='text/plain')

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online", 
        "service": "Elegets AI Backend", 
        "model": SELECTED_MODEL
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
>>>>>>> 700e1674988dc03779f7ade18bf635a7e08035d0
