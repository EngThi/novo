# YouTube Automation Pipeline

Este projeto automatiza a criação de vídeos a partir de texto, IA de voz, IA de imagem e montagem com MoviePy.

## Estrutura

- `.devcontainer/devcontainer.json` – configuração para Codespaces (Python 3.12).
- `tts_module.py` – gera áudio com Google Cloud TTS.
- `merge_audio.py` – concatena arquivos WAV.
- `sdxl_module.py`, `imagen_module.py` – geram imagens IA.
- `assembly.py` – monta vídeo com MoviePy.
- `main.py` – orquestra todo o pipeline.
- `requirements.txt` – dependências Python.
- `assets/` – local para colocar manualmente imagens geradas, áudios finais e vídeos de saída.

## Como usar

1. **Clonar e preparar**  
git clone https://github.com/EngThi/youtube-automation.git
cd youtube-automation
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

text
2. **Gerar imagens IA no Colab**  
- Abra `sdxl_generation.ipynb` no Colab, defina prompts, gere e baixe em `images/`.
- Faça upload dessas imagens para `assets/images/` no seu clone local ou Cloud Shell.
3. **Configurar credenciais GCP**  
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/youtube-perplexity-xxxx.json"

text
4. **Executar pipeline completo**  
python main.py

text
5. **Baixar vídeo**  
- Pelo explorer do Cloud Shell, ou  
- `gcloud alpha cloud-shell scp cloudshell:~/youtube-automation/assets/videos/output_*.mp4 localhost:./`

## Personalizações

- Ajuste `main.py` para alternar entre `sdxl_paths` e `imagen_paths`.
- Para Reels/Shorts, modifique `assembly.py` para resolução `(1080,1920)`.
- Integre upload via YouTube Data API no fim de `main.py`.

---

## 2. Abrir o Codespace e rodar testes locais

1. No GitHub, clique em **Code → Open with Codespaces**.  
2. O ambiente carregará conforme o `.devcontainer`.  
3. No terminal do Codespace:  
python run_tts.py # testa TTS
python merge_audio.py # testa merge de áudio
python main.py # gera vídeo de teste (use dummy images ou reais)

text
4. Ajuste qualquer erro e commit/push das correções.

---

## 3. Repetir ciclo de geração de imagens

Sempre que quiser novos vídeos:

1. No Colab, ajuste prompts e gere novas imagens.  
2. Baixe e envie para `assets/images/`.  
3. No Codespaces ou Cloud Shell, rode `python main.py`.  

Você terá um fluxo contínuo: edição de código no Codespaces, geração de imagens em GPU no Colab e montagem final no Cloud Shell/GCP.

Pronto para testar o pipeline completo? Basta abrir seu Codespace, garantir que o `assets/images/` contenha imagens válidas e executar:

python main.py

text

Se surgir qualquer erro ou quiser integrar upload YouTube, legendas ou verticalização, é só avisar!
