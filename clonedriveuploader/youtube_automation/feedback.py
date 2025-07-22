class FeedbackModule:
    def __init__(self, service_manager):
        self.service_manager = service_manager
    
    def analyze_performance(self, video_id: str) -> Dict:
        """
        Análise completa de performance com sugestões automáticas
        """
        youtube_service = self.service_manager.get_service('youtube')
        
        # Coletar métricas detalhadas
        analytics_request = youtube_service.videos().list(
            part='statistics,snippet',
            id=video_id
        )
        response = analytics_request.execute()
        
        if response['items']:
            stats = response['items'][0]['statistics']
            metrics = {
                'views': int(stats.get('viewCount', 0)),
                'likes': int(stats.get('likeCount', 0)),
                'comments': int(stats.get('commentCount', 0)),
                'shares': int(stats.get('shareCount', 0))
            }
            
            # Calcular KPIs
            engagement_rate = (metrics['likes'] + metrics['comments']) / metrics['views'] * 100
            
            # Análise de performance
            performance_score = self._calculate_performance_score(metrics)
            suggestions = self._generate_optimization_suggestions(metrics)
            
            # A/B Test automático de thumbnails
            if hasattr(self, 'thumbnail_versions'):
                winner = self.test_thumbnail_performance(video_id, self.thumbnail_versions)
                
            return {
                'metrics': metrics,
                'performance_score': performance_score,
                'suggestions': suggestions,
                'engagement_rate': engagement_rate
            }
    
    def _generate_optimization_suggestions(self, metrics: Dict) -> List[str]:
        """
        IA para sugestões de otimização personalizadas
        """
        suggestions = []
        
        if metrics['views'] < 1000:
            suggestions.append("🎯 Melhorar SEO: Adicionar palavras-chave trending nos títulos")
            suggestions.append("📱 Promover em redes sociais: Compartilhar nos Stories")
        
        engagement_rate = (metrics['likes'] + metrics['comments']) / metrics['views'] * 100
        if engagement_rate < 3:
            suggestions.append("💬 Aumentar interação: Adicionar perguntas diretas no vídeo")
            suggestions.append("🎬 Melhorar call-to-action: Pedidos de curtida mais naturais")
        
        return suggestions
