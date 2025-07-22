from pydub import AudioSegment
import os
import subprocess
import re
import shlex
from pathlib import Path
from pathlib import Path

def merge_wav_files(wav_paths, output_path):


def validate_audio_filename(filename: str) -> bool:
    """
    Valida nome de arquivo de áudio
    """
    if not filename or len(filename) > 255:
        return False
    
    # Padrão seguro para arquivos de áudio
    safe_pattern = re.compile(r"^[a-zA-Z0-9\s\._-]+\.(mp3|wav|aac|m4a|ogg)$", re.IGNORECASE)
    return bool(safe_pattern.fullmatch(filename))

def safe_merge_audio(audio_files: list, output_filename: str, fade_duration: float = 1.0):
    """
    Merge arquivos de áudio de forma segura
    """
    # 1. VALIDAÇÃO DE ENTRADA
    if not audio_files or len(audio_files) < 2:
        raise ValueError("Pelo menos 2 arquivos de áudio são necessários para merge")
    
    if not validate_audio_filename(output_filename):
        raise ValueError(f"Nome de arquivo de saída inválido: {output_filename}")
    
    # Validar cada arquivo de entrada
    validated_files = []
    for audio_file in audio_files:
        if not validate_audio_filename(audio_file):
            raise ValueError(f"Nome de arquivo de entrada inválido: {audio_file}")
        
        audio_path = Path(audio_file)
        if not audio_path.exists():
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_file}")
        
        validated_files.append(str(audio_path))
    
    # 2. CONSTRUÇÃO SEGURA DO COMANDO FFMPEG
    cmd_list = ["ffmpeg", "-y"]  # -y para sobrescrever
    
    # Adicionar inputs
    for audio_file in validated_files:
        cmd_list.extend(["-i", audio_file])
    
    # Filtro para concatenar com fade
    filter_complex = ""
    for i, _ in enumerate(validated_files):
        if i == 0:
            filter_complex = f"[{i}:a]"
        else:
            filter_complex += f"[{i}:a]"
    
    filter_complex += f"concat=n={len(validated_files)}:v=0:a=1[outa]"
    
    # Adicionar filtro e output
    cmd_list.extend([
        "-filter_complex", filter_complex,
        "-map", "[outa]",
        "-acodec", "libmp3lame",
        "-b:a", "192k",
        output_filename
    ])
    
    # 3. EXECUÇÃO SEGURA
    try:
        print(f"Executando merge seguro: {len(validated_files)} arquivos")
        result = subprocess.run(
            cmd_list,
            shell=False,
            capture_output=True,
            text=True,
            check=False,
            timeout=600  # 10 minutos timeout
        )
        
        if result.returncode != 0:
            print(f"Erro no merge de áudio (código {result.returncode})")
            print(f"Stderr: {result.stderr}")
            raise RuntimeError(f"Falha no merge de áudio: {result.stderr}")
        else:
            print(f"Merge de áudio concluído com sucesso: {output_filename}")
            
        return result
        
    except subprocess.TimeoutExpired:
        print("Erro: Merge de áudio excedeu timeout de 10 minutos")
        raise
    except FileNotFoundError:
        print("Erro: ffmpeg não encontrado. Instale o ffmpeg primeiro")
        raise
    except Exception as e:
        print(f"Erro inesperado no merge de áudio: {e}")
        raise


    """
    Combina arquivos WAV de forma segura
    """
    combined = AudioSegment.empty()
    for path in wav_paths:
        # Validação de path para prevenir path traversal
        safe_path = Path(path).resolve()
        if not safe_path.exists() or not str(safe_path).endswith('.wav'):
            print(f"⚠️ Arquivo inválido ou não encontrado: {path}")
            continue
            
        audio = AudioSegment.from_wav(str(safe_path))
        combined += audio
    
    # Validação do path de saída
    safe_output = Path(output_path).resolve()
    combined.export(str(safe_output), format="wav")
    print(f"🧩 Áudio combinado salvo em {safe_output}")

def safe_ffmpeg_command(input_files, output_file):
    """
    Executa comando ffmpeg de forma segura usando lista de argumentos
    """
    # CORRETO: Usar lista de argumentos em vez de string
    cmd = ["ffmpeg", "-y"]  # -y para sobrescrever arquivos
    
    for input_file in input_files:
        # Validar cada arquivo de entrada
        safe_input = Path(input_file).resolve()
        if not safe_input.exists():
            raise ValueError(f"Arquivo não encontrado: {input_file}")
        cmd.extend(["-i", str(safe_input)])
    
    # Validar arquivo de saída
    safe_output = Path(output_file).resolve()
    cmd.extend(["-filter_complex", "concat=n={}:v=0:a=1".format(len(input_files))])
    cmd.append(str(safe_output))
    
    # SEGURO: shell=False e lista de argumentos
    result = subprocess.run(cmd, shell=False, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Erro no ffmpeg: {result.stderr}")
    
    return str(safe_output)

if __name__ == "__main__":
    audio_paths = [
        "assets/audio/scene_1.wav",
        "assets/audio/scene_2.wav", 
        "assets/audio/scene_3.wav",
    ]
    merge_output = "assets/audio/final_audio.wav"
    merge_wav_files(audio_paths, merge_output)put)
