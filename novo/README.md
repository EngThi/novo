
# 🎬 Pipeline de Automação de Vídeos - Versão Otimizada

Sistema completo de automação para criação de vídeos, desde a descoberta de conteúdo até upload no Google Drive.

## 🚀 Funcionalidades

### 🔍 **Descoberta Inteligente de Conteúdo**
- Análise de tendências do YouTube e Google Trends
- Geração de ideias com IA (Gemini)
- Scoring automático de relevância

### 📝 **Geração de Roteiros**
- Roteiros estruturados com timestamps
- Diretrizes para imagens automáticas
- Segmentação inteligente de conteúdo

### 🎙️ **Narração Automática**
- Google Cloud Text-to-Speech
- Fallback para TTS local
- Voz em português brasileiro

### 🖼️ **Processamento de Imagens**
- Integração com Unsplash/Pexels
- Geração de placeholders automáticos
- Prompts inteligentes baseados no roteiro

### 🎞️ **Montagem de Vídeo**
- Sincronização automática áudio/imagem
- Intro e outro personalizados
- Transições suaves

### ☁️ **Upload Automático**
- Google Drive com estrutura organizada
- Metadados completos
- URLs de compartilhamento

## 📋 Pré-requisitos

- Python 3.9+
- Conta Google Cloud
- APIs configuradas (Gemini, Google Cloud)

## 🛠️ Instalação

### 1. Setup Inicial
```bash
# Executar script de configuração
chmod +x setup.sh
./setup.sh
```

### 2. Configurar Credenciais

**Google Cloud Console:**
1. Crie/selecione projeto
2. Ative APIs: Drive, Text-to-Speech, Sheets
3. Crie credenciais (Service Account ou OAuth)
4. Baixe como `google-drive-credentials.json`

**Configurar .env:**
```bash
cp .env.example .env
# Edite .env com suas chaves de API
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

## 🎯 Uso

### Execução Completa
```bash
python pipeline_integrado.py
```

### Execução Agendada
```bash
python pipeline_integrado.py --schedule
```

### Módulos Individuais
```bash
# Descoberta de conteúdo
python youtube_automation/content_discovery.py --output-dir output/test

# Geração de roteiro
python youtube_automation/script_generator.py --output-dir output/test

# Processamento de imagens
python youtube_automation/image_processor.py --output-dir output/test

# Montagem de vídeo
python youtube_automation/video_assembler.py --output-dir output/test

# Upload para Drive
python drive_uploader.py --input-dir output/test
```

## 🧪 Testes

```bash
# Executar todos os testes
python test_pipeline.py

# Testes específicos
python -m pytest test_pipeline.py::TestPipeline::test_content_discovery -v
```

## 📊 Dashboard (Opcional)

```bash
python utils/dashboard/app.py
```

Acesse: http://localhost:5000

## 📁 Estrutura do Projeto

```
novo/
├── youtube_automation/          # Módulos principais
│   ├── content_discovery.py     # Descoberta de conteúdo
│   ├── script_generator.py      # Geração de roteiros
│   ├── narration_generator.py   # Síntese de voz
│   ├── image_processor.py       # Processamento de imagens
│   └── video_assembler.py       # Montagem final
├── utils/                       # Utilitários
│   ├── dashboard/               # Interface web
│   └── sheets_manager.py        # Integração Sheets
├── drive_uploader.py            # Sistema de upload
├── pipeline_integrado.py       # Orquestrador principal
├── test_pipeline.py            # Testes automatizados
└── setup.sh                    # Script de configuração
```

## 🔧 Configuração Avançada

### Planilha de Tracking
Configure `SHEETS_TRACKING_ID` no .env para tracking automático de projetos.

### APIs Opcionais
- **Unsplash/Pexels**: Imagens de qualidade
- **ElevenLabs**: Narração premium
- **YouTube API**: Análise de tendências

### Customização
Edite `youtube_automation/config/prompts.py` para personalizar prompts da IA.

## 🚨 Troubleshooting

### Erro de Autenticação Google
```bash
# Remover tokens antigos
rm token.json
# Re-executar para nova autenticação
python pipeline_integrado.py
```

### Erro de Dependências
```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Erro de Memória (MoviePy)
```bash
# Configurar variável de ambiente
export IMAGEIO_FFMPEG_EXE=/usr/bin/ffmpeg
```

## 📈 Melhorias Futuras

- [ ] Integração com YouTube API para upload direto
- [ ] Suporte a múltiplos idiomas
- [ ] Interface web completa
- [ ] Análise de performance automática
- [ ] Integração com redes sociais

## 🤝 Contribuição

1. Fork do projeto
2. Crie branch para feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para branch (`git push origin feature/NovaFuncionalidade`)
5. Abra Pull Request

## 📄 Licença

Este projeto é licenciado sob MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

- 📧 Email: seu-email@dominio.com
- 💬 Issues: [GitHub Issues](https://github.com/seu-usuario/projeto/issues)
- 📚 Wiki: [Documentação Detalhada](https://github.com/seu-usuario/projeto/wiki)

---

⭐ **Se este projeto foi útil, considere dar uma estrela!**
