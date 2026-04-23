import re

def anonymize_text(text):
    if not text:
        return ""
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL]', text)
    text = re.sub(r'\+?\d[\d\-\(\) ]{9,14}\d', '[PHONE]', text)
    text = re.sub(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', '[CARD]', text)
    text = re.sub(r'\d+[\s]*(руб|usd|eur|долла|евро|\$|€)', '[MONEY]', text, flags=re.IGNORECASE)
    return text

def anonymize_dialogue(dialogue_list):
    return [(speaker, anonymize_text(text)) for speaker, text in dialogue_list]