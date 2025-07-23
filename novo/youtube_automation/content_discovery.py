
#!/usr/bin/env python3
"""
Sistema Avançado de Descoberta de Conteúdo
Integra múltiplas fontes para descobrir tendências e tópicos relevantes
"""

import os
import sys
import json
import logging
import requests
import argparse
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta
import google.generativeai as genai
from dotenv import load_dotenv

# Configuração
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class ContentDiscovery:
    """Sistema inteligente de descoberta de conteúdo"""
    
    def __init__(self):
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.trending_topics = []
        
        # Tópicos base para quando APIs não estão disponíveis
        self.fallback_topics = [
            "Mistérios não resolvidos do Brasil",
            "Lendas urbanas brasileiras",
            "Casos criminais famosos",
            "Fenômenos paranormais",
            "História oculta do Brasil",
            "Teorias conspiratórias",
            "Lugares assombrados",
            "Desaparecimentos misteriosos"
        ]
    
    def get_youtube_trends(self) -> List[str]:
        """Obtém tendências do YouTube"""
        if not self.youtube_api_key:
            logger.warning("YouTube API key não encontrada, usando tópicos padrão")
            return self.fallback_topics[:3]
        
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'snippet',
                'chart': 'mostPopular',
                'regionCode': 'BR',
                'videoCategoryId': '25',  # Categoria: News & Politics
                'maxResults': 10,
                'key': self.youtube_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                trends = [item['snippet']['title'] for item in data.get('items', [])]
                logger.info(f"✅ {len(trends)} tendências obtidas do YouTube")
                return trends[:5]
            else:
                logger.warning(f"Erro na API do YouTube: {response.status_code}")
                return self.fallback_topics[:3]
                
        except Exception as e:
            logger.error(f"Erro ao obter tendências: {e}")
            return self.fallback_topics[:3]
    
    def analyze_trends_with_gemini(self, trends: List[str]) -> Dict[str, Any]:
        """Analisa tendências usando Gemini AI"""
        if not GEMINI_API_KEY:
            return self._create_fallback_analysis()
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            Analise as seguintes tendências e tópicos populares: {', '.join(trends)}
            
            Com base nessas tendências, sugira 3 tópicos específicos para vídeos sobre mistérios brasileiros que:
            1. Sejam interessantes para o público brasileiro
            2. Tenham potencial viral
            3. Sejam adequados para um canal de mistérios
            
            Para cada tópico, forneça:
            - Título atrativo
            - Descrição em 2-3 frases
            - Palavras-chave relevantes
            - Nível de interesse (1-10)
            
            Retorne em formato JSON.
            """
            
            response = model.generate_content(prompt)
            
            # Extrair JSON da resposta
            content = response.text
            if '```json' in content:
                json_start = content.find('```json') + 7
                json_end = content.find('```', json_start)
                json_content = content[json_start:json_end].strip()
            else:
                json_content = content
            
            try:
                analysis = json.loads(json_content)
                logger.info("✅ Análise de tendências gerada com Gemini")
                return analysis
            except json.JSONDecodeError:
                logger.warning("Resposta do Gemini não está em formato JSON válido")
                return self._create_fallback_analysis()
                
        except Exception as e:
            logger.error(f"Erro na análise com Gemini: {e}")
            return self._create_fallback_analysis()
    
    def _create_fallback_analysis(self) -> Dict[str, Any]:
        """Cria análise padrão quando APIs não estão disponíveis"""
        return {
            "topics": [
                {
                    "title": "O Mistério da Cidade Perdida de Z",
                    "description": "A busca épica do explorador Percy Fawcett pela cidade perdida na Amazônia que custou sua vida e de sua expedição.",
                    "keywords": ["amazonia", "cidade perdida", "exploração", "percy fawcett"],
                    "interest_level": 9
                },
                {
                    "title": "O Caso do Bebê Diabo de São Paulo",
                    "description": "Em 1976, um caso chocou São Paulo: uma criança nasceu com características estranhas e desapareceu misteriosamente.",
                    "keywords": ["são paulo", "paranormal", "nascimento", "mistério urbano"],
                    "interest_level": 8
                },
                {
                    "title": "A Maldição do Ouro de Minas Gerais",
                    "description": "Famílias inteiras desapareceram após encontrar ouro em cavernas. Coincidência ou maldição ancestral?",
                    "keywords": ["minas gerais", "ouro", "maldição", "desaparecimento"],
                    "interest_level": 7
                }
            ],
            "generation_method": "fallback",
            "timestamp": datetime.now().isoformat()
        }
    
    def discover_content(self, output_dir: Path) -> Dict[str, Any]:
        """Processo completo de descoberta de conteúdo"""
        logger.info("🔍 Iniciando descoberta de conteúdo...")
        
        # 1. Obter tendências
        trends = self.get_youtube_trends()
        
        # 2. Analisar com IA
        analysis = self.analyze_trends_with_gemini(trends)
        
        # 3. Selecionar melhor tópico
        topics = analysis.get('topics', [])
        if topics:
            selected_topic = max(topics, key=lambda x: x.get('interest_level', 0))
        else:
            selected_topic = self.fallback_topics[0]
        
        # 4. Criar resultado
        result = {
            "discovered_trends": trends,
            "analysis": analysis,
            "selected_topic": selected_topic,
            "discovery_timestamp": datetime.now().isoformat(),
            "discovery_method": "automated_ai_analysis"
        }
        
        # 5. Salvar resultado
        discovery_file = output_dir / "content_discovery.json"
        with open(discovery_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Descoberta completa! Tópico selecionado: {selected_topic.get('title', selected_topic)}")
        return result

def main():
    """Função principal para execução standalone"""
    parser = argparse.ArgumentParser(description='Descoberta de Conteúdo')
    parser.add_argument('--output-dir', required=True, help='Diretório de saída')
    
    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    
    # Criar diretório com todos os pais necessários
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Diretório de saída criado/verificado: {output_dir}")
    except Exception as e:
        logger.error(f"Erro ao criar diretório {output_dir}: {e}")
        sys.exit(1)
    
    try:
        discovery = ContentDiscovery()
        result = discovery.discover_content(output_dir)
        
        topic_title = "Tópico selecionado"
        if isinstance(result.get('selected_topic'), dict):
            topic_title = result['selected_topic'].get('title', topic_title)
        elif isinstance(result.get('selected_topic'), str):
            topic_title = result['selected_topic']
        
        print(f"✅ Descoberta concluída: {topic_title}")
        return 0
        
    except Exception as e:
        logger.error(f"Erro na descoberta de conteúdo: {e}")
        print(f"❌ Erro na descoberta: {e}")
        return 1

if __name__ == "__main__":
    main()
