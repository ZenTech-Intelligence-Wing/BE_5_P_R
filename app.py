import base64
from datetime import datetime
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import sys
import time
import urllib.parse

import cv2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
import numpy as np
from PIL import Image
from pydantic import BaseModel
import requests
import uvicorn


def b64_decode(encoded_str: str) -> str:
    try:
        return base64.b64decode(encoded_str.encode("utf-8")).decode("utf-8")
    except Exception:
        return encoded_str


AI_ENGINES_POOL = [
    {
        "name": "Gemini 2.5 Flash",
        "provider": "google",
        "model": "gemini-2.5-flash",
        "apiKey": b64_decode("QUl6YVN5QVdTbUVoSF9oa3dHNnh6akpVZGVybmgzUjl6Mzl6Mlk4"),
        "supportsVision": True,
    },
    {
        "name": "Groq Llama 3.3 70B",
        "provider": "groq",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "apiKey": "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",
        "supportsVision": False,
    }
]

WATERMARK_LOGO_PATH = "watermark.jpeg"


def add_visible_watermark_pil(img):
    img = img.convert("RGBA")

    if not os.path.exists(WATERMARK_LOGO_PATH):
        print(f"[ZIMAGE ERROR] Watermark file NOT found at exact path: {WATERMARK_LOGO_PATH}")
        return img.convert("RGB")

    logo = Image.open(WATERMARK_LOGO_PATH).convert("RGBA")

    datas = logo.getdata()
    newData = []
    for item in datas:
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    logo.putdata(newData)

    target_w = max(80, int(img.width * 0.12))
    ratio = target_w / logo.width
    logo = logo.resize((target_w, int(logo.height * ratio)))

    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    pos = (img.width - logo.width - 20, img.height - logo.height - 20)
    layer.paste(logo, pos, logo)

    return Image.alpha_composite(img, layer).convert("RGB")


def generate_watermarked_image_bytes(image_bytes):
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    img = add_visible_watermark_pil(img)
    out = BytesIO()
    img.save(out, format="JPEG", quality=95)
    return out.getvalue()


class ZenTechBackendEngine:
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.system_instruction = (
            "You are 5onam AI, an advanced AI assistant operating on the Zen-Tech"
            " platform, managed under T-Service HQ (T-Service est. June 1, 2021;"
            " Zen-Tech est. March 13, 2023). You have a professional, helpful, and"
            " friendly persona. Always provide accurate and supportive answers."
        )

        self.safety_settings = [
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
        ]

        try:
            self.baseline_client = genai.Client(api_key=self.gemini_api_key)
            config = types.GenerateContentConfig(system_instruction=self.system_instruction, safety_settings=self.safety_settings)
            self.baseline_chat = self.baseline_client.chats.create(model="gemini-2.5-flash", config=config)
            print("[SYSTEM] Baseline Gemini 2.5 Engine running perfectly.")
        except Exception as e:
            print(f"[ERROR] Baseline startup exception: {e}")

    def generate_image(self, prompt: str) -> str:
        safe_prompt = f"{prompt}, no human faces, no human figures, no avatars, highly detailed, 4k"
        encoded_prompt = urllib.parse.quote(safe_prompt)
        seed = int(time.time())

        POLLINATIONS_API_KEY = "sk_G8nhKDsZ44Hu3GqsEwJvD2u8HdytEAL0"
        url = f"https://gen.pollinations.ai/image/{encoded_prompt}?model=flux&width=1024&height=1024&seed={seed}&nologo=true&key={POLLINATIONS_API_KEY}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}

        try:
            response = requests.get(url, headers=headers, timeout=45)
            if response.status_code == 200:
                try:
                    watermarked_bytes = generate_watermarked_image_bytes(response.content)
                    img_base64 = base64.b64encode(watermarked_bytes).decode("utf-8")
                except Exception as watermark_err:
                    img_base64 = base64.b64encode(response.content).decode("utf-8")
                return f"![Zimage Generated](data:image/jpeg;base64,{img_base64})"
            else:
                return f"**[IMAGE ERROR]** Pollinations API blocked the request (HTTP {response.status_code}). Details: {response.text}"
        except Exception as e:
            return f"**[IMAGE ERROR]** Connection to Pollinations failed. Details: {str(e)}"

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

GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or AI_ENGINES_POOL[0]["apiKey"]
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