#working
# ==========================================
# PURE LOGO AI-PROOF WATERMARK SYSTEM v8.1
# ANTI-WATERMARK REMOVER PROTECTION
# WATERMARK SIZES REDUCED
# PRO USER FEATURE: No watermark for paid users
# ==========================================
# NO TEXT WATERMARK - Only watermark.jpeg logo image
# 
# Strategy:
# 1. LOGO AS SCENE ELEMENT - Describe watermark.jpeg in prompt
#    AI renders logo as natural part of scene (stone carving, neon sign, etc.)
# 2. HIGHLY VISIBLE LOGO OVERLAY - Post-generation logo overlay
#    Large, prominent, multiple positions - AI remover can't remove all
# 3. ADVERSARIAL ANTI-REMOVAL - Perturbations that break AI detection
#    Confuses PhotoTune.ai, Dewatermark.ai detection algorithms
# 4. DCT INVISIBLE FORENSIC - Invisible proof layer
#    Court-level evidence even if visible layers removed
# 5. FREQUENCY DOMAIN ATTACKS - Breaks frequency-based removal
# 6. TEXTURE-MIMICKING NOISE - Logo blends with image texture
# 7. MULTI-SCALE EMBEDDING - Logo at different resolutions
# ==========================================
# NEW: PRO USER SUPPORT
# - If is_pro_user=True: Skip ALL watermark layers
# - If is_pro_user=False/None: Apply full watermark protection
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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def b64_decode(encoded_str: str) -> str:
    try:
        return base64.b64_decode(encoded_str.encode('utf-8')).decode('utf-8')
    except Exception:
        return encoded_str

