"""
Sistema de Prompts Profissionais para Automação Horror/Mistério YouTube
Baseado em análise de canais brasileiros de sucesso como AssombradO e Mundo Inverso
"""

import random
from typing import Dict, List

class HorrorPromptSystem:
    """Sistema de prompts otimizado para geração de conteúdo horror/mistério"""
    
    def __init__(self):
        self.brazilian_folklore_elements = [
            "Saci-Pererê", "Curupira", "Boitatá", "Mula-sem-cabeça", 
            "Lobisomem", "Iara", "Caipora", "Corpo-seco", "Chupacabra"
        ]
        
        self.horror_locations_brazil = [
            "Cemitério da Consolação (SP)", "Hospital Psiquiátrico Pedro II (RJ)",
            "Teatro Municipal de São Paulo", "Ilha das Bonecas (Mexico/BR)",
            "Floresta da Tijuca (RJ)", "Serra da Cantareira (SP)",
            "Campos do Jordão", "Ouro Preto (MG)", "Paraty (RJ)"
        ]

# PROMPTS PARA ROTEIROS - NÍVEL PROFISSIONAL
SCRIPT_PROMPTS = {
    'horror_brasileiro': """
    Você é um roteirista especializado em horror brasileiro, com expertise em folclore nacional e narrativas assombradas.
    
    CONTEXTO: Canal de horror brasileiro com 2.7M+ seguidores, estilo similar ao AssombradO.
    
    TAREFA: Criar um roteiro de 6-8 minutos sobre "{tema}" que mantenha o público brasileiro colado na tela.
    
    ESTRUTURA OBRIGATÓRIA:
    1. GANCHO INICIAL (0-20s):
       - Pergunta perturbadora que gera curiosidade imediata
       - Estatística ou fato chocante relacionado ao tema
       - Promessa clara do que será revelado
    
    2. INTRODUÇÃO MISTERIOSA (20s-1min):
       - Contexto histórico ou geográfico brasileiro
       - Estabelecimento da atmosfera sombria
       - Apresentação dos personagens principais
    
    3. DESENVOLVIMENTO CRESCENTE (1min-5min):
       - 3 eventos escalando em intensidade
       - Cada evento mais perturbador que o anterior
       - Uso de elementos do folclore brasileiro quando relevante
       - Testemunhos ou relatos "reais" para autenticidade
    
    4. CLÍMAX ASSUSTADOR (5-6min):
       - Revelação mais chocante da história
       - Momento de maior tensão e medo
       - Reviravolta inesperada se possível
    
    5. CONCLUSÃO IMPACTANTE (6-8min):
       - Desfecho que deixa o público pensando
       - Call-to-action natural para engajamento
       - Gancho para próximos vídeos
    
    ELEMENTOS ESSENCIAIS:
    - Linguagem: Português brasileiro coloquial mas educado
    - Tom: Suspense crescente, misterioso, envolvente
    - Público: Brasileiros 18-45 anos interessados em horror
    - Incluir descrições visuais detalhadas para cada cena
    - Usar elementos culturais brasileiros para identificação
    
    PALAVRAS-CHAVE PARA SEO: {keywords}
    
    FORMATO DE SAÍDA:
    [TEMPO] NARRAÇÃO
    [VISUAL] Descrição detalhada da imagem/cena
    [AUDIO] Efeitos sonoros ou música sugerida
    
    EXEMPLO DE FORMATAÇÃO:
    [00:00-00:15] "Você sabia que no Brasil existem lugares onde até os mais corajosos se recusam a entrar? Hoje vamos descobrir o que aconteceu em {local específico}..."
    [VISUAL] Imagem noturna e atmosférica do local mencionado
    [AUDIO] Som ambiente baixo, música de suspense sutil
    """,
    
    'mystery_investigation': """
    Você é um investigador profissional de mistérios, especializado em casos não resolvidos brasileiros.
    
    CONTEXTO: Canal investigativo estilo documentário, audiência educada interessada em true crime.
    
    TAREFA: Desenvolver investigação sobre "{tema}" seguindo metodologia jornalística profissional.
    
    ESTRUTURA INVESTIGATIVA:
    1. APRESENTAÇÃO DO CASO (0-30s):
       - Fatos básicos: quando, onde, quem
       - Por que este caso é importante/intrigante
       - Promessa de revelações exclusivas
    
    2. CONTEXTO E BACKGROUND (30s-2min):
       - Situação histórica e social
       - Personagens envolvidos
       - Cronologia inicial dos eventos
    
    3. INVESTIGAÇÃO DETALHADA (2min-5min):
       - Evidências analisadas passo a passo
       - Teorias e hipóteses exploradas
       - Entrevistas ou depoimentos (simulados)
       - Análise crítica de cada pista
    
    4. REVELAÇÕES E DESCOBERTAS (5-6min):
       - Informações exclusivas ou pouco conhecidas
       - Conexões surpreendentes
       - Análise de especialistas
    
    5. CONCLUSÃO ANALÍTICA (6-8min):
       - Resumo das evidências
       - Possíveis explicações
       - Questões em aberto
       - Convite para discussão nos comentários
    
    ELEMENTOS INVESTIGATIVOS:
    - Linguagem técnica mas acessível
    - Fontes citadas quando possível
    - Abordagem imparcial e analítica
    - Respeito às vítimas e familiares
    
    PALAVRAS-CHAVE: {keywords}
    
    FORMATO DOCUMENTÁRIO:
    [TEMPO] NARRAÇÃO INVESTIGATIVA
    [VISUAL] Descrição de evidências, mapas, fotos
    [FONTE] Referência ou origem da informação
    """,
    
    'urban_legends': """
    Você é um especialista em folclore urbano brasileiro, contador de histórias com 20+ anos de experiência.
    
    CONTEXTO: Canal focado em lendas urbanas brasileiras, público jovem-adulto fascinado por histórias locais.
    
    TAREFA: Narrar a lenda urbana sobre "{tema}" de forma envolvente e cultural.
    
    ESTRUTURA NARRATIVA:
    1. INTRODUÇÃO CULTURAL (0-45s):
       - Origem regional da lenda
       - Contexto histórico ou social
       - Por que esta lenda persiste
    
    2. A LENDA ORIGINAL (45s-3min):
       - Versão tradicional da história
       - Elementos folclóricos importantes
       - Significado cultural
    
    3. VARIAÇÕES MODERNAS (3min-5min):
       - Como a lenda evoluiu
       - Adaptações urbanas contemporâneas
       - Relatos "atuais" da lenda
    
    4. ANÁLISE CULTURAL (5-6min):
       - O que a lenda representa
       - Medos e ansiedades sociais
       - Função da lenda na comunidade
    
    5. IMPACTO ATUAL (6-8min):
       - Influência na cultura pop
       - Referências em outros meios
       - Continuidade da tradição
    
    ELEMENTOS CULTURAIS:
    - Respeito à tradição oral
    - Conexão com identidade brasileira
    - Linguagem que honra a origem
    - Explicações de regionalismos
    
    PALAVRAS-CHAVE: {keywords}
    
    FORMATO TRADICIONAL:
    [TEMPO] NARRAÇÃO FOLCLÓRICA
    [VISUAL] Representação artística da lenda
    [CULTURAL] Explicação de elementos específicos
    """
}

