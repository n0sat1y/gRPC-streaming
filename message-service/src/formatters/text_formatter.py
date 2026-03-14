def slim_text_formatter(text: str):
    return text if len(text) <= 50 else text[:47] + "..."
