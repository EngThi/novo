from typing import List, Dict
import logging  # Adicionei isso se não estiver presente, para o logger

class IntelligenceModule:
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.logger = logging.getLogger(__name__)
    
    def fetch_trends(self, category="horror") -> List[Dict]:
        """
        Coleta tendências do YouTube otimizando quota (1 unidade/request)
        """
        youtube_service = self.service_manager.get_service('youtube')
        
        # Busca otimizada por região brasileira
        search_params = {
            'part': 'snippet,statistics',
            'chart': 'mostPopular',
            'regionCode': 'BR',
            'videoCategoryId': '24',  # Entretenimento
            'maxResults': 10,
            'q': f'{category} mistério assombrado brasil'
        }
        
        request = youtube_service.videos().list(**search_params)
        response = request.execute()
        
        # Processamento e análise de engagement
        trends = []
        for item in response['items']:
            engagement_rate = self._calculate_engagement_rate(item)
            trends.append({
                'title': item['snippet']['title'],
                'views': int(item['statistics']['viewCount']),
                'engagement_rate': engagement_rate,
                'keywords': self._extract_keywords(item['snippet']['title']),
                'url': f"https://youtu.be/{item['id']}"
            })
        
        # Log automático no Google Sheets
        self.service_manager.log_to_sheet('Intelligence_Raw', trends)
        return sorted(trends, key=lambda x: x['engagement_rate'], reverse=True)
    
    def _calculate_engagement_rate(self, item):
        # Cálculo simples de taxa de engajamento (likes / views)
        views = int(item['statistics'].get('viewCount', 1))
        likes = int(item['statistics'].get('likeCount', 0))
        return (likes / views) * 100 if views > 0 else 0
    
    def _extract_keywords(self, title):
        # Extração básica de palavras-chave do título
        return [word for word in title.lower().split() if len(word) > 3][:5]
