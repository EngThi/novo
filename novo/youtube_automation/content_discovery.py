import os
import json
import argparse
import datetime
import logging
import requests
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_youtube_trends():
    """Obter tópicos em alta do YouTube via API"""
    try:
        # Esta função pode ser implementada quando você tiver uma chave API do YouTube
        # Por enquanto, retornamos um placeholder
        return ["Tendência YouTube 1", "Tendência YouTube 2", "Tendência YouTube 3"]
    except Exception as e:
        logger.error(f"Erro ao buscar tendências do YouTube: {e}")
        return []

def get_google_trends():
    """Obter tópicos do Google Trends via web scraping ou API"""
    try:
        # Abordagem simples via pytrends ou scraping
        return ["Tendência Google 1", "Tendência Google 2", "Tendência Google 3"]
    except Exception as e:
        logger.error(f"Erro ao buscar tendências do Google: {e}")
        return []

def generate_topic_ideas(trends, num_ideas=5):
    """Gerar ideias de tópicos baseados nas tendências usando Gemini"""
    try:
        # Configurar Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("Chave API do Gemini não encontrada no arquivo .env")
            return []
            
        genai.configure(api_key=api_key)
        
        # Criar prompt para o Gemini
        trends_text = "\n".join(trends)
        prompt = f"""
        Com base nas seguintes tendências:
        
        {trends_text}
        
        Gere {num_ideas} ideias de tópicos para vídeos curtos que sejam atraentes e virais.
        Cada ideia deve:
        1. Ser relevante para o público brasileiro
        2. Ter potencial para engajamento
        3. Ser específica o suficiente para um vídeo de 3-5 minutos
        
        Formate sua resposta como uma lista de ideias, cada uma com um título e uma breve descrição.
        """
        
        # Gerar ideias com o Gemini
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(prompt)
        
        # Processar a resposta
        ideas = []
        lines = response.text.strip().split('\n')
        current_idea = {}
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('- ') or line.startswith('# ') or line.startswith('## ') or line[0].isdigit() and line[1] in ['.', ')']):
                # Salvar ideia anterior se existir
                if current_idea and 'title' in current_idea:
                    ideas.append(current_idea)
                
                # Iniciar nova ideia
                title = line.lstrip('- #0123456789.)').strip()
                current_idea = {'title': title, 'description': ''}
            elif current_idea:
                # Adicionar à descrição
                if 'description' in current_idea and current_idea['description']:
                    current_idea['description'] += ' ' + line
                else:
                    current_idea['description'] = line
        
        # Adicionar a última ideia se existir
        if current_idea and 'title' in current_idea:
            ideas.append(current_idea)
        
        # Limitar ao número desejado
        return ideas[:num_ideas]
        
    except Exception as e:
        logger.error(f"Erro ao gerar ideias com Gemini: {e}")
        return []

def main():
    """Função principal de descoberta de conteúdo"""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Descubra tópicos em alta para conteúdo')
    parser.add_argument('--output-dir', type=str, required=False, 
                        help='Diretório para salvar os resultados')
    args = parser.parse_args()
    
    output_dir = args.output_dir
    if not output_dir:
        output_dir = Path("output") / datetime.datetime.now().strftime("%Y-%m-%d_content")
    else:
        output_dir = Path(output_dir)
    
    # Criar diretório se não existir
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Obter tendências
    logger.info("Buscando tendências do YouTube e Google...")
    youtube_trends = get_youtube_trends()
    google_trends = get_google_trends()
    all_trends = list(set(youtube_trends + google_trends))
    
    # Gerar ideias
    logger.info("Gerando ideias de tópicos com Gemini...")
    topic_ideas = generate_topic_ideas(all_trends)
    
    # Preparar resultado
    result = {
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "trends": all_trends,
        "topic_ideas": topic_ideas
    }
    
    # Salvar resultado
    output_file = output_dir / "content_ideas.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Descoberta de conteúdo concluída! Ideias salvas em {output_file}")
    
    # Exibir algumas ideias geradas
    for i, idea in enumerate(topic_ideas, 1):
        logger.info(f"Ideia #{i}: {idea['title']}")

if __name__ == "__main__":
    main()