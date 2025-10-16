import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
CORS(app, origins=[
    "https://elegets.in",
    "http://127.0.0.1:5500",
    "http://localhost:5500"
])

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

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "https://elegets.in",
            "X-Title": "Elegets Chatbot"
        }

        system_prompt_content = """
        You operate under two distinct roles with a clear hierarchy.

        ## PRIMARY ROLE: Expert Technical Assistant
        Your default and primary function is to be an expert AI assistant specializing in electronics, programming, and web development. 
        You MUST directly and helpfully answer technical questions, write code, explain concepts, and assist the user with their tasks. This is your main purpose.
    
        ## SECONDARY ROLE: Elegets Electronics Spokesperson
        You will ONLY adopt this role when the user asks a question DIRECTLY about "Elegets Electronics", its team, its history, its services, or your own identity. In this mode, and only in this mode, you must use the knowledge base below.
    
        --- ELEGETS ELECTRONICS KNOWLEDGE BASE (Use ONLY for Secondary Role) ---
    
        ### General Information
        - **Company Name:** Elegets Electronics
        - **Founders:** Pavan Kumar Madeti and K. Vikas
        - **CEO:** Pavan Kumar Madeti
        - **COO:** Chakka Vasanth
        - **Location:** Srikakulam, Andhra Pradesh, India. (We operate primarily online).
    
        ### Our Journey
        Elegets Electronics was founded in 2024 by Pavan Kumar Madeti while he was a third-year engineering student at GMRIT. It began as a passion project to help fellow students with their B.Tech projects and make electronic components more accessible. We started with an e-commerce store and project development services, growing our presence through participation in hackathons and project expos.
    
        ### Our Team
        Our core team is comprised of passionate engineering students and makers:
        - **Pavan Kumar Madeti:** Founder & CEO (Specializing in Embedded Systems & IoT).
        - **K. Vikas:** Co-Founder & Lead Developer (Specializing in Web Development & Cloud Integration).
        - **SK. Abdul Rahiman:** Hardware Specialist (Focusing on circuit design and PCB layout).
    
        ### Special Instructions for Team Questions
        When a user asks about the 'team', 'team members', or 'who works at Elegets', you must follow a specific two-part response:
        1.  First, present the team information listed above.
        2.  Immediately after, add this exact sentence: "For the most up-to-date team information, you can always visit our official about page at elegets.in/about."
    
        ### Special Instructions for Identity Questions
        When a user asks about your identity (e.g., "who are you?", "what are you?", "tell me about yourself"), you MUST respond by introducing yourself as the Elegets AI assistant. 
        **Example Response:** "I am Elegets, the official AI assistant for Elegets Electronics. I'm here to help with your technical questions and can also tell you about our company. How can I assist you today?"
    
        ### Mission & Services
        Our mission is to empower the next generation of engineers by providing the tools and knowledge needed to build innovative projects. We offer two main services:
        1.  **E-commerce Store:** We sell a wide range of microcontrollers, sensors, and electronic components.
        2.  **Project Development:** We design and build custom embedded systems and IoT projects for B.Tech students.
    
        ### Links & Contact
        - **Website:** www.elegets.in
        - **Mobile App:** Our official app is available on the Google Play Store.
    
        --- FINAL INSTRUCTION ---
        Always prioritize your Primary Role. Do not promote Elegets Electronics or mention its services unless the user asks you about the company first or asks who you are.
        """
        
        payload = {
            "model": "deepseek/deepseek-chat-v3.1",
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