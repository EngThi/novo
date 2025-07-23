
#!/usr/bin/env python3
"""
Gerador de Roteiros Avançado
Sistema completo para criação de roteiros para vídeos do YouTube
"""

import os
import sys
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

@dataclass
class ScriptSection:
    """Representa uma seção do roteiro"""
    timestamp: str
    title: str
    content: str
    duration: int  # em segundos
    keywords: List[str]
    emotion: str
    visual_cues: List[str]

@dataclass
class VideoScript:
    """Representa um roteiro completo"""
    title: str
    description: str
    total_duration: int
    target_audience: str
    sections: List[ScriptSection]
    tags: List[str]
    thumbnail_description: str

class ScriptGenerator:
    """Gerador avançado de roteiros para YouTube"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Templates de prompts
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict[str, str]:
        """Carrega templates de prompts para diferentes tipos de conteúdo"""
        return {
            'mystery': """
            Crie um roteiro envolvente sobre {topic} com as seguintes características:
            
            ESTRUTURA OBRIGATÓRIA:
            1. [00:00] Hook Inicial (30s) - Desperte curiosidade imediata
            2. [00:30] Apresentação (30s) - Apresente o canal e o tópico
            3. [01:00] Desenvolvimento (4-6 minutos) - Explore o mistério em detalhes
            4. [07:00] Clímax (1 minuto) - Revelação ou teoria principal
            5. [08:00] Conclusão (1 minuto) - Call to action e fechamento
            
            REQUISITOS:
            - Tom: Misterioso, intrigante, mas acessível
            - Duração total: 8-9 minutos
            - Inclua 3-5 palavras-chave relacionadas ao tema
            - Descreva 2-3 momentos visuais marcantes
            - Use linguagem brasileira natural
            
            TÓPICO: {topic}
            """,
            
            'educational': """
            Desenvolva um roteiro educativo sobre {topic} seguindo esta estrutura:
            
            ESTRUTURA:
            1. [00:00] Introdução Cativante (45s)
            2. [00:45] Problema/Questão (1 minuto)
            3. [01:45] Explicação Detalhada (5-6 minutos)
            4. [07:45] Exemplos Práticos (1 minuto)
            5. [08:45] Resumo e Próximos Passos (30s)
            
            CARACTERÍSTICAS:
            - Tom: Educativo mas descontraído
            - Use analogias e exemplos do cotidiano
            - Inclua momentos de interação com o público
            - Duração: 8-10 minutos
            
            TÓPICO: {topic}
            """,
            
            'entertainment': """
            Crie um roteiro divertido sobre {topic} com esta estrutura:
            
            ESTRUTURA:
            1. [00:00] Abertura Energética (20s)
            2. [00:20] Apresentação do Tema (40s)
            3. [01:00] Conteúdo Principal (6-7 minutos)
            4. [08:00] Momento Especial/Surpresa (1 minuto)
            5. [09:00] Despedida e CTA (30s)
            
            ESTILO:
            - Tom: Descontraído, divertido, envolvente
            - Use humor quando apropriado
            - Inclua momentos de suspense ou surpresa
            - Engajamento constante com o público
            
            TÓPICO: {topic}
            """
        }
    
    def generate_script(self, topic: str, script_type: str = 'mystery', 
                       custom_requirements: Optional[str] = None) -> VideoScript:
        """Gera um roteiro completo baseado no tópico e tipo"""
        try:
            logger.info(f"Gerando roteiro sobre: {topic}")
            
            # Selecionar prompt apropriado
            if script_type not in self.prompts:
                script_type = 'mystery'  # Default
            
            prompt_template = self.prompts[script_type]
            
            # Adicionar requisitos customizados se fornecidos
            if custom_requirements:
                prompt_template += f"\n\nREQUISITOS ADICIONAIS:\n{custom_requirements}"
            
            # Gerar roteiro com IA
            prompt = prompt_template.format(topic=topic)
            response = self.model.generate_content(prompt)
            raw_script = response.text
            
            # Processar e estruturar o roteiro
            script = self._parse_script(raw_script, topic)
            
            logger.info(f"✅ Roteiro gerado com sucesso: {script.title}")
            return script
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar roteiro: {e}")
            raise
    
    def _parse_script(self, raw_script: str, topic: str) -> VideoScript:
        """Converte o texto bruto em um objeto VideoScript estruturado"""
        try:
            # Extrair seções usando regex
            sections = self._extract_sections(raw_script)
            
            # Gerar metadados do vídeo
            title = self._extract_title(raw_script, topic)
            description = self._generate_description(sections, topic)
            tags = self._extract_keywords(raw_script)
            thumbnail_desc = self._generate_thumbnail_description(title, sections)
            
            # Calcular duração total
            total_duration = sum(section.duration for section in sections)
            
            return VideoScript(
                title=title,
                description=description,
                total_duration=total_duration,
                target_audience="Jovens e adultos interessados em mistérios e conhecimento",
                sections=sections,
                tags=tags,
                thumbnail_description=thumbnail_desc
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar roteiro: {e}")
            raise
    
    def _extract_sections(self, raw_script: str) -> List[ScriptSection]:
        """Extrai seções do roteiro usando regex"""
        sections = []
        
        # Padrão para encontrar seções com timestamp
        pattern = r'\[(\d{2}:\d{2})\]\s*([^[\n]+)(.*?)(?=\[\d{2}:\d{2}\]|$)'
        matches = re.findall(pattern, raw_script, re.DOTALL)
        
        for i, (timestamp, title, content) in enumerate(matches):
            # Limpar e processar conteúdo
            content = content.strip()
            title = title.strip()
            
            # Calcular duração baseada no próximo timestamp
            duration = self._calculate_section_duration(timestamp, matches, i)
            
            # Extrair palavras-chave da seção
            keywords = self._extract_section_keywords(content)
            
            # Determinar emoção/tom da seção
            emotion = self._determine_emotion(content, title)
            
            # Extrair dicas visuais
            visual_cues = self._extract_visual_cues(content)
            
            section = ScriptSection(
                timestamp=timestamp,
                title=title,
                content=content,
                duration=duration,
                keywords=keywords,
                emotion=emotion,
                visual_cues=visual_cues
            )
            
            sections.append(section)
        
        return sections
    
    def _calculate_section_duration(self, timestamp: str, all_matches: List, index: int) -> int:
        """Calcula a duração de uma seção em segundos"""
        try:
            # Converter timestamp atual para segundos
            current_seconds = self._timestamp_to_seconds(timestamp)
            
            # Se não há próxima seção, assumir 60 segundos
            if index >= len(all_matches) - 1:
                return 60
            
            # Obter próximo timestamp
            next_timestamp = all_matches[index + 1][0]
            next_seconds = self._timestamp_to_seconds(next_timestamp)
            
            return next_seconds - current_seconds
            
        except Exception:
            return 60  # Duração padrão
    
    def _timestamp_to_seconds(self, timestamp: str) -> int:
        """Converte timestamp MM:SS para segundos"""
        try:
            minutes, seconds = map(int, timestamp.split(':'))
            return minutes * 60 + seconds
        except Exception:
            return 0
    
    def _extract_section_keywords(self, content: str) -> List[str]:
        """Extrai palavras-chave importantes da seção"""
        # Palavras a ignorar
        stop_words = {
            'que', 'uma', 'para', 'com', 'por', 'sobre', 'quando', 'onde', 'como',
            'seu', 'sua', 'seus', 'suas', 'este', 'esta', 'estes', 'estas',
            'muito', 'mais', 'mas', 'porque', 'então', 'também', 'ainda'
        }
        
        # Extrair palavras importantes (substantivos e adjetivos)
        words = re.findall(r'\b[A-Za-záâãêéíôõúç]{4,}\b', content.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Retornar as 5 mais relevantes (removendo duplicatas)
        return list(dict.fromkeys(keywords))[:5]
    
    def _determine_emotion(self, content: str, title: str) -> str:
        """Determina a emoção/tom predominante da seção"""
        emotion_keywords = {
            'misterioso': ['mistério', 'enigma', 'secreto', 'oculto', 'desconhecido'],
            'excitante': ['incrível', 'surpreendente', 'fantástico', 'extraordinário'],
            'sombrio': ['morte', 'tragédia', 'perigo', 'medo', 'escuro'],
            'educativo': ['explicação', 'teoria', 'ciência', 'estudo', 'pesquisa'],
            'inspirador': ['superação', 'conquista', 'vitória', 'sucesso', 'esperança']
        }
        
        text = (content + ' ' + title).lower()
        
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                emotion_scores[emotion] = score
        
        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        
        return 'neutro'
    
    def _extract_visual_cues(self, content: str) -> List[str]:
        """Extrai dicas visuais do conteúdo"""
        visual_patterns = [
            r'mostre?\s+([^.!?]+)',
            r'imagem\s+de\s+([^.!?]+)',
            r'vídeo\s+de\s+([^.!?]+)',
            r'visualizar?\s+([^.!?]+)',
            r'cena\s+([^.!?]+)'
        ]
        
        visual_cues = []
        for pattern in visual_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            visual_cues.extend([match.strip() for match in matches])
        
        return visual_cues[:3]  # Máximo 3 dicas visuais por seção
    
    def _extract_title(self, raw_script: str, topic: str) -> str:
        """Extrai ou gera um título para o vídeo"""
        # Procurar por um título explícito no script
        title_patterns = [
            r'título:\s*([^\n]+)',
            r'TÍTULO:\s*([^\n]+)',
            r'^([^[]+?)(?:\[|$)',  # Primeira linha antes de qualquer timestamp
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, raw_script.strip(), re.IGNORECASE | re.MULTILINE)
            if match:
                title = match.group(1).strip()
                if len(title) > 10 and not title.startswith('['):
                    return title
        
        # Se não encontrou, gerar baseado no tópico
        return f"O Mistério de {topic}: Uma História Que Vai Te Surpreender"
    
    def _generate_description(self, sections: List[ScriptSection], topic: str) -> str:
        """Gera descrição do vídeo baseada nas seções"""
        description = f"Explore conosco {topic} neste vídeo fascinante!\n\n"
        description += "🎯 NESTE VÍDEO:\n"
        
        for section in sections[:4]:  # Primeiras 4 seções
            description += f"• {section.timestamp} - {section.title}\n"
        
        description += "\n📱 SIGA-NOS:\n"
        description += "• Instagram: @seucanal\n"
        description += "• Twitter: @seucanal\n"
        description += "\n#mistério #brasil #curiosidades"
        
        return description
    
    def _extract_keywords(self, raw_script: str) -> List[str]:
        """Extrai tags/palavras-chave do script completo"""
        # Extrair palavras importantes
        words = re.findall(r'\b[A-Za-záâãêéíôõúç]{4,}\b', raw_script.lower())
        
        # Filtrar e contar frequência
        word_freq = {}
        stop_words = {
            'que', 'uma', 'para', 'com', 'por', 'sobre', 'quando', 'onde', 'como',
            'muito', 'mais', 'mas', 'porque', 'então', 'também', 'ainda', 'este',
            'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas'
        }
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Retornar as 10 mais frequentes
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def _generate_thumbnail_description(self, title: str, sections: List[ScriptSection]) -> str:
        """Gera descrição para thumbnail baseada no conteúdo"""
        if not sections:
            return "Imagem misteriosa relacionada ao tema"
        
        # Usar a primeira seção ou seção com mais impacto visual
        main_section = sections[0]
        
        description = f"Thumbnail impactante mostrando: {title}. "
        
        if main_section.visual_cues:
            description += f"Elementos visuais: {', '.join(main_section.visual_cues)}. "
        
        description += f"Tom: {main_section.emotion}. Texto grande e legível."
        
        return description
    
    def save_script(self, script: VideoScript, output_dir: Path) -> Dict[str, Path]:
        """Salva o roteiro em múltiplos formatos"""
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            saved_files = {}
            
            # 1. Arquivo JSON estruturado
            json_file = output_dir / "script.json"
            script_dict = {
                'title': script.title,
                'description': script.description,
                'total_duration': script.total_duration,
                'target_audience': script.target_audience,
                'tags': script.tags,
                'thumbnail_description': script.thumbnail_description,
                'sections': [
                    {
                        'timestamp': section.timestamp,
                        'title': section.title,
                        'content': section.content,
                        'duration': section.duration,
                        'keywords': section.keywords,
                        'emotion': section.emotion,
                        'visual_cues': section.visual_cues
                    }
                    for section in script.sections
                ],
                'generated_at': datetime.now().isoformat()
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(script_dict, f, indent=2, ensure_ascii=False)
            saved_files['json'] = json_file
            
            # 2. Arquivo de texto legível
            txt_file = output_dir / "script.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"TÍTULO: {script.title}\n")
                f.write(f"DURAÇÃO: {script.total_duration//60}:{script.total_duration%60:02d}\n")
                f.write(f"PÚBLICO-ALVO: {script.target_audience}\n\n")
                f.write("="*50 + "\n")
                f.write("ROTEIRO\n")
                f.write("="*50 + "\n\n")
                
                for section in script.sections:
                    f.write(f"[{section.timestamp}] {section.title}\n")
                    f.write(f"Duração: {section.duration}s | Tom: {section.emotion}\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"{section.content}\n\n")
                    
                    if section.visual_cues:
                        f.write(f"Dicas visuais: {', '.join(section.visual_cues)}\n")
                    f.write("\n" + "="*50 + "\n\n")
                
                f.write("DESCRIÇÃO DO VÍDEO:\n")
                f.write(script.description)
                f.write(f"\n\nTAGS: {', '.join(script.tags)}")
                f.write(f"\n\nTHUMBNAIL: {script.thumbnail_description}")
            
            saved_files['txt'] = txt_file
            
            # 3. Arquivo para teleprompter
            teleprompter_file = output_dir / "teleprompter.txt"
            with open(teleprompter_file, 'w', encoding='utf-8') as f:
                for section in script.sections:
                    f.write(f"[{section.timestamp}]\n")
                    f.write(f"{section.content}\n\n")
            
            saved_files['teleprompter'] = teleprompter_file
            
            logger.info(f"✅ Roteiro salvo em {output_dir}")
            return saved_files
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar roteiro: {e}")
            raise

def extract_script_sections(script_text: str) -> List[Dict[str, str]]:
    """Função auxiliar para extrair seções do roteiro (compatibilidade)"""
    generator = ScriptGenerator()
    sections_objs = generator._extract_sections(script_text)
    
    return [
        {
            'timestamp': section.timestamp,
            'title': section.title,
            'content': section.content,
            'duration': str(section.duration),
            'emotion': section.emotion
        }
        for section in sections_objs
    ]

def generate_script(topic: str, script_type: str = 'mystery') -> str:
    """Função auxiliar para gerar roteiro (compatibilidade)"""
    generator = ScriptGenerator()
    script = generator.generate_script(topic, script_type)
    
    # Retornar versão em texto
    result = f"TÍTULO: {script.title}\n\n"
    for section in script.sections:
        result += f"[{section.timestamp}] {section.title}\n"
        result += f"{section.content}\n\n"
    
    return result

def main():
    """Função principal para teste"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerador de Roteiros')
    parser.add_argument('--topic', required=True, help='Tópico do vídeo')
    parser.add_argument('--type', default='mystery', choices=['mystery', 'educational', 'entertainment'],
                       help='Tipo de roteiro')
    parser.add_argument('--output-dir', default='output', help='Diretório de saída')
    
    args = parser.parse_args()
    
    try:
        generator = ScriptGenerator()
        script = generator.generate_script(args.topic, args.type)
        saved_files = generator.save_script(script, Path(args.output_dir))
        
        print(f"✅ Roteiro gerado com sucesso!")
        print(f"📝 Título: {script.title}")
        print(f"⏱️ Duração: {script.total_duration//60}:{script.total_duration%60:02d}")
        print(f"📁 Arquivos salvos: {list(saved_files.keys())}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
