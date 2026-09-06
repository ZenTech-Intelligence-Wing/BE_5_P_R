import os
import requests

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def save_memory(
    user_id,
    memory_text,
    embedding,
    memory_type="text",
    access_token=None
):

    url = f"{SUPABASE_URL}/rest/v1/memories"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": access_token or f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    data = {
        "user_id": user_id,
        "memory_text": memory_text,
        "memory_type": memory_type,
        "embedding": embedding
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    print("SUPABASE INSERT STATUS:", response.status_code)
    print("SUPABASE INSERT RESPONSE:", response.text)

    if not response.ok:
        raise Exception(
            f"Memory save failed: {response.status_code} {response.text}"
        )

    return response.json()
