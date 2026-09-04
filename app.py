# ==========================================
# PURE LOGO AI-PROOF WATERMARK SYSTEM v8.1
# ANTI-WATERMARK REMOVER PROTECTION
# RENDER.COM MEMORY & PORT TIMEOUT OPTIMIZED
# ==========================================

import json
import os
import sys
import time
import base64  
import hashlib 
import urllib.parse
from datetime import datetime
import requests
import random
import struct

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
# WATERMARK CLASSES (Lazy Loaded)
# ==========================================

class HighlyVisibleLogoOverlay:
    def __init__(self, logo_path: str):
        self.logo_path = logo_path
    def apply(self, img):
        import os
        from PIL import Image
        if not os.path.exists(self.logo_path): return img
        img = img.convert("RGBA")
        logo = Image.open(self.logo_path).convert("RGBA")
        datas = logo.getdata()
        newData = [(255, 255, 255, 0) if (item[0] > 210 and item[1] > 210 and item[2] > 210) else item for item in datas]
        logo.putdata(newData)
        w, h = img.size
        target_w = max(60, int(w * 0.08))
        ratio = target_w / logo.width
        logo_resized = logo.resize((target_w, int(logo.height * ratio)))
        logo_data = list(logo_resized.getdata())
        transparent = [(r, g, b, int(a * 0.75)) for r, g, b, a in logo_data]
        logo_resized.putdata(transparent)
        layer = Image.new("RGBA", img.size, (0,0,0,0))
        pos = (w - logo_resized.width - 15, h - logo_resized.height - 15)
        layer.paste(logo_resized, pos, logo_resized)
        return Image.alpha_composite(img, layer).convert("RGB")

class TextureBlendedLogo:
    def __init__(self, logo_path: str):
        self.logo_path = logo_path
    def apply(self, img):
        import os
        import numpy as np
        import cv2
        from PIL import Image
        if not os.path.exists(self.logo_path): return img
        img_np = np.array(img).astype(np.float32)
        h, w = img_np.shape[:2]
        logo = Image.open(self.logo_path).convert("RGBA")
        datas = logo.getdata()
        newData = [(255, 255, 255, 0) if (item[0] > 220 and item[1] > 220 and item[2] > 220) else item for item in datas]
        logo.putdata(newData)
        target_w = max(80, int(w * 0.10))
        ratio = target_w / logo.width
        logo = logo.resize((target_w, int(logo.height * ratio)))
        logo_np = np.array(logo).astype(np.float32)
        lx, ly = logo_np.shape[1], logo_np.shape[0]
        x_pos, y_pos = w - lx - 20, h - ly - 20
        if x_pos < 0 or y_pos < 0: return img
        local = img_np[y_pos:y_pos+ly, x_pos:x_pos+lx]
        local_mean = np.mean(local, axis=(0,1))
        local_std = np.std(local, axis=(0,1))
        alpha = logo_np[:, :, 3:4] / 255.0
        logo_rgb = logo_np[:, :, :3]
        logo_adjusted = logo_rgb.copy()
        for c in range(3):
            logo_adjusted[:, :, c] = logo_rgb[:, :, c] * 0.6 + local_mean[c] * 0.4
        logo_adjusted += np.random.randn(ly, lx, 3) * local_std * 0.15
        logo_adjusted = np.clip(logo_adjusted, 0, 255)
        blended = local * (1 - alpha * 0.55) + logo_adjusted * (alpha * 0.55)
        img_np[y_pos:y_pos+ly, x_pos:x_pos+lx] = blended
        return Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))