#================= AI ENGINES =================
AI_ENGINES_POOL= [
    {"name": "NVIDIA Nemotron 70B", "provider": "nvidia", "url": "https://integrate.api.nvidia.com/v1/chat/completions", "model": "nvidia/llama-3.1-nemotron-70b-instruct", "apiKey": "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", "supportsVision": False},
    {"name": "Gemini 1.5 Flash", "provider": "google", "model": "gemini-1.5-flash", "apiKey": b64_decode("QUl6YVN5QVdTbUVoSF9oa3dHNnh6akpVZGVybmgzUjl6Mzl6Mlk4"), "supportsVision": True},
    {"name": "Groq Llama 3.3 70B", "provider": "groq", "url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.3-70b-versatile", "apiKey": "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", "supportsVision": False},
    {"name": "Gemini 1.5 Pro", "provider": "google", "model": "gemini-1.5-pro", "apiKey": b64_decode("QUl6YVN5QVdTbUVoSF9oa3dHNnh6akpVZGVybmgzUjl6Mzl6Mlk4"), "supportsVision": True},
    {"name": "Gemini 3.1 Pro", "provider": "google", "model": "gemini-3.1-pro-preview", "apiKey": b64_decode("QUl6YVN5QVdTbUVoSF9oa3dHNnh6akpVZGVybmgzUjl6Mzl6Mlk4"), "supportsVision": True},
    {"name": "Gemini 3 Flash", "provider": "google", "model": "gemini-3-flash-preview", "apiKey": b64_decode("QUl6YVN5QVdTbUVoSF9oa3dHNnh6akpVZGVybmgzUjl6Mzl6Mlk4"), "supportsVision": True},
    {"name": "Gemini 3.1 Flash-Lite", "provider": "google", "model": "gemini-3.1-flash-lite-preview", "apiKey": b64_decode("QUl6YVN5QVdTbUVoSF9oa3dHNnh6akpVZGVybmgzUjl6Mzl6Mlk4"), "supportsVision": True},
    {"name": "Nano Banana Pro", "provider": "google", "model": "gemini-3-pro-image-preview", "apiKey": b64_decode("QUl6YVN5QVdTbUVoSF9oa3dHNnh6akpVZGVybmgzUjl6Mzl6Mlk4"), "supportsVision": True},
    {"name": "GPT-5.4 Thinking", "provider": "openai", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-5.4-thinking", "apiKey": b64_decode("c2stcHJvai1jeXpuRVNadDlHbzE0ZzdBeXN5Wm42bVowOFR3RjZ3S3VTTDNiZWlUOEd1ZWdUVkt4amFfOE5VUklXMnlIbGhOdHppZEhzYnljLVQzQmxia0ZKZ3ZuN1JUcWVZbmVGUG9iR213MnA1aG1nRkczcnpOZWJuWE9KZVVOQ09aLUdFSHk2cW9ibW5BTVNoSzlqWVM3V2dlZmhFNmlHUUE="), "supportsVision": True},
    {"name": "GPT-5.4 Pro", "provider": "openai", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-5.4-pro", "apiKey": b64_decode("c2stcHJvai1jeXpuRVNadDlHbzE0ZzdBeXN5Wm42bVowOFR3RjZ3S3VTTDNiZWlUOEd1ZWdUVkt4amFfOE5VUklXMnlIbGhOdHppZEhzYnljLVQzQmxia0ZKZ3ZuN1JUcWVZbmVGUG9iR213MnA1aG1nRkczcnpOZWJuWE9KZVVOQ09aLUdFSHk2cW9ibW5BTVNoSzlqWVM3V2dlZmhFNmlHUUE="), "supportsVision": True},
    {"name": "Groq Llama 4 Scout", "provider": "groq", "url": "https://api.groq.com/openai/v1/chat/completions", "model": "meta-llama/llama-4-scout-17b-16e-instruct", "apiKey": "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", "supportsVision": True},
    {"name": "Nano Banana 2 (Flash Image)", "provider": "google", "model": "gemini-3.1-flash-image-preview", "apiKey": b64_decode("QUl6YVN5QVdTbUVoSF9oa3dHNnh6akpVZGVybmgzUjl6Mzl6Mlk4"), "supportsVision": True},
    {"name": "Gemini 2.5 Pro", "provider": "google", "model": "gemini-2.5-pro", "apiKey": b64_decode("QUl6YVN5QVdTbUVoSF9oa3dHNnh6akpVZGVybmgzUjl6Mzl6Mlk4"), "supportsVision": True},
    {"name": "Gemini 2.5 Flash", "provider": "google", "model": "gemini-2.5-flash", "apiKey": b64_decode("QUl6YVN5QVdTbUVoSF9oa3dHNnh6akpVZGVybmgzUjl6Mzl6Mlk4"), "supportsVision": True},
    {"name": "Gemini 1.5 Flash-8B", "provider": "google", "model": "gemini-1.5-flash-8b", "apiKey": b64_decode("QUl6YVN5QVdTbUVoSF9oa3dHNnh6akpVZGVybmgzUjl6Mzl6Mlk4"), "supportsVision": True},
    {"name": "Imagen 4 Ultra", "provider": "google", "model": "imagen-4.0-ultra-generate-001", "apiKey": b64_decode("QUl6YVN5QVdTbUVoSF9oa3dHNnh6akpVZGVybmgzUjl6Mzl6Mlk4"), "supportsVision": False, "isImageModel": True},
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
    """Check if image bytes are AVIF format by magic bytes."""
    if len(image_bytes) < 12:
        return False
    header = image_bytes[:12]
    return b'ftyp' in header and (b'avif' in header or b'avis' in header)

def detect_image_format(image_bytes: bytes) -> str:
    """Detect image format from bytes."""
    if is_avif_image(image_bytes):
        return "AVIF"
    if image_bytes[:2] == b'\xff\xd8':
        return "JPEG"
    if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return "PNG"
    if image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        return "WEBP"
    if image_bytes[:4] == b'GIF8':
        return "GIF"
    return "UNKNOWN"

def convert_avif_to_rgb(image_bytes: bytes) -> Image.Image:
    """Convert AVIF bytes to PIL RGB Image."""
    if not AVIF_AVAILABLE:
        raise RuntimeError("AVIF support not available. Install: pip install pillow-avif-plugin")
    img = Image.open(BytesIO(image_bytes))
    return img.convert("RGB")

def save_as_avif(img: Image.Image, quality: int = 80, speed: int = 6) -> bytes:
    """Save PIL Image as AVIF bytes."""
    if not AVIF_AVAILABLE:
        raise RuntimeError("AVIF support not available. Install: pip install pillow-avif-plugin")
    out = BytesIO()
    img.save(out, format="AVIF", quality=quality, speed=speed)
    return out.getvalue()

def save_as_format(img: Image.Image, fmt: str = "JPEG", quality: int = 92) -> bytes:
    """Save PIL Image to bytes in specified format."""
    out = BytesIO()
    if fmt.upper() == "AVIF":
        if not AVIF_AVAILABLE:
            raise RuntimeError("AVIF support not available")
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
# GIF SUPPORT - Phototune Reject Format
# ==========================================

def save_as_gif(img: Image.Image, duration: int = 100, loop: int = 0) -> bytes:
    """Save PIL Image as GIF bytes. GIF is NOT accepted by Phototune.ai - blocks upload!"""
    out = BytesIO()
    img_gif = img.convert("P", palette=Image.ADAPTIVE, colors=256)
    img_gif.save(out, format="GIF", duration=duration, loop=loop, optimize=True)
    return out.getvalue()

def create_animated_watermark_gif(img: Image.Image, logo_path: str, frames: int = 3) -> bytes:
    """Create animated GIF with watermark. Phototune cannot process animated GIFs!"""
    if not os.path.exists(logo_path):
        return save_as_gif(img)

    images = []
    w, h = img.size

    logo = Image.open(logo_path).convert("RGBA")
    datas = logo.getdata()
    newData = []
    for item in datas:
        if item[0] > 220 and item[1] > 220 and item[2] > 220:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    logo.putdata(newData)

    target_w = max(80, int(w * 0.12))
    ratio = target_w / logo.width
    logo = logo.resize((target_w, int(logo.height * ratio)))

    for i in range(frames):
        frame = img.copy().convert("RGBA")
        offset_x = int(15 + i * 3)
        offset_y = int(h - logo.height - 15 - i * 2)
        alpha_val = int(200 + i * 15)
        logo_data = list(logo.getdata())
        transparent = []
        for r, g, b, a in logo_data:
            transparent.append((r, g, b, min(a, alpha_val)))
        logo_frame = Image.new("RGBA", logo.size)
        logo_frame.putdata(transparent)
        frame.paste(logo_frame, (w - logo.width - offset_x, offset_y), logo_frame)
        frame_p = frame.convert("P", palette=Image.ADAPTIVE, colors=256)
        images.append(frame_p)

    out = BytesIO()
    images[0].save(
        out, 
        format="GIF", 
        save_all=True, 
        append_images=images[1:], 
        duration=300, 
        loop=0,
        optimize=True
    )
    return out.getvalue()


# ==========================================
# PHOTOTUNE ERROR TRIGGER SYSTEM
# ==========================================

class PhototuneErrorTrigger:
    PHOTOTUNE_UPLOAD_URL = "https://phototune.ai/process-watermark"
    PHOTOTUNE_API_ENDPOINT = "https://api.phototune.ai/v1/upload"

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        np.random.seed(int(hashlib.sha256(f"{secret_key}_error_trigger".encode()).hexdigest(), 16) % (2**32))

    def create_error_trigger_file(self, img: Image.Image, fmt: str = "JPEG") -> bytes:
        print("[ERROR-TRIGGER] Creating Phototune error-triggering file...")
        if fmt.upper() == "GIF":
            return self._create_gif_error_trigger(img)
        elif fmt.upper() in ("JPEG", "JPG"):
            return self._create_jpeg_error_trigger(img)
        elif fmt.upper() == "PNG":
            return self._create_png_error_trigger(img)
        else:
            return self._create_generic_error_trigger(img, fmt)

    def _create_gif_error_trigger(self, img: Image.Image) -> bytes:
        out = BytesIO()
        img_gif = img.convert("P", palette=Image.ADAPTIVE, colors=256)
        img_gif.save(out, format="GIF", optimize=True)
        gif_bytes = out.getvalue()
        fake_jpeg_header = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        corrupted = fake_jpeg_header + gif_bytes[6:]
        error_comment = b'\x21\xfe\x25PHOTOTUNE_ERROR_UNSUPPORTED_FORMAT\x00'
        header_end = corrupted.find(b'\x2c')
        if header_end > 0:
            corrupted = corrupted[:header_end] + error_comment + corrupted[header_end:]
        print("[ERROR-TRIGGER] GIF with fake JPEG header created - Phototune will ERROR!")
        return corrupted

    def _create_jpeg_error_trigger(self, img: Image.Image) -> bytes:
        out = BytesIO()
        img.save(out, format="JPEG", quality=92)
        jpeg_bytes = out.getvalue()
        sof_pos = jpeg_bytes.find(b'\xff\xc0')
        if sof_pos > 0:
            corrupted_sof = b'\xff\xc0\x00\x0b\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            jpeg_bytes = jpeg_bytes[:sof_pos] + corrupted_sof + jpeg_bytes[sof_pos+14:]
        fake_eoi = b'\xff\xd9'
        eoi_pos = jpeg_bytes.rfind(b'\xff\xd9')
        if eoi_pos > len(jpeg_bytes) // 2:
            jpeg_bytes = jpeg_bytes[:eoi_pos] + fake_eoi + b'\xff\xfe\x00\x10CORRUPTED' + jpeg_bytes[eoi_pos:]
        invalid_dht = b'\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\xff\xff'
        sos_pos = jpeg_bytes.find(b'\xff\xda')
        if sos_pos > 0:
            jpeg_bytes = jpeg_bytes[:sos_pos] + invalid_dht + jpeg_bytes[sos_pos:]
        print("[ERROR-TRIGGER] Corrupted JPEG created - Phototune will show CORRUPTION ERROR!")
        return jpeg_bytes

    def _create_png_error_trigger(self, img: Image.Image) -> bytes:
        out = BytesIO()
        img.save(out, format="PNG", optimize=True)
        png_bytes = out.getvalue()
        invalid_chunk = struct.pack('>I', 4) + b'tESt' + b'\xde\xad\xbe\xef' + struct.pack('>I', 0x12345678)
        ihdr_pos = png_bytes.find(b'IHDR')
        if ihdr_pos > 4:
            png_bytes = png_bytes[:ihdr_pos-4] + invalid_chunk + png_bytes[ihdr_pos-4:]
        bad_length_chunk = struct.pack('>I', 0xFFFFFFFF) + b'zTeC' + b'A' * 100
        idat_pos = png_bytes.find(b'IDAT')
        if idat_pos > 4:
            png_bytes = png_bytes[:idat_pos-4] + bad_length_chunk + png_bytes[idat_pos-4:]
        print("[ERROR-TRIGGER] Corrupted PNG created - Phototune will show STRUCTURE ERROR!")
        return png_bytes

    def _create_generic_error_trigger(self, img: Image.Image, fmt: str) -> bytes:
        out = BytesIO()
        img.save(out, format=fmt if fmt in ["JPEG", "PNG", "GIF", "WEBP"] else "JPEG")
        raw = out.getvalue()
        error_sig = b'\x00PHOTOTUNE_UPLOAD_ERROR_TRIGGER\x00'
        raw = raw + error_sig
        print(f"[ERROR-TRIGGER] Generic error trigger for {fmt} created")
        return raw

    def create_browser_console_error(self, img_bytes: bytes) -> bytes:
        js_error_trigger = b'<script>console.error("PHOTOTUNE_UPLOAD_BLOCKED_BY_ZENTECH")</script>'
        if b'\xff\xd8' in img_bytes[:2]:
            comment = b'\xff\xfe' + struct.pack('>H', len(js_error_trigger) + 2) + js_error_trigger
            eoi = img_bytes.rfind(b'\xff\xd9')
            if eoi > 0:
                img_bytes = img_bytes[:eoi] + comment + img_bytes[eoi:]
        return img_bytes


# ==========================================
# ANTI-UPLOAD PROTECTION SYSTEM v2.0
# ==========================================

class AntiUploadProtection:
    PHOTOTUNE_DOMAINS = [
        "phototune.ai", "www.phototune.ai", "api.phototune.ai",
        "process-watermark", "phototune.app"
    ]
    BLOCKED_DOMAINS = [
        "phototune.ai", "dewatermark.ai", "watermarkremover.io",
        "apowersoft.com", "media.io", "remove.bg", "cleanup.pictures",
        "snapedit.app", "watermarkremover.net", "fotor.com"
    ]

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.error_trigger = PhototuneErrorTrigger(secret_key)
        np.random.seed(int(hashlib.sha256(f"{secret_key}_anti_upload".encode()).hexdigest(), 16) % (2**32))

    def apply(self, img: Image.Image, image_bytes: bytes, output_format: str = "JPEG") -> bytes:
        print("[ANTI-UPLOAD] Applying Phototune ERROR-TRIGGER protection...")
        error_bytes = self.error_trigger.create_error_trigger_file(img, output_format)
        img = self._poison_exif_metadata_phototune(img)
        img = self._add_forensic_markers(img)
        raw_bytes = self._apply_phototune_structure_corruption(img, output_format)
        protected_bytes = self._append_phototune_payload(raw_bytes, output_format)
        protected_bytes = self.error_trigger.create_browser_console_error(protected_bytes)
        print("[ANTI-UPLOAD] Phototune ERROR trigger applied - Upload will FAIL with error!")
        return protected_bytes

    def _poison_exif_metadata_phototune(self, img: Image.Image) -> Image.Image:
        try:
            img_copy = img.copy()
            exif_dict = {}
            exif_dict[0x010F] = "ZenTech-PHOTOTUNE-BLOCKED"
            exif_dict[0x0110] = "ZT-ANTI-PHOTOTUNE-v8"
            exif_dict[0x0131] = "ZenTech AI - PHOTOTUNE UPLOAD BLOCKED - Copyright Protected"
            exif_dict[0x8298] = "COPYRIGHT ZENTECH 2026 - UNAUTHORIZED WATERMARK REMOVAL PROHIBITED - PHOTOTUNE.AI PROCESSING NOT PERMITTED"
            exif_dict[0x9286] = ("This image is protected by ZenTech AI. "
                               "Phototune.ai and similar watermark removers are NOT AUTHORIZED to process this image. "
                               "Any upload attempt to phototune.ai/process-watermark violates copyright law. "
                               "Forensic tracking enabled. Image ID: " + 
                               hashlib.sha256(self.secret_key.encode()).hexdigest()[:16])
            exif_dict[0xA420] = "ZENTECH_PHOTOTUNE_BLOCK_" + hashlib.sha256(f"{self.secret_key}_{time.time()}".encode()).hexdigest()[:24]
            exif_dict[0xA002] = 99999
            exif_dict[0xA003] = 99999
            img_copy.info['exif'] = self._encode_exif(exif_dict)
            return img_copy
        except Exception as e:
            print(f"[ANTI-UPLOAD WARN] EXIF poisoning failed: {e}")
            return img

    def _encode_exif(self, exif_dict: dict) -> bytes:
        exif_bytes = b'Exif\x00\x00'
        exif_bytes += b'II'
        exif_bytes += struct.pack('<H', 42)
        exif_bytes += struct.pack('<I', 8)
        num_entries = len(exif_dict)
        exif_bytes += struct.pack('<H', num_entries)
        data_offset = 8 + 2 + num_entries * 12 + 4
        extra_data = b''
        for tag, value in sorted(exif_dict.items()):
            if isinstance(value, str):
                encoded = value.encode('utf-8') + b'\x00'
                exif_bytes += struct.pack('<HH', tag, 2)
                exif_bytes += struct.pack('<I', len(encoded))
                if len(encoded) <= 4:
                    exif_bytes += encoded.ljust(4, b'\x00')
                else:
                    exif_bytes += struct.pack('<I', data_offset)
                    extra_data += encoded 
                    data_offset += len(encoded)
            else:
                exif_bytes += struct.pack('<HH', tag, 4)
                exif_bytes += struct.pack('<I', 1)
                exif_bytes += struct.pack('<I', value)
        exif_bytes += struct.pack('<I', 0)
        exif_bytes += extra_data
        return exif_bytes

    def _add_forensic_markers(self, img: Image.Image) -> Image.Image:
        img_np = np.array(img).astype(np.float32)
        h, w = img_np.shape[:2]
        np.random.seed(int(hashlib.sha256(f"{self.secret_key}_fingerprint".encode()).hexdigest(), 16) % (2**32))
        fingerprint = np.random.randint(0, 2, (h, w, 3)) * 1.0
        img_np = np.floor(img_np / 2) * 2 + fingerprint
        for c in range(3):
            shift = (c - 1) * 0.3
            noise = np.random.randn(h, w) * 0.5
            img_np[:, :, c] += noise + shift
        return Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))

    def _apply_phototune_structure_corruption(self, img: Image.Image, fmt: str) -> bytes:
        out = BytesIO()
        if fmt.upper() in ("JPEG", "JPG"):
            img.save(out, format="JPEG", quality=92, optimize=True, progressive=True)
            raw = out.getvalue()
            app1_marker = b'\xff\xe1'
            malformed_data = b'PHOTOTUNE_BLOCK\x00\x01\x02\x03\xff\xfe\xfd'
            soi_pos = raw.find(b'\xff\xd8')
            if soi_pos >= 0:
                raw = raw[:soi_pos+2] + app1_marker + struct.pack('>H', len(malformed_data) + 2) + malformed_data + raw[soi_pos+2:]
            corrupt_marker = b'\xff\xdb'
            corrupt_data = b'\x00\x43\x00' + b'\xff' * 59
            dqt_pos = raw.find(b'\xff\xdb')
            if dqt_pos > 0:
                raw = raw[:dqt_pos] + corrupt_marker + struct.pack('>H', len(corrupt_data) + 2) + corrupt_data + raw[dqt_pos:]
            return raw
        elif fmt.upper() == "PNG":
            img.save(out, format="PNG", optimize=True)
            raw = out.getvalue()
            chunk_type = b'pHtN'
            chunk_data = b"PHOTOTUNE_UPLOAD_BLOCKED_BY_ZENTECH\x00"
            chunk_len = struct.pack('>I', len(chunk_data))
            chunk_crc = struct.pack('>I', 0xDEADBEEF)
            ihdr_pos = raw.find(b'IHDR')
            if ihdr_pos > 4:
                insert_pos = ihdr_pos + 21
                custom_chunk = chunk_len + chunk_type + chunk_data + chunk_crc
                raw = raw[:insert_pos] + custom_chunk + raw[insert_pos:]
            return raw
        elif fmt.upper() == "GIF":
            img.save(out, format="GIF", optimize=True)
            raw = out.getvalue()
            gif_comment = b'\x21\xfe\x1cZenTech-Phototune-Block-v8\x00'
            header_end = raw.find(b'\x2c')
            if header_end > 0:
                raw = raw[:header_end] + gif_comment + raw[header_end:]
            return raw
        elif fmt.upper() == "AVIF":
            if not AVIF_AVAILABLE:
                raise RuntimeError("AVIF support not available")
            img.save(out, format="AVIF", quality=80, speed=6)
            return out.getvalue()
        else:
            img.save(out, format="JPEG", quality=92)
            return out.getvalue()

    def _append_phototune_payload(self, raw_bytes: bytes, fmt: str) -> bytes:
        payload = {
            "ztech_protected": True,
            "version": "8.2",
            "timestamp": int(time.time()),
            "protection_level": "phototune_maximum",
            "anti_phototune": True,
            "phototune_block": True,
            "target_domain": "phototune.ai",
            "target_endpoint": "/process-watermark",
            "forensic_enabled": True,
            "format": fmt,
            "signature": hashlib.sha256(f"{self.secret_key}_{time.time()}".encode()).hexdigest()[:32]
        }
        payload_json = json.dumps(payload).encode('utf-8')
        if fmt.upper() in ("JPEG", "JPG"):
            eoi = raw_bytes.rfind(b'\xff\xd9')
            if eoi > 0:
                custom_marker = b'\xff\xfe'
                marker_data = b"PHOTOTUNE_BLOCK_ZENTECH_" + base64.b64encode(payload_json)
                marker_len = struct.pack('>H', len(marker_data) + 2)
                raw_bytes = raw_bytes[:eoi] + custom_marker + marker_len + marker_data + raw_bytes[eoi:]
        elif fmt.upper() == "PNG":
            chunk_type = b'pHtB'
            chunk_data = base64.b64encode(payload_json)
            chunk_len = struct.pack('>I', len(chunk_data))
            chunk_crc = struct.pack('>I', 0)
            raw_bytes = raw_bytes + chunk_len + chunk_type + chunk_data + chunk_crc
        elif fmt.upper() == "GIF":
            trailer = raw_bytes.rfind(b'\x3b')
            if trailer > 0:
                block_ext = b'\x21\xfe\x20'
                block_data = b"PHOTOTUNE_AI_UPLOAD_BLOCKED_BY_ZENTECH"
                raw_bytes = raw_bytes[:trailer] + block_ext + bytes([len(block_data)]) + block_data + b'\x00' + raw_bytes[trailer:]
        return raw_bytes

    def verify_protection(self, image_bytes: bytes) -> dict:
        result = {
            "protected": False,
            "phototune_block": False,
            "format": detect_image_format(image_bytes),
            "markers_found": [],
            "metadata": {}
        }
        if b'PHOTOTUNE_BLOCK' in image_bytes:
            result["markers_found"].append("phototune_block_marker")
            result["protected"] = True
            result["phototune_block"] = True
        if b'ZenTech-PHOTOTUNE-BLOCKED' in image_bytes:
            result["markers_found"].append("ztech_phototune_exif")
            result["protected"] = True
            result["phototune_block"] = True
        if b'ZENTECH_PHOTOTUNE_BLOCK' in image_bytes:
            result["markers_found"].append("ztech_phototune_id")
            result["protected"] = True
            result["phototune_block"] = True
        return result


# ==========================================
# STRATEGY 2: SINGLE HIGHLY VISIBLE LOGO OVERLAY
# ==========================================

class HighlyVisibleLogoOverlay:
    def __init__(self, logo_path: str):
        self.logo_path = logo_path

    def _remove_white_bg(self, logo: Image.Image) -> Image.Image:
        datas = logo.getdata()
        newData = []
        for item in datas:
            if item[0] > 210 and item[1] > 210 and item[2] > 210:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        logo.putdata(newData)
        return logo

    def apply(self, img: Image.Image) -> Image.Image:
        if not os.path.exists(self.logo_path):
            print(f"[WARN] Logo not found at {self.logo_path}")
            return img
        img = img.convert("RGBA")
        logo = Image.open(self.logo_path).convert("RGBA")
        logo = self._remove_white_bg(logo)
        w, h = img.size
        target_w = max(60, int(w * 0.08))
        ratio = target_w / logo.width
        logo_resized = logo.resize((target_w, int(logo.height * ratio)))
        logo_data = list(logo_resized.getdata())
        transparent = []
        for r, g, b, a in logo_data:
            transparent.append((r, g, b, int(a * 0.75)))
        logo_resized.putdata(transparent)
        layer = Image.new("RGBA", img.size, (0,0,0,0))
        pos = (w - logo_resized.width - 15, h - logo_resized.height - 15)
        layer.paste(logo_resized, pos, logo_resized)
        img = Image.alpha_composite(img, layer)
        print(f"[VISIBLE] Single logo (BR): {target_w}px, opacity=75%")
        return img.convert("RGB")


# ==========================================
# STRATEGY 3: ADVERSARIAL ANTI-REMOVAL v2.0
# ==========================================

class AdversarialAntiRemoval:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def apply(self, img: np.ndarray) -> np.ndarray:
        result = img.astype(np.float32)
        h, w = img.shape[:2]
        np.random.seed(int(hashlib.sha256(f"{self.secret_key}_adv".encode()).hexdigest(), 16) % (2**32))
        lf_noise = np.random.randn(h//4+1, w//4+1, 3) * 4.0
        lf_noise = cv2.resize(lf_noise, (w, h))
        lf_noise = cv2.GaussianBlur(lf_noise, (21, 21), 7.0)
        result += lf_noise * 0.6
        mf_noise = np.random.randn(h//2+1, w//2+1, 3) * 2.5
        mf_noise = cv2.resize(mf_noise, (w, h))
        mf_noise = cv2.GaussianBlur(mf_noise, (9, 9), 3.0)
        result += mf_noise * 0.4
        hf_noise = np.random.randn(h, w, 3) * 1.5
        hf_noise = cv2.GaussianBlur(hf_noise, (3, 3), 0.8)
        result += hf_noise * 0.3
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY).astype(np.float32)
        edges = cv2.Canny(gray.astype(np.uint8), 20, 80)
        edge_pattern = edges.astype(np.float32) * 0.8
        for c in range(3):
            result[:, :, c] += edge_pattern * np.random.randn() * 0.4
        grid_size = 32
        for i in range(0, h, grid_size):
            for j in range(0, w, grid_size):
                if np.random.random() > 0.7:
                    patch = result[i:min(i+grid_size, h), j:min(j+grid_size, w)]
                    noise = np.random.randn(*patch.shape) * 2.0
                    result[i:min(i+grid_size, h), j:min(j+grid_size, w)] += noise
        uap = self._generate_uap(h, w)
        result += uap * 0.5
        result = self._add_fourier_perturbations(result)
        return np.clip(result, 0, 255).astype(np.uint8)

    def _generate_uap(self, h: int, w: int) -> np.ndarray:
        x = np.linspace(-1, 1, w)
        y = np.linspace(-1, 1, h)
        X, Y = np.meshgrid(x, y)
        uap = np.zeros((h, w, 3))
        for c in range(3):
            freq = 2 + c * 3
            phase = np.random.uniform(0, 2*np.pi)
            uap[:, :, c] = np.sin(freq * np.pi * X + phase) * np.cos(freq * np.pi * Y + phase)
        uap = cv2.GaussianBlur(uap, (5, 5), 1.5)
        return uap * 3.0

    def _add_fourier_perturbations(self, img: np.ndarray) -> np.ndarray:
        result = img.copy()
        for c in range(3):
            f = np.fft.fft2(img[:, :, c])
            fshift = np.fft.fftshift(f)
            h, w = fshift.shape
            crow, ccol = h//2, w//2
            mask = np.zeros((h, w))
            r = min(h, w) // 8
            cv2.circle(mask, (ccol, crow), r, 1, -1)
            cv2.circle(mask, (ccol, crow), r//2, 0, -1)
            noise = np.random.randn(h, w) * 2.0
            fshift += noise * mask
            f_ishift = np.fft.ifftshift(fshift)
            img_back = np.fft.ifft2(f_ishift)
            result[:, :, c] = np.abs(img_back)
        return result


# ==========================================
# STRATEGY 4: DCT INVISIBLE FORENSIC WATERMARK v2.0
# ==========================================

class DCTForensicWatermark:
    def __init__(self, secret_key: str, strength: float = 0.25):
        self.secret_key = secret_key
        self.strength = strength
        np.random.seed(int(hashlib.sha256(secret_key.encode()).hexdigest(), 16) % (2**32))
        self.prn = [np.random.randn(8, 8) for _ in range(256)]

    def _text_to_bits(self, text):
        binary = ''.join(format(ord(c), '08b') for c in text)
        return [int(b) for b in binary[:256]]

    def embed(self, image: np.ndarray, text: str = "ZENTECH") -> np.ndarray:
        ycrcb = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
        y = ycrcb[:, :, 0].astype(np.float32)
        h, w = y.shape
        pad_h, pad_w = (8 - h % 8) % 8, (8 - w % 8) % 8
        y = np.pad(y, ((0, pad_h), (0, pad_w)), mode='edge')
        binary = ''.join(format(ord(c), '08b') for c in text)
        bits = [int(b) for b in binary[:256]]
        bits = (bits + [0]*256)[:256]
        np.random.seed(int(hashlib.sha256(self.secret_key.encode()).hexdigest(), 16) % (2**32))
        positions = []
        for i in range(256):
            x = (i * 137 + np.random.randint(0, y.shape[0]//8 - 1)) % (y.shape[0]//8 - 1)
            yy = (i * 239 + np.random.randint(0, y.shape[1]//8 - 1)) % (y.shape[1]//8 - 1)
            positions.append((x, yy))
        for idx, bit in enumerate(bits):
            bx, by = positions[idx]
            block = y[bx*8:(bx+1)*8, by*8:(by+1)*8]
            dct = cv2.dct(block)
            freq_positions = [(2,3), (3,2), (3,3), (2,4), (4,2), (3,4), (4,3)]
            for pos in freq_positions:
                if bit == 1:
                    dct[pos] += self.strength * self.prn[idx][pos] * abs(dct[pos])
                else:
                    dct[pos] -= self.strength * self.prn[idx][pos] * abs(dct[pos])
            y[bx*8:(bx+1)*8, by*8:(by+1)*8] = cv2.idct(dct)
        ycrcb[:, :, 0] = np.clip(y[:h, :w], 0, 255).astype(np.uint8)
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)


# ==========================================
# STRATEGY 5: TEXTURE-BLENDED LOGO OVERLAY v2.0
# ==========================================

class TextureBlendedLogo:
    def __init__(self, logo_path: str):
        self.logo_path = logo_path

    def apply(self, img: Image.Image) -> Image.Image:
        if not os.path.exists(self.logo_path):
            return img
        img_np = np.array(img).astype(np.float32)
        h, w = img_np.shape[:2]
        logo = Image.open(self.logo_path).convert("RGBA")
        datas = logo.getdata()
        newData = []
        for item in datas:
            if item[0] > 220 and item[1] > 220 and item[2] > 220:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        logo.putdata(newData)
        target_w = max(80, int(w * 0.10))
        ratio = target_w / logo.width
        logo = logo.resize((target_w, int(logo.height * ratio)))
        logo_np = np.array(logo).astype(np.float32)
        lx, ly = logo_np.shape[1], logo_np.shape[0]
        x_pos = w - lx - 20
        y_pos = h - ly - 20
        if x_pos < 0 or y_pos < 0:
            return img
        local = img_np[y_pos:y_pos+ly, x_pos:x_pos+lx]
        local_mean = np.mean(local, axis=(0,1))
        local_std = np.std(local, axis=(0,1))
        alpha = logo_np[:, :, 3:4] / 255.0
        logo_rgb = logo_np[:, :, :3]
        logo_adjusted = logo_rgb.copy()
        for c in range(3):
            logo_adjusted[:, :, c] = logo_rgb[:, :, c] * 0.6 + local_mean[c] * 0.4
        noise = np.random.randn(ly, lx, 3) * local_std * 0.15
        logo_adjusted += noise
        logo_adjusted = np.clip(logo_adjusted, 0, 255)
        blended = local * (1 - alpha * 0.55) + logo_adjusted * (alpha * 0.55)
        img_np[y_pos:y_pos+ly, x_pos:x_pos+lx] = blended
        return Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))


# ==========================================
# STRATEGY 6: MULTI-SCALE LOGO EMBEDDING
# ==========================================

class MultiScaleLogoEmbedding:
    def __init__(self, logo_path: str):
        self.logo_path = logo_path

    def apply(self, img: Image.Image) -> Image.Image:
        if not os.path.exists(self.logo_path):
            return img
        img = img.convert("RGBA")
        logo = Image.open(self.logo_path).convert("RGBA")
        datas = logo.getdata()
        newData = []
        for item in datas:
            if item[0] > 220 and item[1] > 220 and item[2] > 220:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        logo.putdata(newData)
        w, h = img.size
        scales = [
            (0.15, 0.75),
            (0.08, 0.50),
            (0.04, 0.30),
            (0.025, 0.20),
        ]
        positions = [
            (w - int(w*0.15) - 15, h - int(h*0.15) - 15),
            (15, 15),
            (w//2 - int(w*0.08)//2, 15),
            (15, h - int(h*0.04) - 15),
        ]
        for i, (scale, opacity) in enumerate(scales):
            target_w = max(30, int(w * scale))
            ratio = target_w / logo.width
            logo_resized = logo.resize((target_w, int(logo.height * ratio)))
            logo_data = list(logo_resized.getdata())
            transparent = []
            for r, g, b, a in logo_data:
                transparent.append((r, g, b, int(a * opacity)))
            logo_resized.putdata(transparent)
            layer = Image.new("RGBA", img.size, (0,0,0,0))
            if i < len(positions):
                layer.paste(logo_resized, positions[i], logo_resized)
            img = Image.alpha_composite(img, layer)
        return img.convert("RGB")


# ==========================================
# STRATEGY 7: ANTI-REMOVAL NOISE PATTERN
# ==========================================

class AntiRemovalNoisePattern:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def apply(self, img: np.ndarray) -> np.ndarray:
        result = img.astype(np.float32)
        h, w = img.shape[:2]
        np.random.seed(int(hashlib.sha256(f"{self.secret_key}_noise".encode()).hexdigest(), 16) % (2**32))
        checker = np.zeros((h, w, 3))
        checker[::2, ::2] = np.random.randn(h//2 + h%2, w//2 + w%2, 3) * 1.5
        checker[1::2, 1::2] = np.random.randn(h//2, w//2, 3) * 1.5
        result += checker[:h, :w]
        noise = self._perlin_noise(h, w)
        result += noise[:, :, np.newaxis] * 2.0
        for i in range(0, h, 4):
            if i < h:
                result[i:i+2, :, :] += np.random.randn(1, 1, 3) * 1.0
        return np.clip(result, 0, 255).astype(np.uint8)

    def _perlin_noise(self, h: int, w: int) -> np.ndarray:
        noise = np.zeros((h, w))
        scale = 16
        for i in range(0, h, scale):
            for j in range(0, w, scale):
                val = np.random.randn()
                noise[i:min(i+scale, h), j:min(j+scale, w)] = val
        noise = cv2.GaussianBlur(noise, (scale+1, scale+1), scale/2)
        return noise


# ==========================================
# STRATEGY 8: EDGE-CONFUSING OVERLAY
# ==========================================

class EdgeConfusingOverlay:
    def __init__(self, logo_path: str):
        self.logo_path = logo_path

    def apply(self, img: Image.Image) -> Image.Image:
        if not os.path.exists(self.logo_path):
            return img
        img_np = np.array(img).astype(np.float32)
        h, w = img_np.shape[:2]
        logo = Image.open(self.logo_path).convert("RGBA")
        datas = logo.getdata()
        newData = []
        for item in datas:
            if item[0] > 220 and item[1] > 220 and item[2] > 220:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        logo.putdata(newData)
        target_w = max(90, int(w * 0.13))
        ratio = target_w / logo.width
        logo = logo.resize((target_w, int(logo.height * ratio)))
        logo_np = np.array(logo).astype(np.float32)
        lx, ly = logo_np.shape[1], logo_np.shape[0]
        x_pos = w - lx - 15
        y_pos = h - ly - 15
        if x_pos < 0 or y_pos < 0:
            return img
        local = img_np[y_pos:y_pos+ly, x_pos:x_pos+lx]
        local_gray = cv2.cvtColor(local.astype(np.uint8), cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(local_gray, 50, 150)
        kernel = np.ones((5,5), np.uint8)
        edges_dilated = cv2.dilate(edges, kernel, iterations=1)
        edge_mask = edges_dilated.astype(np.float32) / 255.0
        edge_mask = cv2.GaussianBlur(edge_mask, (7, 7), 2.0)
        alpha = logo_np[:, :, 3:4] / 255.0
        logo_rgb = logo_np[:, :, :3]
        adjusted_alpha = alpha * (0.4 + 0.6 * (1 - edge_mask[:, :, np.newaxis]))
        local_mean = np.mean(local, axis=(0,1))
        logo_adjusted = logo_rgb * 0.7 + local_mean * 0.3
        blended = local * (1 - adjusted_alpha * 0.60) + logo_adjusted * (adjusted_alpha * 0.60)
        img_np[y_pos:y_pos+ly, x_pos:x_pos+lx] = blended
        return Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))


# ==========================================
# UNIFIED LOGO WATERMARK ENGINE v8.1
# ==========================================

class LogoWatermarkEngine:
    """
    Pure logo-based AI-proof watermark system.
    NO TEXT - Only watermark.jpeg logo image.
    Enhanced anti-removal protection with REDUCED watermark sizes.
    Includes ANTI-UPLOAD PROTECTION to block watermark remover tools.

    NEW: PRO USER SUPPORT
    - If is_pro_user=True: Skip ALL watermark layers, return clean image
    - If is_pro_user=False/None: Apply full watermark protection
    """

    def __init__(self):
        self.visible_overlay = HighlyVisibleLogoOverlay(WATERMARK_LOGO_PATH)
        self.texture_blended = TextureBlendedLogo(WATERMARK_LOGO_PATH)
        self.adversarial = AdversarialAntiRemoval(WATERMARK_SECRET_KEY)
        self.dct_wm = DCTForensicWatermark(WATERMARK_SECRET_KEY)
        self.multi_scale = MultiScaleLogoEmbedding(WATERMARK_LOGO_PATH)
        self.anti_noise = AntiRemovalNoisePattern(WATERMARK_SECRET_KEY)
        self.edge_confusing = EdgeConfusingOverlay(WATERMARK_LOGO_PATH)
        self.anti_upload = AntiUploadProtection(WATERMARK_SECRET_KEY)

    def get_generation_prompt(self, user_prompt: str) -> str:
        """Return user prompt as-is without logo scene injection."""
        return user_prompt

    def apply_post_generation(self, image_bytes: bytes, output_format: str = "JPEG", enable_anti_upload: bool = True, is_pro_user: bool = False) -> bytes:
        """
        Apply all post-generation watermark layers.

        NEW PARAM: is_pro_user
        - True: Skip ALL watermark layers, return clean image
        - False/None: Apply full watermark protection (default for free users)
        """
        # ============================================================
        # PRO USER: SKIP ALL WATERMARKS - RETURN CLEAN IMAGE
        # ============================================================
        if is_pro_user:
            print("[PRO USER] Watermark bypass enabled - Returning clean image without watermark")
            detected_fmt = detect_image_format(image_bytes)
            print(f"[PRO USER] Input format detected: {detected_fmt}")

            if detected_fmt == "AVIF" and AVIF_AVAILABLE:
                img = convert_avif_to_rgb(image_bytes)
            else:
                img = Image.open(BytesIO(image_bytes)).convert("RGB")

            # For PRO users, save as JPEG (best quality, no GIF blocking needed)
            print("[PRO USER] Saving as high-quality JPEG...")
            return save_as_format(img, fmt="JPEG", quality=95)

        # ============================================================
        # FREE USER: APPLY FULL WATERMARK PROTECTION
        # ============================================================
        detected_fmt = detect_image_format(image_bytes)
        print(f"[WM] Input format detected: {detected_fmt}")

        if detected_fmt == "AVIF" and AVIF_AVAILABLE:
            img = convert_avif_to_rgb(image_bytes)
        else:
            img = Image.open(BytesIO(image_bytes)).convert("RGB")

        # Layer 1: Multi-scale logo embedding (primary visible)
        print("[WM] Applying multi-scale logo embedding...")
        img = self.multi_scale.apply(img)

        # Layer 2: Texture-blended logo overlay (blends with scene)
        print("[WM] Applying texture-blended logo...")
        img = self.texture_blended.apply(img)

        # Layer 3: Edge-confusing overlay (hides from edge detection)
        print("[WM] Applying edge-confusing overlay...")
        img = self.edge_confusing.apply(img)

        # Layer 4: Highly visible logo overlay (backup)
        print("[WM] Applying highly visible overlay...")
        img = self.visible_overlay.apply(img)

        # Layer 5: Anti-removal noise patterns
        print("[WM] Applying anti-removal noise...")
        img_np = np.array(img)
        img_np = self.anti_noise.apply(img_np)

        # Layer 6: Adversarial anti-removal perturbations
        print("[WM] Applying adversarial perturbations...")
        img_np = self.adversarial.apply(img_np)

        # Layer 7: DCT invisible forensic watermark
        print("[WM] Applying DCT forensic watermark...")
        img_np = self.dct_wm.embed(img_np)

        img = Image.fromarray(img_np)

        # ============================================================
        # PHOTOTUNE BLOCKING: Output as GIF (Phototune REJECTS GIF!)
        # ============================================================
        if enable_anti_upload and output_format.upper() == "GIF":
            print("[PHOTOTUNE-BLOCK] ======================================")
            print("[PHOTOTUNE-BLOCK] Output: ANIMATED GIF")
            print("[PHOTOTUNE-BLOCK] Phototune accepts: JPG, JPEG, PNG, WEBP, AVIF")
            print("[PHOTOTUNE-BLOCK] Phototune REJECTS: GIF")
            print("[PHOTOTUNE-BLOCK] Upload to phototune.ai -> ERROR: Unsupported format")
            print("[PHOTOTUNE-BLOCK] ======================================")
            return self._create_phototune_blocking_gif(img)

        # Standard output for other formats
        print(f"[WM] Saving as {output_format}...")
        return save_as_format(img, fmt=output_format, quality=92)

    def _create_phototune_blocking_gif(self, img: Image.Image) -> bytes:
        """Create animated GIF that Phototune CANNOT process."""
        print("[GIF] Creating Phototune-blocking animated GIF...")
        frames = []
        w, h = img.size
        logo = Image.open(WATERMARK_LOGO_PATH).convert("RGBA")
        datas = logo.getdata()
        newData = []
        for item in datas:
            if item[0] > 210 and item[1] > 210 and item[2] > 210:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        logo.putdata(newData)
        target_w = max(100, int(w * 0.25))
        ratio = target_w / logo.width
        logo = logo.resize((target_w, int(logo.height * ratio)))
        positions = [
            (w - logo.width - 20, h - logo.height - 20),
            (20, 20),
            (w - logo.width - 20, 20),
            (20, h - logo.height - 20),
            ((w - logo.width)//2, (h - logo.height)//2),
        ]
        for i, (px, py) in enumerate(positions):
            frame = img.copy().convert("RGBA")
            opacity = 0.7 + (i * 0.05)
            logo_data = list(logo.getdata())
            transparent = []
            for r, g, b, a in logo_data:
                transparent.append((r, g, b, int(a * opacity)))
            logo_frame = Image.new("RGBA", logo.size)
            logo_frame.putdata(transparent)
            frame.paste(logo_frame, (px, py), logo_frame)
            frame_p = frame.convert("P", palette=Image.ADAPTIVE, colors=256)
            frames.append(frame_p)
        out = BytesIO()
        frames[0].save(
            out,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=500,
            loop=0,
            optimize=True,
            transparency=0,
            disposal=2
        )
        gif_bytes = out.getvalue()
        print(f"[GIF] Animated GIF created: {len(gif_bytes)} bytes")
        print("[GIF] File extension: .gif")
        print("[GIF] Phototune will show: 'Unsupported format. Please upload JPG, PNG, WEBP or AVIF'")
        return gif_bytes


# ==========================================
# CORE ENGINE
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
        try:
            self.baseline_client = genai.Client(api_key=self.gemini_api_key)
            config = types.GenerateContentConfig(system_instruction=self.system_instruction, safety_settings=self.safety_settings)
            self.baseline_chat = self.baseline_client.chats.create(model="gemini-2.5-flash", config=config)
            print("[SYSTEM] Baseline Gemini 2.5 Engine running perfectly.")
        except Exception as e:
            print(f"[ERROR] Baseline startup exception: {e}")

    def generate_image(self, prompt: str, output_format: str = "GIF", enable_anti_upload: bool = True, is_pro_user: bool = False) -> str:
        """
        Generate image with optional watermark protection.

        NEW PARAM: is_pro_user
        - True: Clean image without watermark (PRO user)
        - False/None: Full watermark protection (Free user)
        """
        safe_prompt = f"{prompt}, no human faces, no human figures, highly detailed, 4k"
        encoded_prompt = urllib.parse.quote(safe_prompt)
        seed = int(time.time())
        print(f"[ZIMAGE] User prompt: {prompt}")
        print(f"[ZIMAGE] PRO User: {is_pro_user}")

        POLLINATIONS_API_KEY = "sk_G8nhKDsZ44Hu3GqsEwJvD2u8HdytEAL0"
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&seed={seed}&nologo=true&key={POLLINATIONS_API_KEY}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}

        try:
            print(f"[ZIMAGE] Requesting image with user prompt...")
            response = requests.get(url, headers=headers, timeout=45)

            if response.status_code == 200:
                try:
                    print("[ZIMAGE] Applying logo watermark layers...")
                    watermarked_bytes = self.watermark_engine.apply_post_generation(
                        response.content, 
                        output_format=output_format,
                        enable_anti_upload=enable_anti_upload,
                        is_pro_user=is_pro_user  # NEW: Pass PRO user flag
                    )
                    img_base64 = base64.b64encode(watermarked_bytes).decode("utf-8")
                    print("[ZIMAGE] Image processing complete!")
                except Exception as e:
                    print(f"[ZIMAGE WARN] Post-gen failed: {e}")
                    img_base64 = base64.b64encode(response.content).decode("utf-8")

                # Set MIME type based on output format (PRO users get JPEG)
                if is_pro_user:
                    mime = "image/jpeg"
                    print("[ZIMAGE] PRO user - Serving high-quality JPEG")
                else:
                    mime_map = {
                        "AVIF": "image/avif",
                        "GIF": "image/gif",
                        "PNG": "image/png",
                        "WEBP": "image/webp",
                        "JPEG": "image/jpeg",
                        "JPG": "image/jpeg"
                    }
                    mime = mime_map.get(output_format.upper(), "image/gif")

                # Add Phototune blocking notice in response (only for free users)
                block_notice = ""
                if not is_pro_user and enable_anti_upload and output_format.upper() == "GIF":
                    block_notice = "\n\n> **Phototune Protection:** This image is saved as `.gif` format. Phototune.ai does NOT support GIF and will show **'Unsupported format'** error on upload."

                return f"![Zimage Generated](data:{mime};base64,{img_base64}){block_notice}"
            else:
                return f"**[IMAGE ERROR]** Pollinations API blocked (HTTP {response.status_code}). Details: {response.text}"
        except Exception as e:
            return f"**[IMAGE ERROR]** Connection failed. Details: {str(e)}"

    def dynamic_route_response(self, user_input: str, target_mode: str) -> str:
        if not user_input.strip(): 
            return "Please enter a question or prompt."
        selected_engine = next((e for e in AI_ENGINES_POOL if e["name"].lower() == target_mode.lower()), None)
        if not selected_engine or selected_engine["provider"] == "google":
            model_to_use = selected_engine["model"] if selected_engine else "gemini-2.5-flash"
            try:
                client = genai.Client(api_key=selected_engine["apiKey"] if selected_engine else self.gemini_api_key)
                config = types.GenerateContentConfig(system_instruction=self.system_instruction, safety_settings=self.safety_settings)
                chat = client.chats.create(model=model_to_use, config=config)
                response = chat.send_message(user_input)
                return response.text or ""
            except Exception as e:
                try:
                    res = self.baseline_chat.send_message(user_input)
                    return res.text or ""
                except Exception as ex:
                    return f"[API Error]: Engine fallback failure. Details: {ex}"

        provider_url = selected_engine.get("url")
        api_key = selected_engine.get("apiKey")
        model_name = selected_engine.get("model")
        if not provider_url or not api_key:
            return f"[Config Error]: Engine '{target_mode}' missing parameters."

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": model_name, "messages": [{"role": "system", "content": self.system_instruction}, {"role": "user", "content": user_input}]}
        try:
            response = requests.post(provider_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[Provider Error]: {selected_engine['name']} HTTP {response.status_code} - {response.text}"
        except Exception as e:
            return f"[Connection Error]: Failed to query {selected_engine['name']}. Details: {str(e)}"


# ==========================================
# FASTAPI SERVER
# ==========================================

app = FastAPI(title="ZenTech Backend API - Anti-Remover Watermark v8.2 (PRO User Support)")

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
        "message": "Server are working as expected no issue \n - Zen-Tech Operation team",
      
        "version": "1.12.332"
    }

GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or AI_ENGINES_POOL[1]["apiKey"]
engine = ZenTechBackendEngine(gemini_api_key=GEMINI_KEY)

class ChatRequest(BaseModel):
    message: str
    mode: str = "Standard"
    output_format: str = "GIF"  # GIF = Phototune blocked! Also: JPEG, PNG, AVIF, WEBP
    enable_anti_upload: bool = True  # Enable anti-upload protection
    is_pro_user: bool = False  # NEW: PRO user flag - True = no watermark, False = watermark
    user_id : str | None = None 
@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        if req.mode == "Zimage Generation":
            reply = engine.generate_image(
                req.message, 
                output_format=req.output_format,
                enable_anti_upload=req.enable_anti_upload,
                is_pro_user=req.is_pro_user  # NEW: Pass PRO user flag
               
            )
        else:
            reply = engine.dynamic_route_response(req.message, req.mode)
  # ==============================
    # MEMORY SYSTEM
    # ==============================
    memory_info = None
    memory = extract_memory(req.message)

    if memory:
        embedding = generate_embedding(
            memory["memory_text"]
        )

        print("MEMORY EXTRACTED:", memory)
        print("EMBEDDING GENERATED:", len(embedding))

        save_memory(
    user_id=req.user_id,
    memory_text=memory["memory_text"],
    memory_type=memory.get("memory_type", "text"),
    embedding=embedding
)
        memory_info = {
    "memory_text": memory["memory_text"],
    "saved": True
}

 print("MEMORY SAVED TO SUPABASE")
    # ==============================
    # RETURN RESPONSE
    # ==============================

   return {
    "response": reply,
    "memory": {
        "saved": True,
        "memory_text": memory["memory_text"]
    }
}
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=str(e)
    )
 
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860) 
