from tts_module import synthesize_text

scenes = [
    "Esta é a primeira cena.",
    "Agora a segunda cena com mais detalhes.",
    "Encerrando na terceira cena."
]

audio_paths = []
for idx, cena in enumerate(scenes, start=1):
    out = f"assets/audio/scene_{idx}.wav"
    synthesize_text(cena, out)
    audio_paths.append(out)
print("Arquivos gerados:", audio_paths)
