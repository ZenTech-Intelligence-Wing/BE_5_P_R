import base64
from datetime import datetime
import json
import os
import time
import urllib.parse

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pydantic import BaseModel
import requests
import uvicorn

# ================= SECURE ENVIRONMENT VARIABLES =================
# Keys are pulled securely from Render's Environment Variables
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

AI_ENGINES_POOL = [
    {
        "name": "Gemini 2.5 Flash",
        "provider": "google",
        "model": "gemini-2.5-flash",
        "apiKey": GEMINI_KEY,
        "supportsVision": True,
    },
    {
        "name": "Groq Llama 3.3 70B",
        "provider": "groq",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "apiKey": GROQ_KEY,
        "supportsVision": False,
    }
]


class ZenTechBackendEngine:
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.system_instruction = (
            "You are 5onam AI, an advanced AI assistant operating on the Zen-Tech"
            " platform, managed under T-Service HQ. You have a professional,"
            " helpful, and friendly persona. Always provide accurate answers."
        )

        self.safety_settings = [
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
        ]
        
        if not self.gemini_api_key:
            print("[WARN] Baseline Gemini API key missing. Ensure GEMINI_API_KEY is set in Render!")
            return

        try:
            self.baseline_client = genai.Client(api_key=self.gemini_api_key)
            config = types.GenerateContentConfig(system_instruction=self.system_instruction, safety_settings=self.safety_settings)
            self.baseline_chat = self.baseline_client.chats.create(model="gemini-2.5-flash", config=config)
            print("[SYSTEM] Baseline Gemini 2.5 Engine running perfectly.")
        except Exception as e:
            print(f"[ERROR] Baseline startup exception: {e}")

    def generate_image(self, prompt: str) -> str:
        # 1. Format & encode prompt
        safe_prompt = f"{prompt}, no human faces, no avatars, highly detailed, 4k"
        encoded_prompt = urllib.parse.quote(safe_prompt)
        seed = int(time.time())

        # 2. Build the active gen.pollinations.ai URL
        url = f"https://gen.pollinations.ai/image/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true"
        
        # 3. DIRECT BROWSER BYPASS:
        # Pass the URL directly back so the user's browser loads it.
        # This completely bypasses Cloudflare bot protection on Render!
        return f"![Zimage Generated]({url})"

    def dynamic_route_response(self, user_input: str, target_mode: str) -> str:
        if not user_input.strip():
            return "Please enter a question or prompt."

        selected_engine = next((e for e in AI_ENGINES_POOL if e["name"].lower() == target_mode.lower()), None)

        if not selected_engine or selected_engine["provider"] == "google":
            model_to_use = selected_engine["model"] if selected_engine else "gemini-2.5-flash"
            try:
                client = genai.Client(api_key=(selected_engine["apiKey"] if selected_engine else self.gemini_api_key))
                config = types.GenerateContentConfig(system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                chat = client.chats.create(model=model_to_use, config=config)
                response = chat.send_message(user_input)
                return response.text or ""
            except Exception as e:
                try:
                    res = self.baseline_chat.send_message(user_input)
                    return res.text or ""
                except Exception as ex:
                    return f"[API Error]: Engine fallback processing failure. Details: {ex}"

        provider_url = selected_engine.get("url")
        api_key = selected_engine.get("apiKey")
        model_name = selected_engine.get("model")

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": model_name, "messages": [{"role": "system", "content": self.system_instruction}, {"role": "user", "content": user_input}]}

        try:
            response = requests.post(provider_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[Provider Error]: {selected_engine['name']} returned HTTP {response.status_code} - {response.text}"
        except Exception as e:
            return f"[Connection Error]: Failed to query {selected_engine['name']}. Details: {str(e)}"


# ==========================================
# FASTAPI WEB SERVER SETUP
# ==========================================

app = FastAPI(title="ZenTech Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "running Successfully"}

# Start Baseline engine securely
engine = ZenTechBackendEngine(gemini_api_key=GEMINI_KEY)

class ChatRequest(BaseModel):
    message: str
    mode: str = "Standard"

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        if req.mode == "Zimage Generation":
            reply = engine.generate_image(req.message)
        else:
            reply = engine.dynamic_route_response(req.message, req.mode)
        return {"response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
