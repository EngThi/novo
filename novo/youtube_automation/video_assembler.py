
import os
import json
import logging
from pathlib import Path
from moviepy.editor import *
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoAssembler:
    def __init__(self):
        self.temp_dir = Path("temp_assembly")
        self.temp_dir.mkdir(exist_ok=True)
    
    def load_project_assets(self, project_dir):
        """Carrega todos os assets do projeto"""
        assets = {
            "audio": [],
            "images": [],
            "script": None
        }
        
        # Carregar áudios
        audio_dir = project_dir / "assets" / "audio"
        if audio_dir.exists():
            for audio_file in audio_dir.glob("*.mp3"):
                assets["audio"].append(audio_file)
        
        # Carregar imagens
        images_dir = project_dir / "assets" / "images"
        if images_dir.exists():
            for img_file in images_dir.glob("*.jpg"):
                assets["images"].append(img_file)
        
        # Carregar script
        script_file = project_dir / "script.json"
        if script_file.exists():
            with open(script_file, "r", encoding="utf-8") as f:
                assets["script"] = json.load(f)
        
        return assets
    
    def create_video_clips(self, assets):
        """Cria clipes de vídeo baseados nos assets"""
        clips = []
        
        if not assets["audio"] or not assets["images"]:
            logger.error("Assets insuficientes para montagem")
            return []
        
        # Calcular duração total do áudio
        total_audio_duration = 0
        audio_clips = []
        
        for audio_file in sorted(assets["audio"]):
            try:
                audio_clip = AudioFileClip(str(audio_file))
                audio_clips.append(audio_clip)
                total_audio_duration += audio_clip.duration
            except Exception as e:
                logger.error(f"Erro ao carregar áudio {audio_file}: {e}")
        
        if not audio_clips:
            return []
        
        # Combinar áudios
        final_audio = concatenate_audioclips(audio_clips)
        
        # Calcular duração por imagem
        num_images = len(assets["images"])
        if num_images == 0:
            return []
        
        duration_per_image = total_audio_duration / num_images
        
        # Criar clipes de imagem
        for i, img_path in enumerate(sorted(assets["images"])):
            try:
                # Carregar e redimensionar imagem
                img_clip = ImageClip(str(img_path), duration=duration_per_image)
                img_clip = img_clip.resize((1920, 1080))
                
                # Aplicar transições suaves
                if i > 0:
                    img_clip = img_clip.crossfadein(0.5)
                if i < num_images - 1:
                    img_clip = img_clip.crossfadeout(0.5)
                
                clips.append(img_clip)
                
            except Exception as e:
                logger.error(f"Erro ao processar imagem {img_path}: {e}")
        
        if clips:
            # Concatenar clipes de imagem
            video_clip = concatenate_videoclips(clips, method="compose")
            
            # Adicionar áudio
            video_clip = video_clip.set_audio(final_audio)
            
            return video_clip
        
        return None
    
    def add_intro_outro(self, main_clip, project_data):
        """Adiciona intro e outro ao vídeo"""
        try:
            # Criar intro simples
            intro_text = f"🎬 {project_data.get('topic', 'Novo Vídeo')}"
            intro_clip = TextClip(
                intro_text,
                fontsize=60,
                color='white',
                font='Arial-Bold'
            ).set_duration(3).set_position('center')
            
            intro_bg = ColorClip(size=(1920, 1080), color=(0, 0, 0)).set_duration(3)
            intro = CompositeVideoClip([intro_bg, intro_clip])
            
            # Criar outro simples
            outro_text = "👍 Se gostou, deixe seu like!\n🔔 Inscreva-se para mais conteúdo!"
            outro_clip = TextClip(
                outro_text,
                fontsize=40,
                color='white',
                font='Arial'
            ).set_duration(4).set_position('center')
            
            outro_bg = ColorClip(size=(1920, 1080), color=(0, 0, 0)).set_duration(4)
            outro = CompositeVideoClip([outro_bg, outro_clip])
            
            # Combinar tudo
            final_video = concatenate_videoclips([intro, main_clip, outro])
            return final_video
            
        except Exception as e:
            logger.error(f"Erro ao adicionar intro/outro: {e}")
            return main_clip
    
    def assemble_video(self, project_dir, output_name=None):
        """Monta o vídeo final"""
        try:
            logger.info("Iniciando montagem do vídeo...")
            
            # Carregar assets
            assets = self.load_project_assets(project_dir)
            
            if not assets["audio"] or not assets["images"]:
                logger.error("Assets insuficientes - precisa de áudio e imagens")
                return None
            
            # Criar clipe principal
            main_clip = self.create_video_clips(assets)
            if not main_clip:
                logger.error("Falha ao criar clipe principal")
                return None
            
            # Adicionar intro/outro
            if assets["script"]:
                final_clip = self.add_intro_outro(main_clip, assets["script"])
            else:
                final_clip = main_clip
            
            # Definir nome do arquivo de saída
            if not output_name:
                topic = assets["script"].get("topic", "video") if assets["script"] else "video"
                output_name = f"{topic.replace(' ', '_')}_final.mp4"
            
            # Criar diretório final
            final_dir = project_dir / "final"
            final_dir.mkdir(exist_ok=True)
            
            output_path = final_dir / output_name
            
            # Renderizar vídeo
            logger.info(f"Renderizando vídeo: {output_path}")
            final_clip.write_videofile(
                str(output_path),
                fps=30,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Limpar recursos
            final_clip.close()
            if main_clip != final_clip:
                main_clip.close()
            
            logger.info(f"✓ Vídeo montado com sucesso: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Erro na montagem do vídeo: {e}")
            return None

def main():
    """Função principal do montador"""
    parser = argparse.ArgumentParser(description='Monta vídeo final')
    parser.add_argument('--output-dir', type=str, required=True,
                        help='Diretório do projeto')
    parser.add_argument('--output-name', type=str,
                        help='Nome do arquivo de saída')
    args = parser.parse_args()
    
    project_dir = Path(args.output_dir)
    
    if not project_dir.exists():
        logger.error(f"Diretório não existe: {project_dir}")
        return
    
    assembler = VideoAssembler()
    result = assembler.assemble_video(project_dir, args.output_name)
    
    if result:
        logger.info(f"✓ Montagem concluída: {result}")
    else:
        logger.error("✗ Falha na montagem")

if __name__ == "__main__":
    main()