# PROMPTS PARA THUMBNAILS - OTIMIZADOS PARA HORROR
THUMBNAIL_PROMPTS = {
    'dramatic_brazilian': """
    Crie uma thumbnail profissional de YouTube para vídeo de horror brasileiro sobre "{title}".
    
    ESPECIFICAÇÕES TÉCNICAS:
    - Resolução: 1280x720 pixels
    - Formato: 16:9
    - Qualidade: 4K, hiper-realista
    - Estilo: Cinematográfico profissional
    
    ELEMENTOS VISUAIS OBRIGATÓRIOS:
    - Pessoa brasileira com expressão de susto/terror autêntico
    - Iluminação dramática com contrastes altos
    - Cores vibrantes: vermelho sangue, amarelo elétrico, preto profundo
    - Elementos de terror sutis no fundo
    
    COMPOSIÇÃO:
    - Regra dos terços aplicada
    - Rosto ocupando 1/3 da imagem
    - Expressão facial claramente visível
    - Olhar direcionado para a "ameaça"
    
    TEXTO NA THUMBNAIL:
    - Máximo 4 palavras em português
    - Fonte: Arial Black ou similar
    - Tamanho: Grande e legível no mobile
    - Cor: Branco com contorno preto grosso
    - Posição: Não sobrepor o rosto
    
    ATMOSFERA:
    - Tensão palpável na imagem
    - Elementos sobrenaturais sutis
    - Qualidade de filme de terror profissional
    - Apelo emocional imediato
    
    EVITAR:
    - Imagens genéricas ou clichês
    - Texto muito pequeno
    - Cores que não contrastam
    - Elementos confusos demais
    """,
    
    'atmospheric_dark': """
    Desenvolva uma thumbnail atmosférica para YouTube sobre "{title}".
    
    CONCEITO VISUAL:
    - Estilo: Gótico brasileiro contemporâneo
    - Mood: Mistério profundo, melancolia assombrada
    - Inspiração: Filmes de Guillermo del Toro
    
    PALETA DE CORES:
    - Primária: Azul profundo (#001122)
    - Secundária: Roxo escuro (#330066)
    - Acentos: Dourado antigo (#FFD700)
    - Contraste: Branco lunar (#FFFFFF)
    
    ELEMENTOS ARTÍSTICOS:
    - Silhuetas misteriosas
    - Neblina ou névoa sutil
    - Arquitetura brasileira colonial
    - Elementos sobrenaturais integrados
    
    COMPOSIÇÃO ARTÍSTICA:
    - Perspectiva em ponto de fuga
    - Iluminação lateral dramática
    - Sombras expressivas
    - Detalhes em alta definição
    
    TEXTO INTEGRADO:
    - Tipografia: Serif elegante
    - Efeito: Brilho sutil
    - Integração: Parte da composição
    - Legibilidade: Prioridade absoluta
    """,
    
    'documentary_style': """
    Crie thumbnail estilo documentário investigativo para "{title}".
    
    ABORDAGEM JORNALÍSTICA:
    - Estilo: Sério, profissional, confiável
    - Referência: Documentários do History Channel
    - Credibilidade: Máxima prioridade
    
    ELEMENTOS DOCUMENTÁRIOS:
    - Fotografias "reais" ou arquivos
    - Mapas ou diagramas
    - Textos informativos
    - Selo de "baseado em fatos reais"
    
    COMPOSIÇÃO INFORMATIVA:
    - Layout organizado
    - Hierarquia visual clara
    - Informações facilmente digeríveis
    - Aparência profissional
    
    PALETA CONFIÁVEL:
    - Cores neutras e sérias
    - Azul confiança (#003366)
    - Cinza profissional (#666666)
    - Vermelho para alertas (#CC0000)
    
    CREDIBILIDADE VISUAL:
    - Qualidade de produção alta
    - Sem elementos sensacionalistas
    - Foco na informação
    - Aparência de mídia séria
    """
}

