import json
import logging
import time
from typing import List, Dict

# ---------------------------------------------------------------------------
# Estrutura de dados para representar o vídeo
# ---------------------------------------------------------------------------
class VideoData:
    def __init__(self, title: str, scenes: List[str], audio_path: str):
        self.title = title
        self.scenes = scenes
        self.audio_path = audio_path

# ---------------------------------------------------------------------------
# Módulo de montagem de vídeo
# ---------------------------------------------------------------------------
class VideoAssemblyModule:
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.video_config = {
            "size": (1920, 1080),   # Resolução Full HD
            "fps": 30,              # Quadros por segundo
            "audio_codec": "aac",   # Codec de áudio
            "output_format": ".mp4" # Extensão de saída
        }
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def assemble_video_moviepy(self, video_data: VideoData, assets: Dict, output_dir: str) -> str:
        """
        Monta um vídeo combinando imagens, áudio e título.
        """
        # Imports sob demanda
        from moviepy import (
            VideoFileClip,
            AudioFileClip,
            ImageClip,
            CompositeVideoClip,
            TextClip,
            concatenate_videoclips,
            ColorClip
        )
        from moviepy.video.fx.FadeIn import FadeIn
        from moviepy.video.fx.FadeOut import FadeOut

        logging.info("Iniciando a montagem do vídeo com MoviePy...")

        # -------------------------------------------------------------------
        # Carregar áudio
        # -------------------------------------------------------------------
        audio_clip_path = assets.get("audio_path") or video_data.audio_path
        if not audio_clip_path:
            raise ValueError("Caminho do áudio é obrigatório para a montagem.")
        try:
            audio_clip = AudioFileClip(audio_clip_path)
            total_duration = audio_clip.duration
        except Exception as e:
            logging.error(f"Erro ao carregar áudio '{audio_clip_path}': {e}")
            raise

        # -------------------------------------------------------------------
        # Criar clipes de imagem
        # -------------------------------------------------------------------
        image_paths = assets.get("image_paths", [])
        num_scenes = len(video_data.scenes) if video_data.scenes else len(image_paths)

        if not image_paths:
            logging.warning("Nenhuma imagem fornecida; usando clipe preto.")
            black = ColorClip(self.video_config["size"], color=(0, 0, 0),
                              duration=total_duration)
            video_clips = [black]
        else:
            scene_duration = total_duration / max(1, num_scenes)
            video_clips = []
            for i, img_path in enumerate(image_paths[:num_scenes]):
                try:
                    img = (
                        ImageClip(img_path)
                        .with_duration(scene_duration)
                        .resized(height=self.video_config["size"][1])
                        .with_position("center")
                    )
                    # zoom sutil
                    img = img.resized(lambda t: 1 + 0.02 * (t / scene_duration))
                    # transições
                    img = img.with_effects([FadeIn(0.5)])
                    if i < num_scenes - 1:
                        img = img.with_effects([FadeOut(0.5)])
                    img = img.with_start(i * scene_duration)
                    video_clips.append(img)
                except Exception as e:
                    logging.error(f"Erro ao processar imagem '{img_path}': {e}")

        # -------------------------------------------------------------------
        # Compor e ajustar duração
        # -------------------------------------------------------------------
        if not video_clips:
            raise RuntimeError("Nenhum clipe criado.")
        final_base = concatenate_videoclips(video_clips, method="compose")
        if final_base.duration < total_duration:
            extra = ColorClip(self.video_config["size"], color=(0, 0, 0),
                              duration=total_duration - final_base.duration)
            final_base = concatenate_videoclips([final_base, extra], method="compose")
        else:
            final_base = final_base.with_duration(total_duration)

        final_video = final_base.with_audio(audio_clip)

        # -------------------------------------------------------------------
        # Título opcional
        # -------------------------------------------------------------------
        if video_data.title:
            try:
                title = (
                    TextClip(
                        text=video_data.title,
                        font_size=70,
                        color="white",
                        stroke_color="black",
                        stroke_width=2,
                        method="caption",
                        size=self.video_config["size"],
                    )
                    .with_duration(3)
                    .with_position(("center", "top"))
                    .with_effects([FadeIn(0.5), FadeOut(0.5)])
                )
                final_video = CompositeVideoClip([final_video, title])
            except Exception as e:
                logging.error(f"Erro ao adicionar título: {e}")

        # -------------------------------------------------------------------
        # Renderizar
        # -------------------------------------------------------------------
        output_file = f"{output_dir}/output_{int(time.time())}{self.video_config['output_format']}"
        logging.info(f"Renderizando vídeo em: {output_file}")
        try:
            final_video.write_videofile(
                output_file,
                fps=self.video_config["fps"],
                codec="libx264",
                audio_codec=self.video_config["audio_codec"],
                preset="medium",
                threads=4,
            )
            logging.info(f"Vídeo renderizado: {output_file}")
            return output_file
        except Exception as e:
            logging.error(f"Erro na renderização: {e}")
            raise
