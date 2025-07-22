import os
from google.cloud import texttospeech

def synthesize_text(
    text: str,
    output_path: str,
    language_code: str = "pt-BR",
    voice_name: str = "pt-BR-Wavenet-A",
    speaking_rate: float = 1.0,
    pitch: float = 0.0
) -> None:
    """
    Gera um arquivo WAV com voz natural do Google Cloud TTS.

    Args:
        text: Texto a ser sintetizado.
        output_path: Caminho para salvar o arquivo .wav.
        language_code: Código da língua (ex.: "pt-BR").
        voice_name: Nome da voz Wavenet.
        speaking_rate: Velocidade da fala (0.25–4.0).
        pitch: Tom da voz em semitons (-20.0–20.0).
    """
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=speaking_rate,
        pitch=pitch
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as out:
        out.write(response.audio_content)
        print(f"🎙️ Áudio salvo: {output_path}")
