# imagen_module.py

import os
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel

def generate_imagen4_images(
    prompts: list[str],
    out_dir: str = "assets/images",
    project: str = None,
    location: str = "us-central1",
    model_name: str = "imagen-4.0-ultra-generate-preview-06-06",
    aspect_ratio: str = "1:1"
):
    """
    Gera imagens via Imagen 4 Ultra (Vertex AI).
    Args:
        prompts: Lista de prompts de texto.
        out_dir: Diretorio para salvar PNGs.
        project: ID do projeto GCP (ou configura ADC).
        location: Região do Vertex AI.
        model_name: ID do modelo Imagen.
        sample_count: Número de variações por prompt.
        aspect_ratio: Razão (ex.: '1:1', '16:9').
    """
    aiplatform.init(project=project, location=location)
    model = ImageGenerationModel.from_pretrained(model_name)

    os.makedirs(out_dir, exist_ok=True)
    out_paths = []

    for idx, prompt in enumerate(prompts, start=1):
        response = model.generate_images(
            prompt=prompt,
            aspect_ratio=aspect_ratio
        )
        for j, img in enumerate(response):
            path = f"{out_dir}/imagen4_{idx}_{j+1}.png"
            img.save(path)
            out_paths.append(path)

    return out_paths
