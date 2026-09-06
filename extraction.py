def extract_memory(text: str):
    """
    Extract useful memory from the user's message.
    """

    if not text:
        return None

    text = text.strip()

    if len(text) < 3:
        return None

    return {
        "memory_text": text,
        "memory_type": "text"
    }
