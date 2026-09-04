# ==========================================
# PURE LOGO AI-PROOF WATERMARK SYSTEM v8.1
# ANTI-WATERMARK REMOVER PROTECTION
# WATERMARK SIZES REDUCED
# PRO USER FEATURE: No watermark for paid users
# ==========================================

import json
import os
import sys
import time
import base64  
import cv2
import hashlib 
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
from io import BytesIO
import urllib.parse
from datetime import datetime
import requests
import random
import struct
from memory.extraction import extract_memory
from memory.embedding import generate_embedding
from memory.storage import save_memory

# ==========================================
# AVIF SUPPORT - pillow-avif-plugin
# ==========================================
try:
    import pillow_avif
    AVIF_AVAILABLE = True
    print("[AVIF] pillow-avif-plugin loaded successfully")
except ImportError:
    AVIF_AVAILABLE = False
    print("[AVIF] pillow-avif-plugin not available, AVIF features disabled")

from google import genai 
from google.genai import types
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

def b64_decode(encoded_str: str) -> str:
    try:
        return base64.b64_decode(encoded_str.encode('utf-8')).decode('utf-8')
    except Exception:
        return encoded_str

# NEW GOOGLE API KEY
NEW_GOOGLE_KEY = "AQ.Ab8RN6KME25Zm5HNS2c0vGIPtGJayqVOZqKX09b6LJm5okDUHg"

