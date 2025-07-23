
#!/usr/bin/env python3
"""
Script de verificação de ambiente e dependências
Verifica se tudo está configurado corretamente antes de executar o pipeline
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

def check_directories():
    """Verifica e cria diretórios necessários"""
    required_dirs = [
        "output",
        "logs", 
        "youtube_automation",
        "utils",
        "temp",
        "data"
    ]
    
    print("📁 Verificando diretórios...")
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Criado: {dir_name}")
        else:
            print(f"  ✓ Existe: {dir_name}")

def check_files():
    """Verifica arquivos essenciais"""
    required_files = [
        "pipeline_integrado.py",
        "drive_uploader.py", 
        "requirements.txt",
        ".env.example"
    ]
    
    print("\n📄 Verificando arquivos essenciais...")
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            print(f"  ✓ Existe: {file_name}")
        else:
            print(f"  ❌ Faltando: {file_name}")

def check_environment():
    """Verifica variáveis de ambiente"""
    load_dotenv()
    
    print("\n🔐 Verificando configuração...")
    
    env_vars = {
        "GEMINI_API_KEY": "Chave do Gemini AI",
        "GOOGLE_APPLICATION_CREDENTIALS": "Caminho das credenciais Google",
        "DRIVE_FOLDER_ID": "ID da pasta do Google Drive"
    }
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var}: Configurado")
        else:
            print(f"  ⚠️  {var}: Não configurado ({description})")

def check_credentials():
    """Verifica arquivos de credenciais"""
    print("\n🗝️  Verificando credenciais...")
    
    creds_file = Path("google-drive-credentials.json")
    if creds_file.exists():
        try:
            with open(creds_file, 'r') as f:
                data = json.load(f)
                if 'client_id' in str(data):
                    print("  ✓ google-drive-credentials.json: Válido")
                else:
                    print("  ❌ google-drive-credentials.json: Formato inválido")
        except json.JSONDecodeError:
            print("  ❌ google-drive-credentials.json: JSON inválido")
    else:
        print("  ⚠️  google-drive-credentials.json: Não encontrado")

def check_dependencies():
    """Verifica dependências Python"""
    print("\n📦 Verificando dependências...")
    
    required_packages = [
        "google-generativeai",
        "google-api-python-client",
        "google-auth",
        "requests",
        "python-dotenv",
        "pillow"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✓ {package}: Instalado")
        except ImportError:
            print(f"  ❌ {package}: Não instalado")

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO DE AMBIENTE DO PIPELINE\n")
    
    check_directories()
    check_files()
    check_environment() 
    check_credentials()
    check_dependencies()
    
    print("\n" + "="*50)
    print("💡 PRÓXIMOS PASSOS:")
    print("1. Configure o arquivo .env com suas credenciais")
    print("2. Adicione google-drive-credentials.json")
    print("3. Execute: python3 pipeline_integrado.py")
    print("="*50)

if __name__ == "__main__":
    main()
