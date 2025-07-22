
#!/usr/bin/env python3
"""
Sistema de Upload para Google Drive - Versão Otimizada
Integração completa com pipeline de automação
"""

import os
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import google.auth
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("drive_uploader")

# Carregar variáveis de ambiente
load_dotenv()

class DriveUploader:
    def __init__(self):
        self.service = None
        self.scopes = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.metadata'
        ]
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "google-drive-credentials.json")
        self.token_path = "token.json"
        
        # Configurar autenticação
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Configura autenticação com Google Drive"""
        try:
            creds = None
            
            # Tentar carregar token existente
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
            
            # Se não houver credenciais válidas disponíveis, solicitar autorização
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        logger.warning(f"Erro ao renovar token: {e}")
                        creds = None
                
                if not creds:
                    # Tentar service account primeiro
                    if os.path.exists(self.credentials_path):
                        try:
                            creds = service_account.Credentials.from_service_account_file(
                                self.credentials_path, scopes=self.scopes)
                            logger.info("Usando credenciais de service account")
                        except Exception as e:
                            logger.warning(f"Falha com service account: {e}")
                            
                            # Fallback para OAuth flow
                            flow = InstalledAppFlow.from_client_secrets_file(
                                self.credentials_path, self.scopes)
                            creds = flow.run_local_server(port=0)
                    else:
                        logger.error(f"Arquivo de credenciais não encontrado: {self.credentials_path}")
                        return False
                
                # Salvar credenciais para próxima execução (apenas OAuth)
                if hasattr(creds, 'to_json'):
                    with open(self.token_path, 'w') as token:
                        token.write(creds.to_json())
            
            # Construir serviço
            self.service = build('drive', 'v3', credentials=creds)
            logger.info("Autenticação com Google Drive concluída")
            return True
            
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            return False
    
    def create_folder(self, folder_name, parent_id=None):
        """Cria uma pasta no Google Drive"""
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                folder_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id,name'
            ).execute()
            
            logger.info(f"Pasta criada: {folder.get('name')} (ID: {folder.get('id')})")
            return folder.get('id')
            
        except HttpError as e:
            logger.error(f"Erro ao criar pasta: {e}")
            return None
    
    def upload_file(self, file_path, folder_id=None, custom_name=None):
        """Faz upload de um arquivo para o Google Drive"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"Arquivo não encontrado: {file_path}")
                return None
            
            # Determinar tipo MIME
            mime_types = {
                '.txt': 'text/plain',
                '.json': 'application/json',
                '.mp3': 'audio/mpeg',
                '.mp4': 'video/mp4',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.pdf': 'application/pdf'
            }
            
            mime_type = mime_types.get(file_path.suffix.lower(), 'application/octet-stream')
            
            # Metadados do arquivo
            file_metadata = {
                'name': custom_name or file_path.name
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Upload do arquivo
            media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            logger.info(f"Arquivo enviado: {file.get('name')} (ID: {file.get('id')})")
            return file
            
        except HttpError as e:
            logger.error(f"Erro ao fazer upload: {e}")
            return None
    
    def upload_directory(self, local_dir, parent_folder_id=None, project_name=None):
        """Faz upload de um diretório completo"""
        try:
            local_dir = Path(local_dir)
            if not local_dir.exists():
                logger.error(f"Diretório não encontrado: {local_dir}")
                return None
            
            # Criar pasta principal do projeto
            if not project_name:
                project_name = f"{datetime.now().strftime('%Y-%m-%d')}_{local_dir.name}"
            
            main_folder_id = self.create_folder(project_name, parent_folder_id)
            if not main_folder_id:
                return None
            
            uploaded_files = []
            total_files = 0
            
            # Fazer upload recursivo
            def upload_recursive(current_dir, parent_id):
                nonlocal total_files
                
                for item in current_dir.iterdir():
                    if item.is_file():
                        # Upload de arquivo
                        file_result = self.upload_file(item, parent_id)
                        if file_result:
                            uploaded_files.append({
                                'name': file_result.get('name'),
                                'id': file_result.get('id'),
                                'link': file_result.get('webViewLink'),
                                'local_path': str(item)
                            })
                            total_files += 1
                    
                    elif item.is_dir() and not item.name.startswith('.'):
                        # Criar subpasta e fazer upload recursivo
                        subfolder_id = self.create_folder(item.name, parent_id)
                        if subfolder_id:
                            upload_recursive(item, subfolder_id)
            
            # Executar upload
            upload_recursive(local_dir, main_folder_id)
            
            # Gerar relatório
            result = {
                'project_name': project_name,
                'main_folder_id': main_folder_id,
                'total_files': total_files,
                'uploaded_files': uploaded_files,
                'drive_url': f"https://drive.google.com/drive/folders/{main_folder_id}"
            }
            
            # Salvar URL para referência
            url_file = local_dir / "drive_url.txt"
            with open(url_file, 'w') as f:
                f.write(result['drive_url'])
            
            logger.info(f"Upload concluído: {total_files} arquivos enviados")
            logger.info(f"URL do projeto: {result['drive_url']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no upload do diretório: {e}")
            return None

def main():
    """Função principal para uso via linha de comando"""
    parser = argparse.ArgumentParser(description='Upload de arquivos para Google Drive')
    parser.add_argument('--input-dir', type=str, required=True,
                        help='Diretório para upload')
    parser.add_argument('--project-name', type=str,
                        help='Nome do projeto no Drive')
    parser.add_argument('--parent-folder-id', type=str,
                        help='ID da pasta pai no Drive')
    
    args = parser.parse_args()
    
    # Inicializar uploader
    uploader = DriveUploader()
    if not uploader.service:
        logger.error("Falha na inicialização do Drive")
        return 1
    
    # Fazer upload
    result = uploader.upload_directory(
        args.input_dir,
        args.parent_folder_id,
        args.project_name
    )
    
    if result:
        print(f"\n✅ Upload concluído com sucesso!")
        print(f"📁 Projeto: {result['project_name']}")
        print(f"📊 Arquivos enviados: {result['total_files']}")
        print(f"🔗 URL: {result['drive_url']}")
        return 0
    else:
        print("\n❌ Falha no upload")
        return 1

if __name__ == "__main__":
    exit(main())
