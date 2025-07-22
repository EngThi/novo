#!/usr/bin/env python3
import os
import sys
import time
import logging
import schedule
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import json
import subprocess

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "youtube_automation" / "output"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

class PipelineAutomatizado:
    def __init__(self):
        """Inicializa o pipeline automatizado"""
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.configure_apis()
        
    def configure_apis(self):
        """Configura as APIs necessárias"""
        # Configurar Gemini para geração de conteúdo
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            logger.info("API Gemini configurada com sucesso")
        else:
            logger.warning("Chave da API Gemini não encontrada no .env")
        
        # Verificar credenciais do Google Cloud
        if not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
            logger.warning(f"Arquivo de credenciais GCP não encontrado: {GOOGLE_APPLICATION_CREDENTIALS}")
    
    def discover_trending_topics(self):
        """Descobre tópicos em alta para criação de conteúdo"""
        logger.info("Descobrindo tópicos em alta...")
        
        try:
            # Usar Gemini para identificar tópicos em alta
            model = genai.GenerativeModel('gemini-1.5-pro')
            prompt = """
            Identifique 5 tópicos em alta no Brasil hoje que seriam interessantes para vídeos curtos.
            Para cada tópico, forneça:
            1. Um título curto e cativante
            2. Uma breve descrição do assunto
            3. Por que esse tópico está gerando interesse
            
            Formate sua resposta como uma lista JSON com os campos: title, description, e relevance.
            """
            
            response = model.generate_content(prompt)
            
            # Processar a resposta para extrair os tópicos
            content = response.text
            # Tentar encontrar conteúdo JSON na resposta
            import re
            json_match = re.search(r'\[\s*\{.*\}\s*\]', content, re.DOTALL)
            
            if json_match:
                topics_json = json_match.group(0)
                topics = json.loads(topics_json)
            else:
                # Fallback: Estruturar manualmente
                topics = [
                    {
                        "title": "Mistérios do Folclore Brasileiro",
                        "description": "Explorando as lendas menos conhecidas do folclore brasileiro",
                        "relevance": "Próximo ao dia do folclore"
                    }
                ]
            
            # Salvar tópicos descobertos
            topics_dir = OUTPUT_DIR / f"{self.today}_trending_topics"
            topics_dir.mkdir(exist_ok=True, parents=True)
            
            with open(topics_dir / "topics.json", "w", encoding="utf-8") as f:
                json.dump(topics, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Descobertos {len(topics)} tópicos em alta")
            return topics
            
        except Exception as e:
            logger.error(f"Erro ao descobrir tópicos em alta: {e}")
            return []
    
    def generate_script(self, topic):
        """Gera um roteiro detalhado para o tópico"""
        logger.info(f"Gerando roteiro para: {topic['title']}")
        
        try:
            # Usar Gemini para gerar o roteiro
            model = genai.GenerativeModel('gemini-1.5-pro')
            prompt = f"""
            Crie um roteiro detalhado para um vídeo de 3-5 minutos sobre: "{topic['title']}"
            
            Descrição: {topic.get('description', '')}
            
            O roteiro deve incluir:
            1. Uma introdução cativante (15-20 segundos)
            2. Desenvolvimento do tema com 3-5 pontos principais
            3. Conclusão com uma chamada para ação
            
            Para cada seção, inclua timestamps no formato [MM:SS] e instruções para imagens entre parênteses.
            Exemplo:
            [00:00] Olá, pessoal! Hoje vamos explorar os mistérios do folclore brasileiro. (Imagem: floresta amazônica ao anoitecer)
            """
            
            response = model.generate_content(prompt)
            script = response.text
            
            # Criar diretório para o projeto
            project_name = topic['title'].replace(" ", "_")
            project_dir = OUTPUT_DIR / f"{self.today}_{project_name}"
            project_dir.mkdir(exist_ok=True, parents=True)
            assets_dir = project_dir / "assets"
            assets_dir.mkdir(exist_ok=True)
            
            # Salvar o roteiro
            with open(project_dir / "script.txt", "w", encoding="utf-8") as f:
                f.write(script)
            
            # Analisar o roteiro para extrair segmentos e prompts de imagem
            segments = self.parse_script(script)
            with open(project_dir / "segments.json", "w", encoding="utf-8") as f:
                json.dump(segments, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Roteiro gerado com {len(segments)} segmentos")
            return project_dir, segments
        
        except Exception as e:
            logger.error(f"Erro ao gerar roteiro: {e}")
            return None, []
    
    def parse_script(self, script):
        """Extrai segmentos e prompts de imagem do roteiro"""
        lines = script.split('\n')
        segments = []
        current_segment = None
        
        import re
        timestamp_pattern = re.compile(r'\[(\d+):(\d+)\]')
        image_pattern = re.compile(r'\(Imagem:?\s*(.*?)\)', re.IGNORECASE)
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Procurar por timestamp
            timestamp_match = timestamp_pattern.search(line)
            if timestamp_match:
                # Salvar segmento anterior
                if current_segment:
                    segments.append(current_segment)
                
                # Iniciar novo segmento
                minutes = int(timestamp_match.group(1))
                seconds = int(timestamp_match.group(2))
                time_seconds = minutes * 60 + seconds
                
                text = line[timestamp_match.end():].strip()
                current_segment = {
                    "timestamp": f"{minutes:02d}:{seconds:02d}",
                    "time_seconds": time_seconds,
                    "text": text,
                    "image_prompt": ""
                }
                
                # Procurar por prompt de imagem
                image_match = image_pattern.search(text)
                if image_match:
                    current_segment["image_prompt"] = image_match.group(1).strip()
                    current_segment["text"] = text[:image_match.start()].strip()
            
            elif current_segment:
                # Continuar segmento atual
                image_match = image_pattern.search(line)
                if image_match:
                    current_segment["image_prompt"] = image_match.group(1).strip()
                else:
                    current_segment["text"] += " " + line
        
        # Adicionar o último segmento
        if current_segment:
            segments.append(current_segment)
        
        return segments
    
    def generate_narration(self, project_dir, segments):
        """Gera narração para os segmentos do roteiro usando Google Cloud TTS"""
        logger.info("Gerando narração com Google Cloud TTS")
        
        try:
            # Criar diretório para áudios
            audio_dir = project_dir / "assets" / "audio"
            audio_dir.mkdir(exist_ok=True, parents=True)
            
            # Preparar script para módulo TTS existente
            script_for_tts = []
            for i, segment in enumerate(segments):
                script_for_tts.append({
                    "id": f"segment_{i:02d}",
                    "text": segment["text"]
                })
            
            # Salvar script para TTS
            with open(project_dir / "tts_script.json", "w", encoding="utf-8") as f:
                json.dump(script_for_tts, f, ensure_ascii=False, indent=2)
            
            # Executar o módulo TTS existente no youtube_automation
            cmd = [
                "python", 
                str(PROJECT_ROOT / "youtube_automation" / "tts_module.py"),
                "--input", str(project_dir / "tts_script.json"),
                "--output", str(audio_dir)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Erro no TTS: {result.stderr}")
                return False
            
            logger.info(f"Narração gerada para {len(segments)} segmentos")
            
            # Atualizar segmentos com caminhos de áudio
            for i, segment in enumerate(segments):
                segment["audio_file"] = str(audio_dir / f"segment_{i:02d}.wav")
            
            # Salvar segmentos atualizados
            with open(project_dir / "segments.json", "w", encoding="utf-8") as f:
                json.dump(segments, f, ensure_ascii=False, indent=2)
            
            return True
        
        except Exception as e:
            logger.error(f"Erro ao gerar narração: {e}")
            return False
    
    def generate_images(self, project_dir, segments):
        """Gera imagens para os segmentos usando Google Vertex AI Imagen"""
        logger.info("Gerando imagens com API de IA")
        
        try:
            # Criar diretório para imagens
            images_dir = project_dir / "assets" / "images"
            images_dir.mkdir(exist_ok=True, parents=True)
            
            # Definir prompts padrão para fallback
            default_prompts = [
                "Brazilian folklore creatures in a mystical forest, digital art style",
                "Ancient Amazonian legends, dramatic cinematic lighting",
                "Mysterious Brazilian folklore characters, professional photography",
                "Traditional cultural stories from Brazil, illustrated style",
                "Legendary creatures from South American folklore, fantasy art"
            ]
            
            # Gerar imagens para cada segmento com prompt
            for i, segment in enumerate(segments):
                # Obter o prompt da imagem ou usar fallback
                image_prompt = segment.get("image_prompt", "").strip()
                if not image_prompt:
                    image_prompt = default_prompts[i % len(default_prompts)]
                
                # Melhorar o prompt para geração de imagem
                enhanced_prompt = f"High quality, cinematic, 4K: {image_prompt}"
                
                # Aqui você integraria com a API de geração de imagens
                # Como estamos simulando, salvamos um placeholder
                logger.info(f"Gerando imagem para: '{enhanced_prompt}'")
                
                # Salvar o prompt para uso futuro
                segment["enhanced_image_prompt"] = enhanced_prompt
                
                # Caminho da imagem (será gerada ou baixada)
                image_path = str(images_dir / f"image_{i:02d}.jpg")
                segment["image_file"] = image_path
                
                # NOTA: Aqui você adicionaria código para chamar a API de imagem
                # Por enquanto, apenas simulamos o processo
                
                # Simulação: crie um arquivo de texto com o prompt como fallback
                with open(images_dir / f"prompt_{i:02d}.txt", "w", encoding="utf-8") as f:
                    f.write(enhanced_prompt)
            
            # Salvar segmentos atualizados
            with open(project_dir / "segments.json", "w", encoding="utf-8") as f:
                json.dump(segments, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Prompts de imagem gerados para {len(segments)} segmentos")
            
            # NOTA: Aqui você poderia automatizar a chamada para o notebook do Colab
            # ou integrar diretamente com a API do Vertex AI
            
            # Se você precisar de um placeholder para desenvolvimento, gere imagens de cor única
            for i, segment in enumerate(segments):
                # Criar uma imagem de placeholder
                try:
                    from PIL import Image, ImageDraw, ImageFont
                    img = Image.new('RGB', (1280, 720), color=(73, 109, 137))
                    d = ImageDraw.Draw(img)
                    d.text((640, 360), f"Imagem {i+1}: {segment.get('enhanced_image_prompt', '')[:50]}...", 
                           fill=(255, 255, 255), anchor="mm")
                    img.save(segment["image_file"])
                except Exception as e:
                    logger.warning(f"Não foi possível gerar imagem placeholder: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar imagens: {e}")
            return False
    
    def assemble_video(self, project_dir, segments):
        """Monta o vídeo final a partir dos segmentos, narração e imagens"""
        logger.info("Montando vídeo final")
        
        try:
            # Criar diretório para vídeo final
            final_dir = project_dir / "final"
            final_dir.mkdir(exist_ok=True)
            
            # Verificar se temos MoviePy instalado
            try:
                import moviepy.editor as mpy
            except ImportError:
                logger.error("MoviePy não está instalado. Execute: pip install moviepy")
                return False
            
            # Criar clipes para cada segmento
            clips = []
            for i, segment in enumerate(segments):
                # Verificar se temos arquivo de áudio
                if not os.path.exists(segment.get("audio_file", "")):
                    logger.warning(f"Arquivo de áudio não encontrado para segmento {i}")
                    continue
                
                # Verificar se temos arquivo de imagem
                if not os.path.exists(segment.get("image_file", "")):
                    logger.warning(f"Arquivo de imagem não encontrado para segmento {i}")
                    continue
                
                # Carregar áudio e obter duração
                audio_clip = mpy.AudioFileClip(segment["audio_file"])
                duration = audio_clip.duration
                
                # Criar clipe de imagem com duração igual ao áudio
                img_clip = mpy.ImageClip(segment["image_file"]).set_duration(duration)
                
                # Adicionar texto com o segmento do roteiro
                txt_clip = mpy.TextClip(
                    segment["text"][:50] + "..." if len(segment["text"]) > 50 else segment["text"],
                    fontsize=24, color='white', bg_color='black', size=(img_clip.w, None), 
                    method='caption'
                ).set_position(('center', 'bottom')).set_duration(duration)
                
                # Combinar imagem e texto
                video_clip = mpy.CompositeVideoClip([img_clip, txt_clip])
                
                # Adicionar áudio
                final_clip = video_clip.set_audio(audio_clip)
                
                clips.append(final_clip)
            
            if not clips:
                logger.error("Nenhum clipe válido para montar o vídeo")
                return False
            
            # Concatenar todos os clipes
            final_video = mpy.concatenate_videoclips(clips, method="compose")
            
            # Salvar vídeo final
            output_file = final_dir / "video_final.mp4"
            final_video.write_videofile(
                str(output_file),
                fps=24,
                codec='libx264',
                audio_codec='aac',
                threads=4
            )
            
            logger.info(f"Vídeo final montado e salvo em: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao montar vídeo: {e}")
            return False
    
    def upload_to_drive(self, project_dir):
        """Faz upload da pasta do projeto para o Google Drive"""
        logger.info("Iniciando upload para o Google Drive")
        
        try:
            # Executar o módulo de upload existente
            cmd = [
                "python",
                str(PROJECT_ROOT / "drive-uploader" / "backend" / "upload.py"),
                "--input-dir", str(project_dir)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Erro no upload para Drive: {result.stderr}")
                return False
            
            logger.info("Upload para Google Drive concluído com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao fazer upload para Google Drive: {e}")
            return False
    
    def run_pipeline(self):
        """Executa o pipeline completo de automação"""
        logger.info("Iniciando pipeline de automação de vídeo")
        
        # Passo 1: Descobrir tópicos em alta
        topics = self.discover_trending_topics()
        if not topics:
            logger.error("Não foi possível descobrir tópicos em alta")
            return False
        
        # Selecionar o primeiro tópico (mais relevante)
        selected_topic = topics[0]
        logger.info(f"Tópico selecionado: {selected_topic['title']}")
        
        # Passo 2: Gerar roteiro
        project_dir, segments = self.generate_script(selected_topic)
        if not project_dir or not segments:
            logger.error("Não foi possível gerar o roteiro")
            return False
        
        # Passo 3: Gerar narração
        if not self.generate_narration(project_dir, segments):
            logger.error("Não foi possível gerar a narração")
            return False
        
        # Passo 4: Gerar imagens
        if not self.generate_images(project_dir, segments):
            logger.error("Não foi possível gerar as imagens")
            return False
        
        # Passo 5: Montar vídeo
        if not self.assemble_video(project_dir, segments):
            logger.error("Não foi possível montar o vídeo")
            return False
        
        # Passo 6: Fazer upload para o Google Drive
        if not self.upload_to_drive(project_dir):
            logger.error("Não foi possível fazer upload para o Google Drive")
            return False
        
        logger.info("Pipeline concluído com sucesso!")
        return True


def run_scheduled_job():
    """Executa o job agendado"""
    pipeline = PipelineAutomatizado()
    pipeline.run_pipeline()


if __name__ == "__main__":
    # Verificar modo de execução
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        # Modo agendado
        logger.info("Iniciando em modo agendado (execução às 3:00 da manhã)")
        schedule.every().day.at("03:00").do(run_scheduled_job)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        # Execução direta
        pipeline = PipelineAutomatizado()
        pipeline.run_pipeline()