class AdversarialAntiRemoval:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    def apply(self, img):
        import numpy as np
        import cv2
        result = img.astype(np.float32)
        h, w = img.shape[:2]
        np.random.seed(int(hashlib.sha256(f"{self.secret_key}_adv".encode()).hexdigest(), 16) % (2**32))
        lf_noise = np.random.randn(h//4+1, w//4+1, 3) * 4.0
        lf_noise = cv2.resize(lf_noise, (w, h))
        lf_noise = cv2.GaussianBlur(lf_noise, (21, 21), 7.0)
        result += lf_noise * 0.6
        hf_noise = np.random.randn(h, w, 3) * 1.5
        hf_noise = cv2.GaussianBlur(hf_noise, (3, 3), 0.8)
        result += hf_noise * 0.3
        return np.clip(result, 0, 255).astype(np.uint8)

class AntiRemovalNoisePattern:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    def apply(self, img):
        import numpy as np
        result = img.astype(np.float32)
        h, w = img.shape[:2]
        np.random.seed(int(hashlib.sha256(f"{self.secret_key}_noise".encode()).hexdigest(), 16) % (2**32))
        checker = np.zeros((h, w, 3))
        checker[::2, ::2] = np.random.randn(h//2 + h%2, w//2 + w%2, 3) * 1.5
        result += checker[:h, :w]
        return np.clip(result, 0, 255).astype(np.uint8)

class LogoWatermarkEngine:
    def __init__(self):
        self.visible_overlay = HighlyVisibleLogoOverlay(WATERMARK_LOGO_PATH)
        self.texture_blended = TextureBlendedLogo(WATERMARK_LOGO_PATH)
        self.adversarial = AdversarialAntiRemoval(WATERMARK_SECRET_KEY)
        self.anti_noise = AntiRemovalNoisePattern(WATERMARK_SECRET_KEY)

    def apply_post_generation(self, image_bytes: bytes, output_format: str = "JPEG", enable_anti_upload: bool = True, is_pro_user: bool = False) -> bytes:
        from io import BytesIO
        from PIL import Image
        import numpy as np

        if is_pro_user:
            img = Image.open(BytesIO(image_bytes)).convert("RGB")
            out = BytesIO()
            img.save(out, format="JPEG", quality=95)
            return out.getvalue()
        
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        img = self.visible_overlay.apply(img)
        img = self.texture_blended.apply(img)
        
        img_np = np.array(img)
        img_np = self.anti_noise.apply(img_np)
        img_np = self.adversarial.apply(img_np)
        img = Image.fromarray(img_np)

        out = BytesIO()
        save_fmt = output_format if output_format.upper() in ["JPEG", "JPG", "PNG", "GIF", "WEBP"] else "JPEG"
        
        if enable_anti_upload and save_fmt == "GIF":
            img = img.convert("P", palette=Image.ADAPTIVE, colors=256)
            img.save(out, format="GIF", optimize=True)
            return out.getvalue()

        img.save(out, format=save_fmt, quality=92)
        return out.getvalue()

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

        selected_engine = next((e for e in AI_ENGINES_POOL if e["name"].lower() == target_mode.lower()), None)
        
        fallback_chain = []
        if selected_engine:
            fallback_chain.append(selected_engine) 
        
        fallback_chain.extend([e for e in AI_ENGINES_POOL if e != selected_engine])

        for engine in fallback_chain:
            try:
                if engine["provider"] == "google":
                    api_key = engine.get("apiKey", self.gemini_api_key)
                    client = genai.Client(api_key=api_key)
                    config = types.GenerateContentConfig(system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                    chat = client.chats.create(model=engine["model"], config=config)
                    response = chat.send_message(user_input)
                    return response.text or "" 
                
                else:
                    provider_url = engine.get("url")
                    api_key = engine.get("apiKey")
                    model_name = engine.get("model")
                    
                    if not provider_url or not api_key:
                        continue 

                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    payload = {"model": model_name, "messages": [{"role": "system", "content": self.system_instruction}, {"role": "user", "content": user_input}]}
                    
                    response = requests.post(provider_url, headers=headers, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data["choices"][0]["message"]["content"] 
                    else:
                        continue 

            except Exception as e:
                continue 

        return "[System Error]: All 41 AI engines in the fallback pool are currently unavailable or rate limited."


# ==========================================
# FASTAPI SERVER - RENDER STARTUP OPTIMIZED
# ==========================================

app = FastAPI(title="ZenTech Backend API - AI Routing & Render Optimized")

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
        "message": "Server working perfectly on Render",
        "version": "1.12.332"
    }

GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or NEW_GOOGLE_KEY

class ChatRequest(BaseModel):
    message: str
    mode: str = "Standard"
    output_format: str = "GIF"  
    enable_anti_upload: bool = True  
    is_pro_user: bool = False  
    user_id : str | None = None 

# LAZY LOAD THE ENGINE
global_engine = None

def get_engine():
    global global_engine
    if global_engine is None:
        global_engine = ZenTechBackendEngine(gemini_api_key=GEMINI_KEY)
    return global_engine

@app.post("/chat")
async def chat_endpoint(req: ChatRequest, request: Request):
    try:
        authorization = request.headers.get("Authorization")

        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Authorization token missing"
            )

        active_engine = get_engine()

        if req.mode == "Zimage Generation":
            reply = active_engine.generate_image(
                req.message, 
                output_format=req.output_format,
                enable_anti_upload=req.enable_anti_upload,
                is_pro_user=req.is_pro_user 
            )
        else:
            reply = active_engine.dynamic_route_response(req.message, req.mode)
            
        memory_info = None
        try:
            # LAZY LOAD MEMORY MODULES
            from memory.extraction import extract_memory
            from memory.embedding import generate_embedding
            from memory.storage import save_memory

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
        except Exception as mem_err:
            pass

        return {
            "response": reply,
            "memory": memory_info
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
