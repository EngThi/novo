import os
import json
import argparse
import logging
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_script(topic, output_dir):
    """Gera um roteiro detalhado para o tópico usando Gemini"""
    try:
        # Configurar Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("Chave API do Gemini não encontrada no arquivo .env")
            return None
            
        genai.configure(api_key=api_key)
        
        # Criar prompt para o Gemini
        prompt = f"""
        Crie um roteiro detalhado para um vídeo sobre: "{topic['title']}"
        
        Descrição do tópico: {topic.get('description', '')}
        
        O roteiro deve seguir esta estrutura:
        1. Introdução cativante (15-20 segundos)
        2. Apresentação do tema principal (30 segundos)
        3. Desenvolvimento do conteúdo com 3-5 pontos principais (2-3 minutos)
        4. Conclusão com chamada para ação (15-20 segundos)
        
        Inclua timestamps aproximados no formato [MM:SS] para cada seção.
        Forneça diretrizes para imagens/visuais em cada seção entre parênteses.
        O roteiro deve ter um tom conversacional e envolvente.
        """
        
        # Gerar roteiro com o Gemini
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        
        # Processar o roteiro para extrair timestamps
        raw_script = response.text.strip()
        
        # Criar a estrutura do roteiro
        script_data = {
            "topic": topic['title'],
            "description": topic.get('description', ''),
            "raw_script": raw_script,
            "sections": extract_script_sections(raw_script)
        }

        # Gerar também os segmentos para o processamento de imagem
        segments = generate_segments_from_script(script_data)
        segments_file = output_dir / "segments.json"
        with open(segments_file, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)
        
        # Criar diretórios de assets no output
        assets_dir = output_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Salvar o roteiro
        script_file = output_dir / "script.json"
        with open(script_file, "w", encoding="utf-8") as f:
            json.dump(script_data, f, ensure_ascii=False, indent=2)
        
        # Também salvar como texto para fácil leitura
        text_file = output_dir / "script.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(f"# ROTEIRO: {topic['title']}\n\n")
            f.write(raw_script)
        
        logger.info(f"Roteiro gerado com sucesso e salvo em {script_file}")
        return script_data
        
    except Exception as e:
        logger.error(f"Erro ao gerar roteiro com Gemini: {e}")
        return None

def extract_script_sections(raw_script):
    """Extrai seções e timestamps do roteiro"""
    lines = raw_script.split('\n')
    sections = []
    current_section = None
    current_text = []
    
    for line in lines:
        # Buscar padrões de timestamp como [00:15], [1:30], etc.
        import re
        timestamp_match = re.search(r'\[(\d+:\d+)\]', line)
        
        # Se encontrou um timestamp, pode ser o início de uma nova seção
        if timestamp_match:
            # Salvar seção anterior se existir
            if current_section:
                current_section["text"] = "\n".join(current_text)
                sections.append(current_section)
                current_text = []
            
            # Iniciar nova seção
            timestamp_str = timestamp_match.group(1)
            minutes, seconds = map(int, timestamp_str.split(':'))
            timestamp_seconds = minutes * 60 + seconds
            
            # Tentar extrair o título da seção
            title = line.replace(timestamp_match.group(0), '').strip()
            # Se o título estiver vazio ou for apenas pontuação, use um genérico
            if not title or title in [':', '-', '.']:
                title = f"Seção {len(sections) + 1}"
            
            current_section = {
                "title": title,
                "timestamp": timestamp_str,
                "timestamp_seconds": timestamp_seconds,
                "text": ""
            }
            
            # Verificar se há instruções de imagem
            image_match = re.search(r'\((.*?)\)', line)
            if image_match:
                current_section["image_guidance"] = image_match.group(1)
        
        # Se já temos uma seção atual, adicione esta linha ao texto
        elif current_section is not None:
            current_text.append(line)
    
    # Adicionar a última seção se existir
    if current_section:
        current_section["text"] = "\n".join(current_text)
        sections.append(current_section)
    
    return sections

def generate_segments_from_script(script_data):
    """Gera segmentos para processamento de imagem a partir do roteiro"""
    segments = []

    for i, section in enumerate(script_data.get("sections", [])):
        # Extrair prompt de imagem das diretrizes
        image_prompt = section.get("image_guidance", "")
        if not image_prompt:
            # Gerar prompt baseado no texto
            text_words = section.get("text", "").split()[:10]
            image_prompt = " ".join(text_words)

        segment = {
            "id": i,
            "title": section.get("title", f"Segmento {i+1}"),
            "text": section.get("text", ""),
            "timestamp": section.get("timestamp", "00:00"),
            "timestamp_seconds": section.get("timestamp_seconds", 0),
            "image_prompt": image_prompt,
            "image_file": ""  # Será preenchido pelo image_processor
        }

        segments.append(segment)

    return segments

def main():
    """Função principal do gerador de roteiro"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Gera roteiro para vídeo')
    parser.add_argument('--output-dir', type=str, required=True, 
                        help='Diretório para salvar o roteiro')
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    
    # Verificar se o diretório existe
    if not output_dir.exists():
        logger.error(f"Diretório de output não existe: {output_dir}")
        return
    
    # Carregar ideias de conteúdo
    content_file = output_dir / "content_ideas.json"
    if not content_file.exists():
        logger.error(f"Arquivo de ideias de conteúdo não encontrado: {content_file}")
        return
    
    with open(content_file, "r", encoding="utf-8") as f:
        content_data = json.load(f)
    
    # Pegar a primeira ideia (melhor pontuada)
    if len(content_data["topic_ideas"]) > 0:
        selected_topic = content_data["topic_ideas"][0]
        logger.info(f"Gerando roteiro para o tópico: {selected_topic['title']}")
        generate_script(selected_topic, output_dir)
    else:
        logger.error("Nenhuma ideia de tópico encontrada")

if __name__ == "__main__":
    main()