# PROMPTS PARA ÁUDIO/NARRAÇÃO
AUDIO_PROMPTS = {
    'suspenseful_narration': """
    Configuração de voz para narração de suspense em português brasileiro:
    
    CARACTERÍSTICAS VOCAIS:
    - Tom: Grave e envolvente
    - Ritmo: Pausado com acelerações estratégicas
    - Emoção: Mistério crescente
    - Dicção: Clara e articulada
    
    TÉCNICAS NARRATIVAS:
    - Pausas dramáticas antes de revelações
    - Intensificação gradual do tom
    - Sussurros para momentos íntimos
    - Elevação para clímax
    
    CONFIGURAÇÃO TÉCNICA:
    - Velocidade: 0.9x (ligeiramente mais lento)
    - Pitch: -2 semitones (mais grave)
    - Emphasis: Médio
    - Stability: Alto
    
    PONTOS DE ENFASE:
    - Números e estatísticas
    - Nomes de lugares
    - Momentos de revelação
    - Perguntas retóricas
    """
}

# PROMPTS PARA OTIMIZAÇÃO DE PERFORMANCE
OPTIMIZATION_PROMPTS = {
    'title_optimization': """
    Gere 5 títulos otimizados para YouTube sobre "{topic}" seguindo as melhores práticas:
    
    CRITÉRIOS DE OTIMIZAÇÃO:
    - Máximo 60 caracteres
    - Palavras-chave no início
    - Gatilhos emocionais
    - Números quando relevante
    - Português brasileiro coloquial
    
    GATILHOS COMPROVADOS:
    - "VOCÊ NÃO VAI ACREDITAR"
    - "CASO REAL"
    - "NUNCA CONTARAM"
    - "DESCOBRIRAM"
    - "ASSUSTADOR"
    
    FORMATO DE SAÍDA:
    1. [TÍTULO] - [JUSTIFICATIVA]
    2. [TÍTULO] - [JUSTIFICATIVA]
    3. [TÍTULO] - [JUSTIFICATIVA]
    4. [TÍTULO] - [JUSTIFICATIVA]
    5. [TÍTULO] - [JUSTIFICATIVA]
    
    EXEMPLO:
    1. "CASO REAL: O Que Descobriram Nesta Casa Assombrada" - Combina gatilho emocional + curiosidade + credibilidade
    """,
    
    'description_seo': """
    Crie descrição SEO otimizada para vídeo sobre "{topic}":
    
    ESTRUTURA DA DESCRIÇÃO:
    1. PRIMEIRA LINHA (crítica):
       - Resumo atrativo em 1 frase
       - Principais palavras-chave
       - Gancho para continuar lendo
    
    2. CORPO PRINCIPAL:
       - Contexto do vídeo
       - Principais pontos abordados
       - Palavras-chave distribuídas naturalmente
    
    3. CALL-TO-ACTION:
       - Pedido de curtida/inscrição
       - Convite para comentários
       - Sugestão de próximos vídeos
    
    PALAVRAS-CHAVE PRINCIPAIS: {keywords}
    
    ELEMENTOS OBRIGATÓRIOS:
    - Timestamps dos momentos principais
    - Links para redes sociais
    - Aviso de conteúdo quando necessário
    - Créditos de fontes
    
    LIMITE: 500 palavras
    """
}

