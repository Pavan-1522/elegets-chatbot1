import os
import json
import requests
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)

# --- CORS CONFIGURATION ---
# We allow credentials (if needed) and specific origins.
# Note: Ensure your frontend URL is exactly right (http vs https, trailing slash).
CORS(app, resources={r"/*": {"origins": [
    "https://elegets.in",
    "http://127.0.0.1:5501",
    "http://localhost:5500",
    "http://localhost:5000",
    "https://ai.elegets.in",
    "https://elegets-chatbot1.vercel.app" 
]}})

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = """
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

@app.route('/', methods=['POST'])
def chat():
    # 1. Validation
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not API_KEY:
        return jsonify({"error": "Server API key missing."}), 500

    data = request.json
    user_message = data.get('message')
    history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # 2. Build OpenRouter Payload
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://elegets.in",
        "X-Title": "Elegets Chatbot"
    }

    # Construct messages list (System + History + New Message)
    messages = [{"role": "system", "content": SYSTEM_PROMPT.strip()}]
    
    # Optional: Add last few messages from history for context (limit to last 4 to save tokens)
    # Be careful not to include the system prompt twice if it's in history
    for msg in history[-4:]: 
        if msg.get('role') != 'system':
            messages.append({"role": msg.get('role'), "content": msg.get('content')})

    # Add current user message if not already added
    if not messages or messages[-1]['content'] != user_message:
        messages.append({"role": "user", "content": user_message})

    payload = {
        "model": "xiaomi/mimo-v2-flash:free", # Or "google/gemini-2.0-flash-exp:free"
        "messages": messages,
        "stream": True  # <--- CRITICAL: ENABLE STREAMING
    }

    # 3. Define the Generator Function
    def generate():
        try:
            with requests.post(API_URL, headers=headers, json=payload, stream=True) as r:
                r.raise_for_status()
                
                # Iterate over the response stream line by line
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        
                        # OpenRouter sends lines starting with "data: "
                        if decoded_line.startswith('data: '):
                            json_str = decoded_line.replace('data: ', '')
                            
                            # Check for stream end signal
                            if json_str.strip() == '[DONE]':
                                break
                                
                            try:
                                chunk = json.loads(json_str)
                                # Extract content delta
                                content = chunk['choices'][0]['delta'].get('content', '')
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"\n[Error: {str(e)}]"

    # 4. Return the Stream Response
    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
