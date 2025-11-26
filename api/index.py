import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
CORS(app, origins=["*"]) # Allow all origins for testing (Change to specific domains later)

# --- CONFIGURATION ---
# List models in order of preference. If the first fails, it tries the next.
MODEL_LIST = [
    "google/gemini-2.0-flash-exp:free",      # 1. Fast & Smart
    "deepseek/deepseek-r1:free",             # 2. Good reasoning
    "meta-llama/llama-3-8b-instruct:free",   # 3. Reliable backup
    "microsoft/phi-3-mini-128k-instruct:free" # 4. Last resort
]

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
Always prioritize your **Primary Role**. Do not promote Elegets Electronics or mention its services unless the user asks you about the company first or asks who you are. Keep it friendly and simple! 😊"""

@app.route('/', methods=['POST'])
def chat():
    print("--- CHAT FUNCTION TRIGGERED ---")
    
    # 1. Check API Key
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not API_KEY:
        print("!!! FATAL ERROR: OPENROUTER_API_KEY is missing!")
        return jsonify({"error": "Server configuration error."}), 500

    # 2. Get User Message safely
    data = request.get_json(silent=True) # Returns None if not JSON
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    user_message = data['message']
    print(f"Received message: '{user_message}'")

    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://elegets.in",
        "X-Title": "Elegets Chatbot"
    }

    # 3. FALLBACK LOOP SYSTEM
    last_error = ""
    
    for model in MODEL_LIST:
        print(f"Attempting to send request to model: {model}...")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user", "content": user_message}
            ]
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            
            # If successful (200 OK)
            if response.status_code == 200:
                bot_response = response.json()['choices'][0]['message']['content']
                print(f"--- SUCCESS with {model} ---")
                return jsonify({"reply": bot_response})
            
            # If Rate Limit (429) or Server Error (5xx), print and Try Next Model
            elif response.status_code == 429 or response.status_code >= 500:
                print(f"!!! Model {model} failed with status {response.status_code}. Trying next...")
                last_error = f"Model {model} busy."
                continue # Go to top of loop for next model
            
            # If Client Error (400, 401), Stop immediately (don't retry)
            else:
                print(f"!!! Client Error {response.status_code}: {response.text}")
                return jsonify({"error": f"API Error: {response.text}"}), response.status_code

        except Exception as e:
            print(f"!!! Connection Error with {model}: {e}")
            last_error = str(e)
            continue

    # 4. If Loop finishes and nothing worked
    print("!!! All models failed.")
    return jsonify({"error": "All AI models are currently busy. Please try again in a moment.", "details": last_error}), 503

# --- CRITICAL ADDITION: RUN THE SERVER ---
if __name__ == '__main__':
    # Debug=True helps you see errors in the terminal
    # Host='0.0.0.0' allows access from other devices on the network
    app.run(debug=True, port=5000)