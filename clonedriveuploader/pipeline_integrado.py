#!/usr/bin/env python3

"""
Pipeline Integrado: YouTube Automation + Drive Uploader

Este script executa seu pipeline de criação de vídeos e faz upload 
automático de TODOS os assets para o Google Drive.
"""

import os
import sys
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Carrega credenciais do .env
load_dotenv()

# === CONFIGURAÇÃO DE PATHS PARA IMPORTS ===
# Adiciona os diretórios dos módulos ao sys.path
REPO_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(REPO_ROOT / 'youtube_automation'))
sys.path.insert(0, str(REPO_ROOT / 'drive-uploader' / 'backend'))

# Credenciais Drive Uploader
DRIVE_CLIENT_ID = os.getenv("DRIVE_CLIENT_ID")
DRIVE_CLIENT_SECRET = os.getenv("DRIVE_CLIENT_SECRET")
DRIVE_PROJECT_ID = os.getenv("DRIVE_PROJECT_ID")

try:
    # Importações após configurar sys.path
    from youtube_automation.main import run_pipeline
    print("✅ run_pipeline importado com sucesso!")
    
except ImportError as e:
    print(f"❌ Erro ao importar run_pipeline: {e}")
    print(" Verifique se o arquivo existe:")
    print(f"   - {REPO_ROOT / 'youtube_automation' / 'main.py'}")
    sys.exit(1)

try:
    from drive_client import DriveClient
    print("✅ DriveClient importado com sucesso!")
    
except ImportError as e:
    print(f"❌ Erro ao importar DriveClient: {e}")
    print(" Verifique se o arquivo existe:")
    print(f"   - {REPO_ROOT / 'drive-uploader' / 'backend' / 'drive_client.py'}")
    sys.exit(1)

def main():
    """
    Executa o pipeline completo com upload automático
    """
    
    print(" Iniciando Pipeline Integrado")
    
    # 1. Executa pipeline de criação de vídeo
    try:
        print(" Executando pipeline de criação...")
        project_folder = run_pipeline(topic="Mistérios do Brasil")
        print(f"✅ Pipeline concluído. Pasta: {project_folder}")
    except Exception as e:
        print(f"❌ Erro no pipeline de criação: {e}")
        return

    # 2. Inicializa cliente Drive
    try:
        print(" Inicializando cliente Google Drive...")
        drive = DriveClient(
            client_id=DRIVE_CLIENT_ID,
            client_secret=DRIVE_CLIENT_SECRET,
            project_id=DRIVE_PROJECT_ID,
            redirect_uri="urn:ietf:wg:oauth:2.0:oob"
        )
        print("✅ Cliente Drive inicializado")
    except Exception as e:
        print(f"❌ Erro ao inicializar Drive: {e}")
        return

    # 3. Cria pasta de projeto no Drive
    try:
        date_str = datetime.date.today().isoformat()
        drive_folder = f"{date_str}_{project_folder.name}"
        print(f" Criando pasta no Drive: {drive_folder}")
        
        root_folder_id = drive.create_folder(drive_folder, parent_id=None)
        print(f"✅ Pasta criada no Drive com ID: {root_folder_id}")
    except Exception as e:
        print(f"❌ Erro ao criar pasta no Drive: {e}")
        return

    # 4. Upload de assets
    upload_count = 0
    subfolders = ["raw", "assets/audio", "assets/images", "assets/thumbnails", "final"]
    
    for sub in subfolders:
        local_dir = project_folder / sub
        if not local_dir.exists():
            print(f"⚠️ Pasta não encontrada: {local_dir}")
            continue
            
        try:
            # Cria subpasta no Drive
            sub_folder_id = drive.create_folder(sub, parent_id=root_folder_id)
            print(f" Criada subpasta: {sub}")
            
            # Upload de cada arquivo
            for file_path in local_dir.iterdir():
                if file_path.is_file():
                    drive.upload_file(
                        local_path=str(file_path),
                        drive_folder_id=sub_folder_id
                    )
                    print(f"⬆️ {file_path.name} → {sub}")
                    upload_count += 1
                    
        except Exception as e:
            print(f"❌ Erro no upload da pasta {sub}: {e}")

    print(f" Pipeline integrado concluído!")
    print(f" Total de arquivos enviados: {upload_count}")
    print(f" Verifique no Google Drive: {drive_folder}")

if __name__ == "__main__":
    main()