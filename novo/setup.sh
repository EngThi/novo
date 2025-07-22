
#!/bin/bash
# Script para configurar a estrutura completa do projeto

echo "=== Configuração do Pipeline de Automação de Vídeos ==="

# Criar estrutura de diretórios
echo "Criando estrutura de pastas..."
mkdir -p data/audio
mkdir -p data/images
mkdir -p data/final
mkdir -p youtube_automation/output
mkdir -p logs

# Verificar se o arquivo requirements.txt existe
if [ ! -f requirements.txt ]; then
    echo "Criando arquivo requirements.txt..."
    cat > requirements.txt << EOL
# Google APIs
google-api-python-client>=2.0.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=0.5.0
google-generativeai>=0.3.0

# IA e processamento
openai>=1.0.0
pillow>=9.0.0
requests>=2.28.0

# Audio/Video
moviepy>=1.0.3
pydub>=0.25.1

# Web e APIs
fastapi>=0.100.0
uvicorn>=0.20.0
jinja2>=3.1.0
python-multipart>=0.0.6

# Utilitários
python-dotenv>=1.0.0
schedule>=1.2.0
psutil>=5.9.0
pathlib>=1.0.1
EOL
fi

# Verificar arquivo .env
if [ ! -f .env ]; then
    echo "Criando arquivo .env a partir do template..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Configure as variáveis no arquivo .env antes de executar o pipeline!"
fi

# Verificar credenciais do Google
if [ ! -f google-drive-credentials.json ]; then
    echo "⚠️  Arquivo google-drive-credentials.json não encontrado!"
    echo "   Baixe suas credenciais do Google Cloud Console e coloque neste diretório."
fi

# Verificar permissões
chmod +x *.py 2>/dev/null || true

echo ""
echo "=== Configuração concluída! ==="
echo ""
echo "Próximos passos:"
echo "1. Configure o arquivo .env com suas chaves de API"
echo "2. Adicione o arquivo google-drive-credentials.json"
echo "3. Execute: pip install -r requirements.txt"
echo "4. Teste o pipeline: python pipeline_integrado.py"
echo "5. Inicie o dashboard: python utils/dashboard/app.py"
echo ""
echo "Para execução agendada, use: python pipeline_integrado.py --schedule"
