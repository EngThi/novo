
import os
import json
import logging
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriveUploader:
    def __init__(self):
        self.credentials_path = os.getenv("DRIVE_CREDENTIALS_PATH", "google-drive-credentials.json")
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializa o serviço do Google Drive"""
        try:
            if not os.path.exists(self.credentials_path):
                logger.error(f"Arquivo de credenciais não encontrado: {self.credentials_path}")
                return
            
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            self.service = build('drive', 'v3', credentials=credentials)
            logger.info("Serviço do Google Drive inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar Google Drive: {e}")
            self.service = None
    
    def create_folder(self, folder_name, parent_id=None):
        """Cria uma pasta no Google Drive"""
        if not self.service:
            return None
        
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                folder_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            logger.info(f"Pasta criada: {folder_name} (ID: {folder.get('id')})")
            return folder.get('id')
        except Exception as e:
            logger.error(f"Erro ao criar pasta: {e}")
            return None
    
    def upload_file(self, file_path, folder_id=None, new_name=None):
        """Faz upload de um arquivo para o Google Drive"""
        if not self.service:
            return None
        
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                logger.error(f"Arquivo não encontrado: {file_path}")
                return None
            
            # Determinar tipo MIME
            mime_types = {
                '.txt': 'text/plain',
                '.json': 'application/json',
                '.mp4': 'video/mp4',
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png'
            }
            
            mime_type = mime_types.get(file_path.suffix.lower(), 'application/octet-stream')
            
            file_metadata = {
                'name': new_name or file_path.name
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            media = MediaFileUpload(str(file_path), mimetype=mime_type)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink'
            ).execute()
            
            logger.info(f"Arquivo enviado: {file_path.name} (ID: {file.get('id')})")
            return file
        except Exception as e:
            logger.error(f"Erro ao fazer upload do arquivo {file_path}: {e}")
            return None
    
    def upload_project(self, project_dir, project_name=None):
        """Faz upload de uma pasta completa de projeto"""
        if not self.service:
            logger.error("Serviço do Google Drive não inicializado")
            return None
        
        try:
            project_path = Path(project_dir)
            if not project_path.exists():
                logger.error(f"Diretório do projeto não encontrado: {project_path}")
                return None
            
            # Nome do projeto
            if not project_name:
                project_name = f"Video_Automation_{project_path.name}"
            
            # Criar pasta principal do projeto
            main_folder_id = self.create_folder(project_name)
            if not main_folder_id:
                return None
            
            uploaded_files = []
            
            # Upload de arquivos na raiz do projeto
            for file_path in project_path.iterdir():
                if file_path.is_file():
                    result = self.upload_file(file_path, main_folder_id)
                    if result:
                        uploaded_files.append(result)
            
            # Upload de subpastas
            for subdir in project_path.iterdir():
                if subdir.is_dir():
                    subfolder_id = self.create_folder(subdir.name, main_folder_id)
                    if subfolder_id:
                        for file_path in subdir.rglob('*'):
                            if file_path.is_file():
                                result = self.upload_file(file_path, subfolder_id)
                                if result:
                                    uploaded_files.append(result)
            
            # Obter link da pasta principal
            folder_link = f"https://drive.google.com/drive/folders/{main_folder_id}"
            
            # Salvar URL do Drive no projeto
            url_file = project_path / "drive_url.txt"
            with open(url_file, 'w') as f:
                f.write(folder_link)
            
            logger.info(f"Upload completo! Pasta: {folder_link}")
            return {
                'folder_id': main_folder_id,
                'folder_link': folder_link,
                'uploaded_files': len(uploaded_files)
            }
        except Exception as e:
            logger.error(f"Erro no upload do projeto: {e}")
            return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload para Google Drive')
    parser.add_argument('--input-dir', type=str, required=True,
                        help='Diretório do projeto para upload')
    parser.add_argument('--project-name', type=str,
                        help='Nome do projeto no Drive')
    args = parser.parse_args()
    
    uploader = DriveUploader()
    result = uploader.upload_project(args.input_dir, args.project_name)
    
    if result:
        print(f"✓ Upload concluído: {result['folder_link']}")
        print(f"✓ {result['uploaded_files']} arquivos enviados")
    else:
        print("✗ Erro no upload")
