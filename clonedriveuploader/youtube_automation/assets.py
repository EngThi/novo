from typing import Dict
from google.cloud import texttospeech
import time
import google.generativeai as genai

import subprocess
import re
import shlex
from pathlib import Path


def validate_filename(filename: str) -> bool:
    """
    Valida nome de arquivo para prevenir injeção de comando
    """
    if not filename or len(filename) > 255:
        return False
    
    # Padrão seguro: apenas letras, números, espaços, hífens, underscores e pontos
    safe_pattern = re.compile(r"^[a-zA-Z0-9\s\._-]+$")
    return bool(safe_pattern.fullmatch(filename))

def safe_subprocess_run(command_list, **kwargs):
    """
    Executa subprocess de forma segura com validação
    """
    if not isinstance(command_list, list):
        raise ValueError("Comando deve ser uma lista de strings")
    
    # Validar cada argumento
    for arg in command_list:
        if not isinstance(arg, str):
            raise ValueError("Todos os argumentos devem ser strings")
    
    # Configurações seguras padrão
    safe_kwargs = {
        'shell': False,           # NUNCA usar shell=True
        'capture_output': True,   # Capturar stdout/stderr
        'text': True,            # Decodificar como texto
        'check': False,          # Não levantar exceção automaticamente
        'timeout': 300           # Timeout de 5 minutos
    }
    
    # Atualizar com kwargs fornecidos
    safe_kwargs.update(kwargs)
    
    try:
        print(f"Executando comando seguro: {command_list}")
        result = subprocess.run(command_list, **safe_kwargs)
        
        if result.returncode != 0:
            print(f"Comando falhou com código {result.returncode}")
            print(f"Stderr: {result.stderr}")
        else:
            print("Comando executado com sucesso")
            
        return result
        
    except subprocess.TimeoutExpired:
        print("Erro: Comando excedeu timeout")
        raise
    except FileNotFoundError:
        print(f"Erro: Comando '{command_list[0]}' não encontrado")
        raise
    except Exception as e:
        print(f"Erro inesperado: {e}")
        raise

def process_media_file_secure(input_filename: str, output_filename: str, command_type: str = "convert"):
    """
    Processa arquivo de mídia de forma segura
    """
    # 1. VALIDAÇÃO RIGOROSA DA ENTRADA
    if not validate_filename(input_filename) or not validate_filename(output_filename):
        raise ValueError(f"Nome de arquivo inválido detectado. Entrada: '{input_filename}', Saída: '{output_filename}'")
    
    # Verificar se arquivo de entrada existe
    input_path = Path(input_filename)
    if not input_path.exists():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_filename}")
    
    # 2. CONSTRUÇÃO SEGURA DO COMANDO
    if command_type == "convert":
        # Conversão de vídeo para áudio
        cmd_list = [
            "ffmpeg",
            "-y",                    # Sobrescrever arquivo de saída
            "-i", str(input_path),   # Arquivo de entrada
            "-acodec", "libmp3lame", # Codec de áudio
            "-b:a", "128k",          # Bitrate
            output_filename          # Arquivo de saída
        ]
    elif command_type == "extract_audio":
        # Extrair áudio apenas
        cmd_list = [
            "ffmpeg",
            "-y",
            "-i", str(input_path),
            "-vn",                   # Sem vídeo
            "-acodec", "copy",       # Copiar codec de áudio
            output_filename
        ]
    else:
        raise ValueError(f"Tipo de comando não suportado: {command_type}")
    
    # 3. EXECUÇÃO SEGURA
    return safe_subprocess_run(cmd_list)


from pathlib import Path

class AssetProductionModule:
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.tts_client = texttospeech.TextToSpeechClient()
    
    def safe_media_process(self, input_path, output_path, process_type="convert"):
        """
        Processa mídia de forma segura usando subprocess
        """
        # Validação de paths
        safe_input = Path(input_path).resolve()
        safe_output = Path(output_path).resolve()
        
        if not safe_input.exists():
            raise FileNotFoundError(f"Arquivo de entrada não encontrado: {input_path}")
        
        # Comandos seguros baseados no tipo
        if process_type == "convert":
            cmd = ["ffmpeg", "-i", str(safe_input), str(safe_output)]
        elif process_type == "resize":
            cmd = ["ffmpeg", "-i", str(safe_input), "-vf", "scale=1280:720", str(safe_output)]
        else:
            raise ValueError(f"Tipo de processo inválido: {process_type}")
        
        # Execução segura
        result = subprocess.run(cmd, shell=False, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Erro no processamento: {result.stderr}")
        
        return str(safe_output)
    
    def generate_audio_tts(self, script: str, output_path: str) -> str:
        """
        Gera áudio com Google TTS (1M caracteres grátis/mês)
        """
        # Configuração para voz brasileira natural
        synthesis_input = texttospeech.SynthesisInput(text=script)
        voice = texttospeech.VoiceSelectionParams(
            language_code="pt-BR",
            name="pt-BR-Neural2-A",  # Voz feminina brasileira
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )
        
        response = self.tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        
        with open(output_path, "wb") as out:
            out.write(response.audio_content)
        
        return output_path
    
    def generate_thumbnails_gemini(self, title: str) -> Dict[str, str]:
        """
        Gera thumbnails A/B usando Gemini 2.0 Flash Image Generation
        """
        thumbnails = {}
        
        prompts = {
            'A': f"""
            Crie uma thumbnail profissional de YouTube para "{title}".
            ESPECIFICAÇÕES:
            - Resolução: 1280x72020 pixels
            - Pessoa com expressão de susto/surpresa
            - Cores vibrantes: vermelho, amarelo, contraste alto
            - Texto legível em português
            - Estilo: Realista, cinematográfico
            - Elementos: Sombras dramáticas, lighting profissional
            """,
            'B': f"""
            Crie uma thumbnail atmosférica de YouTube para "{title}".
            ESPECIFICAÇÕES:
            - Resolução: 1280x720 pixels
            - Ambiente misterioso, silhuetas
            - Cores escuras: azul profundo, roxo, preto
            - Texto com efeito de brilho
            - Estilo: Artístico, gótico
            - Elementos: Neblina, elementos sobrenaturais
            """
        }
        
        for version, prompt in prompts.items():
            response = genai.GenerativeModel('gemini-2.0-flash').generate_content(
                prompt,
                generation_config={
                    "response_modalities": ["IMAGE", "TEXT"],
                    "temperature": 0.7
                }
            )
            
            thumbnail_path = f"thumbnail_{version}_{int(time.time())}.jpg"
            if response.parts:
                for part in response.parts:
                    if part.inline_data:
                        with open(thumbnail_path, "wb") as f:
                            f.write(part.inline_data.data)
            
            thumbnails[version] = thumbnail_path
        
        return thumbnails
    
    def generate_scene_images(self, scenes: list) -> list:
        """
        Gera imagens para cenas do roteiro
        """
        scene_images = []
        for i, scene in enumerate(scenes):
            prompt = f"Crie imagem para cena de horror: {scene[:100]}"
            response = genai.GenerativeModel('gemini-2.0-flash').generate_content(prompt)
            image_path = f"scene_{i}_{int(time.time())}.jpg"
            # Salvar imagem (lógica similar ao thumbnail)
            scene_images.append(image_path)
        return scene_images