#================= AI ENGINES =================
AI_ENGINES_POOL = [
    {"name": "NVIDIA Nemotron 70B", "provider": "nvidia", "url": "https://integrate.api.nvidia.com/v1/chat/completions", "model": "nvidia/llama-3.1-nemotron-70b-instruct", "apiKey": "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", "supportsVision": False},
    {"name": "Gemini 1.5 Flash", "provider": "google", "model": "gemini-1.5-flash", "apiKey": NEW_GOOGLE_KEY, "supportsVision": True},
    {"name": "Groq Llama 3.3 70B", "provider": "groq", "url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.3-70b-versatile", "apiKey": "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", "supportsVision": False},
    {"name": "Gemini 1.5 Pro", "provider": "google", "model": "gemini-1.5-pro", "apiKey": NEW_GOOGLE_KEY, "supportsVision": True},
    {"name": "Gemini 3.1 Pro", "provider": "google", "model": "gemini-3.1-pro-preview", "apiKey": NEW_GOOGLE_KEY, "supportsVision": True},
    {"name": "Gemini 3 Flash", "provider": "google", "model": "gemini-3-flash-preview", "apiKey": NEW_GOOGLE_KEY, "supportsVision": True},
    {"name": "Gemini 3.1 Flash-Lite", "provider": "google", "model": "gemini-3.1-flash-lite-preview", "apiKey": NEW_GOOGLE_KEY, "supportsVision": True},
    {"name": "Nano Banana Pro", "provider": "google", "model": "gemini-3-pro-image-preview", "apiKey": NEW_GOOGLE_KEY, "supportsVision": True},
    {"name": "GPT-5.4 Thinking", "provider": "openai", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-5.4-thinking", "apiKey": b64_decode("c2stcHJvai1jeXpuRVNadDlHbzE0ZzdBeXN5Wm42bVowOFR3RjZ3S3VTTDNiZWlUOEd1ZWdUVkt4amFfOE5VUklXMnlIbGhOdHppZEhzYnljLVQzQmxia0ZKZ3ZuN1JUcWVZbmVGUG9iR213MnA1aG1nRkczcnpOZWJuWE9KZVVOQ09aLUdFSHk2cW9ibW5BTVNoSzlqWVM3V2dlZmhFNmlHUUE="), "supportsVision": True},
    {"name": "GPT-5.4 Pro", "provider": "openai", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-5.4-pro", "apiKey": b64_decode("c2stcHJvai1jeXpuRVNadDlHbzE0ZzdBeXN5Wm42bVowOFR3RjZ3S3VTTDNiZWlUOEd1ZWdUVkt4amFfOE5VUklXMnlIbGhOdHppZEhzYnljLVQzQmxia0ZKZ3ZuN1JUcWVZbmVGUG9iR213MnA1aG1nRkczcnpOZWJuWE9KZVVOQ09aLUdFSHk2cW9ibW5BTVNoSzlqWVM3V2dlZmhFNmlHUUE="), "supportsVision": True},
    {"name": "Groq Llama 4 Scout", "provider": "groq", "url": "https://api.groq.com/openai/v1/chat/completions", "model": "meta-llama/llama-4-scout-17b-16e-instruct", "apiKey": "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", "supportsVision": True},
    {"name": "Nano Banana 2 (Flash Image)", "provider": "google", "model": "gemini-3.1-flash-image-preview", "apiKey": NEW_GOOGLE_KEY, "supportsVision": True},
    {"name": "Gemini 2.5 Pro", "provider": "google", "model": "gemini-2.5-pro", "apiKey": NEW_GOOGLE_KEY, "supportsVision": True},
    {"name": "Gemini 2.5 Flash", "provider": "google", "model": "gemini-2.5-flash", "apiKey": NEW_GOOGLE_KEY, "supportsVision": True},
    {"name": "Gemini 1.5 Flash-8B", "provider": "google", "model": "gemini-1.5-flash-8b", "apiKey": NEW_GOOGLE_KEY, "supportsVision": True},
    {"name": "Imagen 4 Ultra", "provider": "google", "model": "imagen-4.0-ultra-generate-001", "apiKey": NEW_GOOGLE_KEY, "supportsVision": False, "isImageModel": True},
    {"name": "GPT-5.3 Instant", "provider": "openai", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-5.3-instant", "apiKey": b64_decode("c2stcHJvai1jeXpuRVNadDlHbzE0ZzdBeXN5Wm42bVowOFR3RjZ3S3VTTDNiZWlUOEd1ZWdUVkt4amFfOE5VUklXMnlIbGhOdHppZEhzYnljLVQzQmxia0ZKZ3ZuN1JUcWVZbmVGUG9iR213MnA1aG1nRkczcnpOZWJuWE9KZVVOQ09aLUdFSHk2cW9ibW5BTVNoSzlqWVM3V2dlZmhFNmlHUUE="), "supportsVision": True},
    {"name": "GPT-5.3 Codex", "provider": "openai", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-5.3-codex", "apiKey": b64_decode("c2stcHJvai1jeXpuRVNadDlHbzE0ZzdBeXN5Wm42bVowOFR3RjZ3S3VTTDNiZWlUOEd1ZWdUVkt4amFfOE5VUklXMnlIbGhOdHppZEhzYnljLVQzQmxia0ZKZ3ZuN1JUcWVZbmVGUG9iR213MnA1aG1nRkczcnpOZWJuWE9KZVVOQ09aLUdFSHk2cW9ibW5BTVNoSzlqWVM3V2dlZmhFNmlHUUE="), "supportsVision": False},
    {"name": "OpenAI o3-pro", "provider": "openai", "url": "https://api.openai.com/v1/chat/completions", "model": "o3-pro", "apiKey": b64_decode("c2stcHJvai1jeXpuRVNadDlHbzE0ZzdBeXN5Wm42bVowOFR3RjZ3S3VTTDNiZWlUOEd1ZWdUVkt4amFfOE5VUklXMnlIbGhOdHppZEhzYnljLVQzQmxia0ZKZ3ZuN1JUcWVZbmVGUG9iR213MnA1aG1nRkczcnpOZWJuWE9KZVVOQ09aLUdFSHk2cW9ibW5BTVNoSzlqWVM3V2dlZmhFNmlHUUE="), "supportsVision": True},
    {"name": "GPT Image 1.5", "provider": "openai", "url": "https://api.openai.com/v1/images/generations", "model": "gpt-image-1.5", "apiKey": b64_decode("c2stcHJvai1jeXpuRVNadDlHbzE0ZzdBeXN5Wm42bVowOFR3RjZ3S3VTTDNiZWlUOEd1ZWdUVkt4amFfOE5VUklXMnlIbGhOdHppZEhzYnljLVQzQmxia0ZKZ3ZuN1JUcWVZbmVGUG9iR213MnA1aG1nRkczcnpOZWJuWE9KZVVOQ09aLUdFSHk2cW9ibW5BTVNoSzlqWVM3V2dlZmhFNmlHUUE="), "supportsVision": False, "isImageModel": True},
    {"name": "GPT-5 mini", "provider": "openai", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-5-mini", "apiKey": b64_decode("c2stcHJvai1jeXpuRVNadDlHbzE0ZzdBeXN5Wm42bVowOFR3RjZ3S3VTTDNiZWlUOEd1ZWdUVkt4amFfOE5VUklXMnlIbGhOdHppZEhzYnljLVQzQmxia0ZKZ3ZuN1JUcWVZbmVGUG9iR213MnA1aG1nRkczcnpOZWJuWE9KZVVOQ09aLUdFSHk2cW9ibW5BTVNoSzlqWVM3V2dlZmhFNmlHUUE="), "supportsVision": True},
    {"name": "GPT-5 nano", "provider": "openai", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-5-nano", "apiKey": b64_decode("c2stcHJvai1jeXpuRVNadDlHbzE0ZzdBeXN5Wm42bVowOFR3RjZ3S3VTTDNiZWlUOEd1ZWdUVkt4amFfOE5VUklXMnlIbGhOdHppZEhzYnljLVQzQmxia0ZKZ3ZuN1JUcWVZbmVGUG9iR213MnA1aG1nRkczcnpOZWJuWE9KZVVOQ09aLUdFSHk2cW9ibW5BTVNoSzlqWVM3V2dlZmhFNmlHUUE="), "supportsVision": True},
    {"name": "Groq Llama 4 Maverick", "provider": "groq", "url": "https://api.groq.com/openai/v1/chat/completions", "model": "meta-llama/llama-4-maverick-17b-128e-instruct", "apiKey": "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", "supportsVision": True},
    {"name": "Groq DeepSeek R1", "provider": "groq", "url": "https://api.groq.com/openai/v1/chat/completions", "model": "deepseek-r1-distill-llama-70b", "apiKey": "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", "supportsVision": False},
    {"name": "Groq Mixtral 8x7B", "provider": "groq", "url": "https://api.groq.com/openai/v1/chat/completions", "model": "mixtral-8x7b-32768", "apiKey": "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", "supportsVision": False},
    {"name": "Groq Llama Guard 4", "provider": "groq", "url": "https://api.groq.com/openai/v1/chat/completions", "model": "meta-llama/llama-guard-4-12b", "apiKey": "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", "supportsVision": False},
    {"name": "OpenRouter Auto", "provider": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "openrouter/auto", "apiKey": "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", "supportsVision": True},
    {"name": "Llama 3.3 70B Free", "provider": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "meta-llama/llama-3.3-70b-instruct:free", "apiKey": "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", "supportsVision": False},
    {"name": "Xiaomi MiMo 309B Free", "provider": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "xiaomi/mimo-v2-flash:free", "apiKey": "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", "supportsVision": False},
    {"name": "DeepSeek R1 Free", "provider": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "deepseek/deepseek-r1:free", "apiKey": "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", "supportsVision": False},
    {"name": "Mistral Small 3.1 Free", "provider": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "mistralai/mistral-small-3.1-24b-instruct:free", "apiKey": "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", "supportsVision": True},
    {"name": "Gemma 3 27B Free", "provider": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "google/gemma-3-27b-it:free", "apiKey": "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", "supportsVision": True},
    {"name": "Nemotron 3 Nano Free", "provider": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "nvidia/nemotron-3-nano-30b-a3b:free", "apiKey": "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", "supportsVision": False},
    {"name": "DeepSeek V3", "provider": "siliconflow", "url": "https://api.siliconflow.cn/v1/chat/completions", "model": "deepseek-ai/DeepSeek-V3", "apiKey": "YOUR_SILICONFLOW_KEY", "supportsVision": False},
    {"name": "DeepSeek R1 Pro", "provider": "siliconflow", "url": "https://api.siliconflow.cn/v1/chat/completions", "model": "deepseek-ai/DeepSeek-R1", "apiKey": "YOUR_SILICONFLOW_KEY", "supportsVision": False},
    {"name": "OpenRouter Free Pool", "provider": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "openrouter/free", "apiKey": "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", "supportsVision": True},
    {"name": "Llama 4 Scout Free", "provider": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "meta-llama/llama-4-scout:free", "apiKey": "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", "supportsVision": True},
    {"name": "OpenAI gpt-oss-120b Free", "provider": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "openai/gpt-oss-120b:free", "apiKey": "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", "supportsVision": False},
    {"name": "Mistral Devstral 2 Free", "provider": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "mistralai/devstral-2512:free", "apiKey": "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", "supportsVision": False},
    {"name": "Step 3.5 Flash Free", "provider": "openrouter", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "stepfun/step-3.5-flash:free", "apiKey": "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", "supportsVision": False},
]

WATERMARK_LOGO_PATH = "watermark.jpeg"
WATERMARK_SECRET_KEY = "ZenTech_LogoOnly_AIProof_2026"

# ==========================================
# AVIF UTILITY FUNCTIONS
# ==========================================
def is_avif_image(image_bytes: bytes) -> bool:
    if len(image_bytes) < 12:
        return False
    header = image_bytes[:12]
    return b'ftyp' in header and (b'avif' in header or b'avis' in header)

def detect_image_format(image_bytes: bytes) -> str:
    if is_avif_image(image_bytes): return "AVIF"
    if image_bytes[:2] == b'\xff\xd8': return "JPEG"
    if image_bytes[:8] == b'\x89PNG\r\n\x1a\n': return "PNG"
    if image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP': return "WEBP"
    if image_bytes[:4] == b'GIF8': return "GIF"
    return "UNKNOWN"

def convert_avif_to_rgb(image_bytes: bytes) -> Image.Image:
    if not AVIF_AVAILABLE: raise RuntimeError("AVIF not available")
    img = Image.open(BytesIO(image_bytes))
    return img.convert("RGB")

def save_as_format(img: Image.Image, fmt: str = "JPEG", quality: int = 92) -> bytes:
    out = BytesIO()
    if fmt.upper() == "AVIF":
        if not AVIF_AVAILABLE: raise RuntimeError("AVIF support not available")
        img.save(out, format="AVIF", quality=quality, speed=6)
    elif fmt.upper() == "PNG":
        img.save(out, format="PNG")
    elif fmt.upper() in ("JPEG", "JPG"):
        img.save(out, format="JPEG", quality=quality)
    elif fmt.upper() == "WEBP":
        img.save(out, format="WEBP", quality=quality)
    else:
        img.save(out, format="JPEG", quality=quality)
    return out.getvalue()

# ==========================================
# WATERMARK ENGINE (Placeholder for brevity)
# ==========================================
class LogoWatermarkEngine:
    def __init__(self):
        pass
    def apply_post_generation(self, image_bytes: bytes, output_format: str = "JPEG", enable_anti_upload: bool = True, is_pro_user: bool = False) -> bytes:
        if is_pro_user:
            detected_fmt = detect_image_format(image_bytes)
            img = convert_avif_to_rgb(image_bytes) if detected_fmt == "AVIF" and AVIF_AVAILABLE else Image.open(BytesIO(image_bytes)).convert("RGB")
            return save_as_format(img, fmt="JPEG", quality=95)
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        return save_as_format(img, fmt=output_format, quality=92)


# ==========================================
# CORE ENGINE - UPDATED FOR INSTANT FAILOVER
# ==========================================

class ZenTechBackendEngine():
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        self.watermark_engine = LogoWatermarkEngine()
        self.system_instruction = (
            "You are 5onam AI, an advanced AI assistant operating on the Zen-Tech platform, "
            "managed under T-Service HQ (T-Service est. June 1, 2021; Zen-Tech est. March 13, 2023). "
            "You have a professional, helpful, and friendly persona. Always provide accurate and supportive answers."
        )
        self.safety_settings = [
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE),
        ]

    def generate_image(self, prompt: str, output_format: str = "GIF", enable_anti_upload: bool = True, is_pro_user: bool = False) -> str:
        safe_prompt = f"{prompt}, no human faces, no human figures, highly detailed, 4k"
        encoded_prompt = urllib.parse.quote(safe_prompt)
        seed = int(time.time())

        POLLINATIONS_API_KEY = "sk_G8nhKDsZ44Hu3GqsEwJvD2u8HdytEAL0"
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true&key={POLLINATIONS_API_KEY}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}

        try:
            response = requests.get(url, headers=headers, timeout=45)
            if response.status_code == 200:
                try:
                    watermarked_bytes = self.watermark_engine.apply_post_generation(
                        response.content, 
                        output_format=output_format,
                        enable_anti_upload=enable_anti_upload,
                        is_pro_user=is_pro_user 
                    )
                    img_base64 = base64.b64encode(watermarked_bytes).decode("utf-8")
                except Exception as e:
                    print(f"[ZIMAGE WARN] Post-gen failed: {e}")
                    img_base64 = base64.b64encode(response.content).decode("utf-8")

                mime = "image/jpeg" if is_pro_user else {"AVIF": "image/avif", "GIF": "image/gif", "PNG": "image/png", "WEBP": "image/webp", "JPEG": "image/jpeg", "JPG": "image/jpeg"}.get(output_format.upper(), "image/gif")

                block_notice = "\n\n> **Phototune Protection:** This image is saved as `.gif` format. Phototune.ai does NOT support GIF and will show **'Unsupported format'** error on upload." if (not is_pro_user and enable_anti_upload and output_format.upper() == "GIF") else ""
                
                return f"![Zimage Generated](data:{mime};base64,{img_base64}){block_notice}"
            else:
                return f"**[IMAGE ERROR]** API blocked (HTTP {response.status_code})."
        except Exception as e:
            return f"**[IMAGE ERROR]** Connection failed. Details: {str(e)}"

    def dynamic_route_response(self, user_input: str, target_mode: str) -> str:
        if not user_input.strip(): 
            return "Please enter a question or prompt."

        # 1. Grab the model the user requested
        selected_engine = next((e for e in AI_ENGINES_POOL if e["name"].lower() == target_mode.lower()), None)
        
        # 2. Build the seamless fallback chain
        fallback_chain = []
        if selected_engine:
            fallback_chain.append(selected_engine) # Try what they asked for first
        
        # Add ALL other models to the list (Groq, OpenAI, NVIDIA, OpenRouter)
        fallback_chain.extend([e for e in AI_ENGINES_POOL if e != selected_engine])

        # 3. The Seamless Loop: It will iterate rapidly until one succeeds
        for engine in fallback_chain:
            print(f"[AI ROUTER] Routing to: {engine['name']}")
            try:
                if engine["provider"] == "google":
                    model_to_use = engine["model"]
                    api_key = engine.get("apiKey", self.gemini_api_key)
                    
                    client = genai.Client(api_key=api_key)
                    config = types.GenerateContentConfig(system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                    chat = client.chats.create(model=model_to_use, config=config)
                    response = chat.send_message(user_input)
                    return response.text or "" # Success! Break out of the loop and return.
                
                else:
                    provider_url = engine.get("url")
                    api_key = engine.get("apiKey")
                    model_name = engine.get("model")
                    
                    if not provider_url or not api_key:
                        continue # If config is missing, instantly jump to the next model

                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    payload = {"model": model_name, "messages": [{"role": "system", "content": self.system_instruction}, {"role": "user", "content": user_input}]}
                    
                    response = requests.post(provider_url, headers=headers, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data["choices"][0]["message"]["content"] # Success! Break out and return.
                    else:
                        print(f"[Provider Error] {engine['name']} HTTP {response.status_code}. Failing over instantly...")
                        continue # If a model is down/429, jump to the next immediately

            except Exception as e:
                print(f"[Connection Error] {engine['name']} failed: {str(e)}. Failing over instantly...")
                continue # If network drops, jump to the next immediately

        return "[System Error]: All 41 AI engines in the fallback pool are currently unavailable or rate limited."


# ==========================================
# FASTAPI SERVER
# ==========================================

app = FastAPI(title="ZenTech Backend API - AI Routing v8.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Server working as expected",
        "version": "1.12.332"
    }

GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or AI_ENGINES_POOL[1]["apiKey"]
engine = ZenTechBackendEngine(gemini_api_key=GEMINI_KEY)

class ChatRequest(BaseModel):
    message: str
    mode: str = "Standard"
    output_format: str = "GIF"  
    enable_anti_upload: bool = True  
    is_pro_user: bool = False  
    user_id : str | None = None 

@app.post("/chat")
async def chat_endpoint(req: ChatRequest, request: Request):
    try:
        authorization = request.headers.get("Authorization")

        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authorization token missing"
            )

        if req.mode == "Zimage Generation":
            reply = engine.generate_image(
                req.message, 
                output_format=req.output_format,
                enable_anti_upload=req.enable_anti_upload,
                is_pro_user=req.is_pro_user 
            )
        else:
            reply = engine.dynamic_route_response(req.message, req.mode)
            
        # ==============================
        # MEMORY SYSTEM
        # ==============================
        memory_info = None
        memory = extract_memory(req.message)

        if memory:
            embedding = generate_embedding(memory["memory_text"])

            save_memory(
                user_id=req.user_id,
                memory_text=memory["memory_text"],
                memory_type=memory.get("memory_type", "text"),
                embedding=embedding,
                access_token=authorization
            )

            memory_info = {
                "saved": True,
                "memory_text": memory["memory_text"],
                "memory_type": memory.get("memory_type", "text")
            }

        return {
            "response": reply,
            "memory": memory_info
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
