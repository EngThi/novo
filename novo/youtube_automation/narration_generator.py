import json
import requests
import os

def generate_narration():
    """Gera narração de áudio baseada nos roteiros."""
    # Carregar roteiros
    with open('data/scripts.json', 'r') as f:
        scripts = json.load(f)
    
    for i, script in enumerate(scripts):
        print(f"Gerando narração para: {script['topic']}")
        
        # Aqui você pode integrar com APIs de TTS como ElevenLabs, Google TTS, etc.
        # Exemplo com ElevenLabs:
        
        # api_key = os.environ.get("ELEVEN_LABS_API_KEY")
        # voice_id = "pNInz6obpgDQGcFmaJgB"  # ID de voz da ElevenLabs
        
        # for segment in script["timestamps"]:
        #     text = segment["text"]
        #     response = requests.post(
        #         f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        #         headers={"xi-api-key": api_key},
        #         json={"text": text}
        #     )
        #     
        #     # Salvar áudio
        #     with open(f"data/audio/script_{i}_segment_{segment['start']}.mp3", "wb") as f:
        #         f.write(response.content)
        
        # Simulação para teste:
        print(f"Narração gerada para {script['topic']}")
    
    print("Geração de narração concluída.")

if __name__ == "__main__":
    generate_narration()
import os
import json
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import texttospeech

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NarrationGenerator:
    def __init__(self):
        self.tts_client = None
        self.setup_tts()
    
    def setup_tts(self):
        """Configura o cliente Text-to-Speech"""
        try:
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if credentials_path and os.path.exists(credentials_path):
                self.tts_client = texttospeech.TextToSpeechClient()
                logger.info("Cliente TTS do Google Cloud configurado")
            else:
                logger.warning("Credenciais do Google Cloud não encontradas, usando TTS básico")
        except Exception as e:
            logger.error(f"Erro ao configurar TTS: {e}")
    
    def extract_narration_text(self, script_data):
        """Extrai texto para narração do roteiro"""
        narration_text = []
        
        if "sections" in script_data:
            for section in script_data["sections"]:
                # Remove instruções de imagem e timestamps
                text = section.get("text", "").strip()
                if text:
                    # Remove parênteses com instruções de imagem
                    import re
                    text = re.sub(r'\([^)]*\)', '', text)
                    text = re.sub(r'\[[^\]]*\]', '', text)
                    text = text.strip()
                    if text:
                        narration_text.append({
                            "section": section.get("title", ""),
                            "timestamp": section.get("timestamp", ""),
                            "text": text
                        })
        else:
            # Fallback para roteiro simples
            raw_text = script_data.get("raw_script", "")
            if raw_text:
                # Remove instruções e timestamps
                import re
                clean_text = re.sub(r'\([^)]*\)', '', raw_text)
                clean_text = re.sub(r'\[[^\]]*\]', '', clean_text)
                narration_text.append({
                    "section": "Roteiro Completo",
                    "timestamp": "00:00",
                    "text": clean_text.strip()
                })
        
        return narration_text
    
    def generate_audio_google(self, text, output_path):
        """Gera áudio usando Google Text-to-Speech"""
        try:
            # Configurar síntese
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configurar voz em português brasileiro
            voice = texttospeech.VoiceSelectionParams(
                language_code="pt-BR",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
            
            # Configurar áudio
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0
            )
            
            # Gerar áudio
            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Salvar arquivo
            with open(output_path, "wb") as f:
                f.write(response.audio_content)
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar áudio com Google TTS: {e}")
            return False
    
    def generate_audio_basic(self, text, output_path):
        """Fallback para TTS básico usando pyttsx3"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            # Configurar velocidade e voz
            engine.setProperty('rate', 180)
            voices = engine.getProperty('voices')
            if voices:
                # Procurar por voz em português
                for voice in voices:
                    if 'pt' in voice.id.lower() or 'brazil' in voice.id.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            # Salvar áudio
            engine.save_to_file(text, str(output_path))
            engine.runAndWait()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar áudio básico: {e}")
            return False
    
    def generate_narration(self, script_file, output_dir):
        """Gera narração completa do roteiro"""
        try:
            # Carregar roteiro
            with open(script_file, "r", encoding="utf-8") as f:
                script_data = json.load(f)
            
            # Extrair texto para narração
            narration_sections = self.extract_narration_text(script_data)
            
            if not narration_sections:
                logger.error("Nenhum texto encontrado para narração")
                return False
            
            # Criar diretório de áudio
            audio_dir = output_dir / "assets" / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)
            
            generated_files = []
            
            # Gerar áudio para cada seção
            for i, section in enumerate(narration_sections):
                filename = f"narration_{i+1:02d}_{section['section'].replace(' ', '_')}.mp3"
                output_path = audio_dir / filename
                
                logger.info(f"Gerando áudio para: {section['section']}")
                
                # Tentar Google TTS primeiro, depois fallback
                success = False
                if self.tts_client:
                    success = self.generate_audio_google(section['text'], output_path)
                
                if not success:
                    success = self.generate_audio_basic(section['text'], output_path)
                
                if success:
                    generated_files.append({
                        "file": str(output_path),
                        "section": section['section'],
                        "timestamp": section['timestamp'],
                        "duration": 0  # Será calculado depois
                    })
                    logger.info(f"✓ Áudio gerado: {filename}")
                else:
                    logger.error(f"✗ Falha ao gerar áudio para: {section['section']}")
            
            # Salvar metadados da narração
            narration_metadata = {
                "topic": script_data.get("topic", ""),
                "total_sections": len(narration_sections),
                "generated_files": len(generated_files),
                "files": generated_files
            }
            
            metadata_file = audio_dir / "narration_metadata.json"
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(narration_metadata, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Narração gerada com sucesso: {len(generated_files)} arquivos")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar narração: {e}")
            return False

def main():
    """Função principal do gerador de narração"""
    parser = argparse.ArgumentParser(description='Gera narração para o roteiro')
    parser.add_argument('--output-dir', type=str, required=True,
                        help='Diretório do projeto')
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    script_file = output_dir / "script.json"
    
    if not script_file.exists():
        logger.error(f"Arquivo de roteiro não encontrado: {script_file}")
        return
    
    generator = NarrationGenerator()
    success = generator.generate_narration(script_file, output_dir)
    
    if success:
        logger.info("✓ Geração de narração concluída")
    else:
        logger.error("✗ Falha na geração de narração")

if __name__ == "__main__":
    main()
