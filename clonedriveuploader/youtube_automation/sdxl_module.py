# sdxl_module.py

import torch
from diffusers import StableDiffusionXLPipeline, StableDiffusionXLImg2ImgPipeline

# Configure dispositivo (GPU preferencial)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def generate_sdxl_images(
    prompts: list[str],
    out_dir: str = "assets/images",
    num_inference_steps: int = 30,
    guidance_scale: float = 7.5,
):
    """
    Gera imagens a partir de prompts usando SDXL.
    Args:
        prompts: Lista de textos para gerar cada imagem.
        out_dir: Pasta de saída para salvar PNGs.
        num_inference_steps: Passos de inferência.
        guidance_scale: Escala de guidance (condicionamento).
    """
    # Carregar modelo base e refiner
    base_pipe = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16, variant="fp16", use_safetensors=True
    ).to(DEVICE)
    refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-refiner-1.0",
        torch_dtype=torch.float16, variant="fp16", use_safetensors=True
    ).to(DEVICE)

    base_pipe.enable_attention_slicing()
    out_paths = []

    for idx, prompt in enumerate(prompts, start=1):
        # Gera imagem bruta
        image = base_pipe(
            prompt=prompt,
            negative_prompt="low quality, blurry",
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps
        ).images[0]

        # Aplica refino para detalhes
        ref_image = refiner(
            image=image,
            prompt=prompt,
            negative_prompt="low quality, blurry",
            guidance_scale=guidance_scale,
            num_inference_steps=int(num_inference_steps/2)
        ).images[0]

        # Salvar
        out_path = f"{out_dir}/sdxl_{idx}.png"
        ref_image.save(out_path)
        out_paths.append(out_path)

    return out_paths
