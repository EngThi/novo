
#!/bin/bash

echo "🚀 Configurando Pipeline de Automação de Vídeos..."

# Verificar se estamos no diretório correto
if [ ! -f "pipeline_integrado.py" ]; then
    echo "❌ Execute este script no diretório do projeto"
    exit 1
fi

# Criar estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p output
mkdir -p logs
mkdir -p youtube_automation/output
mkdir -p data
mkdir -p temp

# Verificar Python
echo "🐍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+"
    exit 1
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Instale pip"
    exit 1
fi

# Instalar dependências
echo "📦 Instalando dependências..."
pip3 install -r requirements.txt

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚙️ Criando arquivo .env..."
        cp .env.example .env
        echo "✅ Arquivo .env criado. Configure suas credenciais!"
    else
        echo "❌ Arquivo .env.example não encontrado"
        exit 1
    fi
else
    echo "✅ Arquivo .env já existe"
fi

# Verificar credenciais do Google
if [ ! -f "google-drive-credentials.json" ]; then
    echo "⚠️  IMPORTANTE: Adicione o arquivo google-drive-credentials.json"
    echo "   1. Acesse https://console.cloud.google.com/"
    echo "   2. Crie credenciais OAuth 2.0"
    echo "   3. Baixe o arquivo JSON"
    echo "   4. Renomeie para 'google-drive-credentials.json'"
fi

# Verificar FFmpeg (opcional)
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg encontrado - vídeos reais serão gerados"
else
    echo "⚠️  FFmpeg não encontrado - modo simulação ativado"
    echo "   Para instalar: sudo apt-get install ffmpeg"
fi

# Testar importações Python básicas
echo "🧪 Testando dependências Python..."
python3 -c "
import sys
try:
    import google.generativeai as genai
    import googleapiclient.discovery
    import PIL
    import requests
    print('✅ Todas as dependências principais instaladas')
except ImportError as e:
    print(f'❌ Erro na importação: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Erro nas dependências. Execute: pip3 install -r requirements.txt"
    exit 1
fi

# Executar testes básicos
echo "🧪 Executando testes básicos..."
python3 test_pipeline.py

echo ""
echo "🎉 CONFIGURAÇÃO CONCLUÍDA!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Configure suas credenciais no arquivo .env"
echo "2. Adicione google-drive-credentials.json"
echo "3. Execute: python3 pipeline_integrado.py"
echo ""
echo "🆘 SUPORTE:"
echo "- Logs em: logs/"
echo "- Testes: python3 test_pipeline.py"
echo "- Dashboard: python3 utils/dashboard/app.py"
