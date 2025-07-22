#!/bin/bash
# Script para configurar a estrutura de pastas necessária

# Criar estrutura de diretórios
mkdir -p data/audio
mkdir -p data/images
mkdir -p data/final

echo "Estrutura de pastas criada."

# Verificar se o arquivo requirements.txt existe
if [ ! -f requirements.txt ]; then
    echo "Criando arquivo requirements.txt"
    cat > requirements.txt << EOL
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
openai
pillow
requests
EOL
fi

echo "Configuração concluída!"