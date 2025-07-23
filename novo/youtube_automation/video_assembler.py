
#!/usr/bin/env python3
"""
Sistema Avançado de Montagem de Vídeos
Combina áudio, imagens e efeitos para criar vídeos profissionais
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess
from PIL import Image, ImageDraw, ImageFont
import tempfile

# Configuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoAssembler:
    """Sistema profissional de montagem de vídeos"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "video_assembly"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Verificar se FFmpeg está disponível
        self.ffmpeg_available = self._check_ffmpeg()
        
        # Configurações padrão
        self.video_config = {
            "resolution": "1920x1080",
            "fps": 30,
            "audio_bitrate": "128k",
            "video_bitrate": "2M",
            "format": "mp4"
        }
    
    def _check_ffmpeg(self) -> bool:
        """Verifica se FFmpeg está disponível"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, 
                                  text=True)
            return result.returncode == 0
        except FileNotFoundError:
            logger.warning("FFmpeg não encontrado. Funcionalidade limitada.")
            return False
    
    def create_intro_image(self, title: str, output_path: Path) -> Path:
        """Cria imagem de introdução com título"""
        try:
            # Criar imagem base
            img = Image.new('RGB', (1920, 1080), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            
            # Tentar carregar fonte
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96)
            except:
                font = ImageFont.load_default()
                title_font = ImageFont.load_default()
            
            # Adicionar gradiente simples
            for y in range(1080):
                color_value = int(26 + (y / 1080) * 40)
                draw.rectangle([(0, y), (1920, y+1)], fill=(color_value, color_value, color_value + 20))
            
            # Adicionar título
            bbox = draw.textbbox((0, 0), title, font=title_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (1920 - text_width) // 2
            y = (1080 - text_height) // 2
            
            # Sombra do texto
            draw.text((x+3, y+3), title, font=title_font, fill='#000000')
            # Texto principal
            draw.text((x, y), title, font=title_font, fill='#ffffff')
            
            # Adicionar subtítulo
            subtitle = "Mistérios do Brasil"
            bbox = draw.textbbox((0, 0), subtitle, font=font)
            sub_width = bbox[2] - bbox[0]
            sub_x = (1920 - sub_width) // 2
            sub_y = y + text_height + 20
            
            draw.text((sub_x+2, sub_y+2), subtitle, font=font, fill='#000000')
            draw.text((sub_x, sub_y), subtitle, font=font, fill='#ff6b6b')
            
            img.save(output_path)
            logger.info(f"✅ Imagem de intro criada: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Erro ao criar imagem de intro: {e}")
            # Criar imagem placeholder simples
            img = Image.new('RGB', (1920, 1080), color='#1a1a2e')
            img.save(output_path)
            return output_path
    
    def prepare_images(self, images_dir: Path, duration_per_image: float = 5.0) -> List[Path]:
        """Prepara imagens para o vídeo"""
        prepared_images = []
        
        # Procurar por imagens
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif']:
            image_files.extend(images_dir.glob(ext))
        
        if not image_files:
            logger.warning("Nenhuma imagem encontrada, criando placeholders")
            # Criar imagens placeholder
            for i in range(3):
                placeholder_path = self.temp_dir / f"placeholder_{i}.jpg"
                self.create_placeholder_image(f"Imagem {i+1}", placeholder_path)
                prepared_images.append(placeholder_path)
        else:
            # Processar imagens existentes
            for img_path in image_files[:10]:  # Máximo 10 imagens
                try:
                    processed_path = self.temp_dir / f"processed_{img_path.name}"
                    self.resize_image(img_path, processed_path)
                    prepared_images.append(processed_path)
                except Exception as e:
                    logger.error(f"Erro ao processar {img_path}: {e}")
        
        logger.info(f"✅ {len(prepared_images)} imagens preparadas")
        return prepared_images
    
    def resize_image(self, input_path: Path, output_path: Path):
        """Redimensiona imagem para o formato do vídeo"""
        try:
            with Image.open(input_path) as img:
                # Converter para RGB se necessário
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Redimensionar mantendo proporção
                img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                
                # Criar nova imagem com fundo preto
                new_img = Image.new('RGB', (1920, 1080), (0, 0, 0))
                
                # Centralizar imagem redimensionada
                x = (1920 - img.width) // 2
                y = (1080 - img.height) // 2
                new_img.paste(img, (x, y))
                
                new_img.save(output_path, 'JPEG', quality=95)
                
        except Exception as e:
            logger.error(f"Erro ao redimensionar imagem: {e}")
            # Criar placeholder em caso de erro
            self.create_placeholder_image("Erro na imagem", output_path)
    
    def create_placeholder_image(self, text: str, output_path: Path):
        """Cria imagem placeholder"""
        img = Image.new('RGB', (1920, 1080), color='#2c3e50')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (1920 - text_width) // 2
        y = (1080 - text_height) // 2
        
        draw.text((x, y), text, font=font, fill='white')
        img.save(output_path)
    
    def assemble_video(self, output_dir: Path) -> bool:
        """Monta o vídeo final"""
        logger.info("🎬 Iniciando montagem do vídeo...")
        
        try:
            # Verificar arquivos necessários
            audio_file = None
            for ext in ['*.mp3', '*.wav', '*.m4a']:
                audio_files = list(output_dir.glob(ext))
                if audio_files:
                    audio_file = audio_files[0]
                    break
            
            if not audio_file:
                logger.error("Arquivo de áudio não encontrado")
                return False
            
            # Preparar imagens
            images_dir = output_dir / "images"
            if not images_dir.exists():
                images_dir = output_dir
            
            images = self.prepare_images(images_dir)
            
            if not self.ffmpeg_available:
                logger.warning("FFmpeg não disponível. Criando vídeo simulado.")
                return self._create_mock_video(output_dir, audio_file)
            
            # Usar FFmpeg para criar vídeo
            return self._create_video_with_ffmpeg(output_dir, images, audio_file)
            
        except Exception as e:
            logger.error(f"Erro na montagem: {e}")
            return False
    
    def _create_video_with_ffmpeg(self, output_dir: Path, images: List[Path], audio_file: Path) -> bool:
        """Cria vídeo usando FFmpeg"""
        try:
            video_output = output_dir / "video_final.mp4"
            
            # Criar lista de imagens para FFmpeg
            image_list_file = self.temp_dir / "images.txt"
            with open(image_list_file, 'w') as f:
                for img in images:
                    f.write(f"file '{img.absolute()}'\n")
                    f.write("duration 5\n")  # 5 segundos por imagem
            
            # Comando FFmpeg
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(image_list_file),
                '-i', str(audio_file),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                str(video_output)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Vídeo criado com sucesso: {video_output}")
                return True
            else:
                logger.error(f"Erro no FFmpeg: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao criar vídeo com FFmpeg: {e}")
            return False
    
    def _create_mock_video(self, output_dir: Path, audio_file: Path) -> bool:
        """Cria arquivo de informação quando FFmpeg não está disponível"""
        try:
            info_file = output_dir / "video_info.json"
            
            info = {
                "status": "mock_video_created",
                "message": "FFmpeg não disponível. Vídeo seria criado com:",
                "audio_file": str(audio_file),
                "video_duration": "estimado_5min",
                "resolution": "1920x1080",
                "note": "Instale FFmpeg para gerar vídeo real"
            }
            
            with open(info_file, 'w') as f:
                json.dump(info, f, indent=2)
            
            logger.info("✅ Informações do vídeo salvas (modo simulado)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar mock video: {e}")
            return False

def main():
    """Função principal para execução standalone"""
    parser = argparse.ArgumentParser(description='Montagem de Vídeo')
    parser.add_argument('--output-dir', required=True, help='Diretório de trabalho')
    
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    
    assembler = VideoAssembler()
    success = assembler.assemble_video(output_dir)
    
    if success:
        print("✅ Montagem de vídeo concluída")
        return 0
    else:
        print("❌ Erro na montagem do vídeo")
        return 1

if __name__ == "__main__":
    sys.exit(main())
