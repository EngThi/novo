import os
import json
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import requests
import io

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_placeholder_image(prompt, width=1280, height=720):
    """Gera uma imagem placeholder com o texto do prompt"""
    img = Image.new('RGB', (width, height), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    
    # Usar fonte padrão
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Adicionar texto do prompt
    d.text((width/2, height/2), prompt, fill=(255, 255, 255), anchor="mm", font=font)
    
    # Retornar imagem como bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    return img_byte_arr.getvalue()

def download_unsplash_image(query, width=1280, height=720):
    """Baixa uma imagem do Unsplash com base no query"""
    try:
        # Tentar usar Unsplash API (precisa de API key)
        api_key = os.getenv("UNSPLASH_API_KEY")
        if api_key:
            response = requests.get(
                "https://api.unsplash.com/search/photos",
                headers={"Authorization": f"Client-ID {api_key}"},
                params={"query": query, "per_page": 1, "orientation": "landscape"}
            )

            data = response.json()

            if "results" in data and len(data["results"]) > 0:
                img_url = data["results"][0]["urls"]["regular"]
                img_response = requests.get(img_url, timeout=30)
                if img_response.status_code == 200:
                    return img_response.content

        # Fallback: usar Pexels API se disponível
        pexels_key = os.getenv("PEXELS_API_KEY")
        if pexels_key:
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": pexels_key},
                params={"query": query, "per_page": 1, "orientation": "landscape"}
            )

            data = response.json()
            if "photos" in data and len(data["photos"]) > 0:
                img_url = data["photos"][0]["src"]["large"]
                img_response = requests.get(img_url, timeout=30)
                if img_response.status_code == 200:
                    return img_response.content

        # Fallback final: usar Unsplash Source (sem API key)
        url = f"https://source.unsplash.com/{width}x{height}/?{query.replace(' ', '+')}"
        response = requests.get(url, timeout=30)
        return response.content

    except Exception as e:
        logger.error(f"Erro ao baixar imagem: {e}")
        return None

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Processador de imagens')
    parser.add_argument('--output-dir', type=str, required=True, 
                        help='Diretório para salvar as imagens')
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    
    # Criar diretório para imagens
    images_dir = output_dir / "assets" / "images"
    images_dir.mkdir(exist_ok=True, parents=True)
    
    # Carregar segmentos do roteiro
    segments_file = output_dir / "segments.json"
    if not segments_file.exists():
        logger.error(f"Arquivo de segmentos não encontrado: {segments_file}")
        return
    
    with open(segments_file, "r", encoding="utf-8") as f:
        segments = json.load(f)
    
    logger.info(f"Processando imagens para {len(segments)} segmentos")
    
    # Processar cada segmento
    for i, segment in enumerate(segments):
        # Obter prompt de imagem
        image_prompt = segment.get("image_prompt", "").strip()
        if not image_prompt:
            image_prompt = f"Visual para: {segment.get('text', '')[:50]}"
        
        logger.info(f"Segmento {i+1}: Gerando imagem para '{image_prompt}'")
        
        # Caminho da imagem
        image_path = images_dir / f"segment_{i:02d}.jpg"
        
        # Tentar baixar do Unsplash
        image_data = download_unsplash_image(image_prompt)
        
        # Fallback para placeholder se falhar
        if not image_data:
            logger.warning(f"Usando imagem placeholder para segmento {i+1}")
            image_data = generate_placeholder_image(image_prompt)
        
        # Salvar imagem
        with open(image_path, "wb") as f:
            f.write(image_data)
        
        # Atualizar caminho no segmento
        segment["image_file"] = str(image_path)
    
    # Salvar segmentos atualizados
    with open(segments_file, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Processamento de imagens concluído: {len(segments)} imagens")

if __name__ == "__main__":
    main()