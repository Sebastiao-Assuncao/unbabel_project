from google.cloud import translate_v2 as translate
from fastapi import HTTPException
import os

translate_client = translate.Client()

supported_languages = [item['language'] for item in translate_client.get_languages()]

def translate_text(source: str, target: str, text: str):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Check for valid target language
    if target not in supported_languages:
        raise HTTPException(status_code=400, detail="Non-existing target language. Check input")
    
    
    if not source or source not in supported_languages:
        # If source language is not provided or is wrong, Translation API will try to detect it
        result = translate_client.translate(text, target_language=target)
        return (result["translatedText"], result["detectedSourceLanguage"])


    result = translate_client.translate(text, source_language=source, target_language=target)
    return (result["translatedText"], source)
    


def mock_translate(text: str, target_language: str) -> str:
    return f"{text} [Translated to {target_language}]"