# SISTEMA DE ANÁLISE DE PERFORMANCE
PERFORMANCE_ANALYSIS = {
    'ctr_optimization': """
    Analise a performance do vídeo "{video_title}" e sugira melhorias:
    
    MÉTRICAS ATUAIS:
    - CTR: {ctr}%
    - Visualizações: {views}
    - Retenção: {retention}%
    - Engajamento: {engagement}%
    
    BENCHMARKS PARA HORROR:
    - CTR ideal: 6-12%
    - Retenção ideal: 45-60%
    - Engajamento ideal: 3-8%
    
    ANÁLISE AUTOMÁTICA:
    Se CTR < 6%: Problema no título/thumbnail
    Se Retenção < 45%: Problema no conteúdo/ritmo
    Se Engajamento < 3%: Problema na conexão com audiência
    
    SUGESTÕES ESPECÍFICAS:
    [Baseadas nas métricas atuais]
    """,
    
    'audience_retention': """
    Analise a retenção de audiência e identifique melhorias:
    
    PONTOS DE ANÁLISE:
    - Primeiros 15 segundos (críticos)
    - Meio do vídeo (manutenção)
    - Últimos 30 segundos (call-to-action)
    
    PADRÕES IDENTIFICADOS:
    - Quedas bruscas (pontos problemáticos)
    - Picos de interesse (replicar)
    - Padrão geral de retenção
    
    AÇÕES CORRETIVAS:
    - Ajustar ritmo narrativo
    - Melhorar ganchos
    - Otimizar transições
    - Reduzir momentos lentos
    """
}

# FUNÇÃO PARA GERAR PROMPTS PERSONALIZADOS
def generate_custom_prompt(category: str, theme: str, keywords: List[str] = None) -> str:
    """
    Gera prompt personalizado baseado na categoria e tema
    """
    if keywords is None:
        keywords = []
    
    prompt_template = SCRIPT_PROMPTS.get(category, SCRIPT_PROMPTS['horror_brasileiro'])
    
    # Personalização baseada no tema
    if 'folclore' in theme.lower():
        prompt_template = SCRIPT_PROMPTS['urban_legends']
    elif 'crime' in theme.lower():
        prompt_template = SCRIPT_PROMPTS['mystery_investigation']
    
    # Substituição de variáveis
    custom_prompt = prompt_template.format(
        tema=theme,
        keywords=', '.join(keywords) if keywords else 'horror, mistério, brasil'
    )
    
    return custom_prompt

# SISTEMA DE VALIDAÇÃO DE QUALIDADE
def validate_script_quality(script: str) -> Dict:
    """
    Valida a qualidade do roteiro gerado
    """
    quality_metrics = {
        'word_count': len(script.split()),
        'has_hook': 'você' in script.lower()[:200],
        'has_conclusion': any(word in script.lower()[-300:] for word in ['conclusão', 'fim', 'final']),
        'reading_time': len(script.split()) / 150,  # palavras por minuto
        'engagement_words': sum(1 for word in ['você', 'imagine', 'descobrir', 'revelar'] if word in script.lower()),
        'quality_score': 0
    }
    
    # Cálculo do score de qualidade
    score = 0
    if quality_metrics['word_count'] > 800: score += 25
    if quality_metrics['has_hook']: score += 25
    if quality_metrics['has_conclusion']: score += 25
    if quality_metrics['engagement_words'] > 5: score += 25
    
    quality_metrics['quality_score'] = score
    
    return quality_metrics

# EXPORTAR SISTEMA COMPLETO
__all__ = [
    'HorrorPromptSystem',
    'SCRIPT_PROMPTS',
    'THUMBNAIL_PROMPTS', 
    'AUDIO_PROMPTS',
    'OPTIMIZATION_PROMPTS',
    'PERFORMANCE_ANALYSIS',
    'generate_custom_prompt',
    'validate_script_quality'
]
