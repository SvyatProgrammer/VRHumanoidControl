import requests
import json

def transcribe_with_diarization(audio_path, api_key):
    url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&diarize=true&language=ru"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "audio/wav"  
    }

    with open(audio_path, "rb") as audio_file:
        response = requests.post(url, headers=headers, data=audio_file)

    if response.status_code != 200:
        raise Exception(f"Deepgram API Error: {response.status_code}")

    data = response.json()
    formatted_dialogue = []

    try:
        paragraphs = data["results"]["channels"][0]["alternatives"][0]["paragraphs"]["transcript_data"]
        for p in paragraphs:
            formatted_dialogue.append((p["speaker"], p["text"]))
    except KeyError:
        words = data["results"]["channels"][0]["alternatives"][0]["words"]
        if words:
            current_speaker = words[0]["speaker"]
            current_text = []
            for w in words:
                if w["speaker"] == current_speaker:
                    current_text.append(w["word"])
                else:
                    formatted_dialogue.append((current_speaker, " ".join(current_text)))
                    current_speaker = w["speaker"]
                    current_text = [w["word"]]
            formatted_dialogue.append((current_speaker, " ".join(current_text)))

    return formatted_dialogue