from typing import Dict
import google.generativeai as genai

class VideoData:
    def __init__(self):
        self.title = ""
        self.script = ""
        self.scenes = []

class CreativeModule:
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.gemini_client = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_script(self, trend_data: Dict) -> VideoData:
        """
        Gera roteiro otimizado com Gemini 2.0 Flash (gratuito)
        """
        prompt = f"""
        Crie um roteiro de vídeo de 6-7 minutos em português brasileiro sobre "{trend_data['title']}" 
        para canal de horror/mistério no YouTube.

        ESTRUTURA OBRIGATÓRIA:
        1. GANCHO (0-15s): Pergunta intrigante
        2. INTRODUÇÃO (15-45s): Contexto do mistério
        3. DESENVOLVIMENTO (45s-5min): 3 eventos escalando suspense
        4. CLÍMAX (5-6min): Revelação assustadora
        5. CONCLUSÃO (6-7min): Desfecho + call-to-action

        ESPECIFICAÇÕES:
        - Linguagem: Português brasileiro coloquial
        - Tom: Suspense, mistério, envolvente
        - Público: Jovens adultos brasileiros
        - Incluir descrições visuais para cada seção
        - Palavras-chave: {', '.join(trend_data.get('keywords', []))}
        
        FORMATO DE SAÍDA:
        Para cada seção: [TEMPO] NARRAÇÃO + [VISUAL] descrição
        """
        
        response = self.gemini_client.generate_content(
            prompt,
            generation_config={
                "temperature": 0.8,
                "top_p": 0.95,
                "max_output_tokens": 2048
            }
        )
        
        video_data = VideoData()
        video_data.title = f"{trend_data['title'].upper()}: O MISTÉRIO REVELADO"
        video_data.script = response.text
        video_data.scenes = self._extract_visual_descriptions(response.text)
        
        return video_data
    
    def _extract_visual_descriptions(self, text: str) -> list:
        # Extração simples de cenas do texto gerado
        return text.split("\n\n")[:5]
