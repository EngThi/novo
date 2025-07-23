
#!/usr/bin/env python3
"""
Sistema Completo de Upload para Google Drive
Baseado no clonedriveuploader com melhorias de segurança e funcionalidade
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import pickle

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Escopos necessários para o Google Drive
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]

class DriveUploader:
    """Sistema robusto de upload para Google Drive"""
    
    def __init__(self, credentials_path: str = "google-drive-credentials.json"):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path("token.pickle")
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Autentica com o Google Drive API"""
        creds = None
        
        # Carregar token salvo se existir
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Se não há credenciais válidas, fazer login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Erro ao renovar token: {e}")
                    creds = None
            
            if not creds:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Arquivo de credenciais não encontrado: {self.credentials_path}\n"
                        "Baixe suas credenciais do Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Salvar credenciais para próxima execução
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('drive', 'v3', credentials=creds)
        logger.info("✅ Autenticação com Google Drive realizada com sucesso")
    
    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
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
                fields='id,name,webViewLink'
            ).execute()
            
            folder_id = folder.get('id')
            folder_url = folder.get('webViewLink')
            
            logger.info(f"✅ Pasta criada: {folder_name} (ID: {folder_id})")
            return folder_id, folder_url
            
        except HttpError as e:
            logger.error(f"❌ Erro ao criar pasta {folder_name}: {e}")
            raise
    
    def upload_file(self, file_path: Path, folder_id: Optional[str] = None, 
                   description: str = "") -> Dict[str, Any]:
        """Upload de um arquivo para o Google Drive"""
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
            # Metadados do arquivo
            file_metadata = {
                'name': file_path.name,
                'description': description
            }
            
            if folder_id:
                file_metadata['parents'] = [folder_id]
            
            # Determinar tipo MIME
            mime_type = self._get_mime_type(file_path)
            
            # Upload do arquivo
            media = MediaFileUpload(
                str(file_path),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink,size'
            ).execute()
            
            result = {
                'id': file.get('id'),
                'name': file.get('name'),
                'url': file.get('webViewLink'),
                'size': file.get('size'),
                'local_path': str(file_path)
            }
            
            logger.info(f"✅ Upload concluído: {file_path.name}")
            return result
            
        except HttpError as e:
            logger.error(f"❌ Erro no upload de {file_path.name}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Erro inesperado no upload: {e}")
            raise
    
    def upload_directory(self, directory: Path, project_name: str) -> Dict[str, Any]:
        """Upload de um diretório completo para o Google Drive"""
        try:
            if not directory.exists() or not directory.is_dir():
                raise ValueError(f"Diretório inválido: {directory}")
            
            # Criar pasta principal do projeto
            main_folder_id, main_folder_url = self.create_folder(project_name)
            
            # Estrutura para organizar uploads
            uploaded_files = {
                'project_name': project_name,
                'main_folder_url': main_folder_url,
                'main_folder_id': main_folder_id,
                'files': [],
                'subfolders': {}
            }
            
            # Mapear tipos de arquivo para subpastas
            folder_mapping = {
                'scripts': ['.py', '.txt', '.md'],
                'audio': ['.mp3', '.wav', '.m4a'],
                'images': ['.jpg', '.jpeg', '.png', '.gif'],
                'videos': ['.mp4', '.avi', '.mov'],
                'data': ['.json', '.csv', '.xml']
            }
            
            # Criar subpastas
            for folder_name in folder_mapping.keys():
                subfolder_id, subfolder_url = self.create_folder(
                    folder_name.capitalize(), 
                    main_folder_id
                )
                uploaded_files['subfolders'][folder_name] = {
                    'id': subfolder_id,
                    'url': subfolder_url,
                    'files': []
                }
            
            # Upload de todos os arquivos
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    # Determinar pasta de destino
                    target_folder = self._determine_target_folder(
                        file_path, folder_mapping
                    )
                    
                    folder_id = uploaded_files['subfolders'][target_folder]['id']
                    
                    # Upload do arquivo
                    file_info = self.upload_file(
                        file_path, 
                        folder_id,
                        f"Arquivo do projeto {project_name}"
                    )
                    
                    uploaded_files['subfolders'][target_folder]['files'].append(file_info)
                    uploaded_files['files'].append(file_info)
            
            # Salvar informações do upload
            self._save_upload_info(directory, uploaded_files)
            
            logger.info(f"✅ Upload completo do projeto: {project_name}")
            logger.info(f"📁 URL da pasta: {main_folder_url}")
            
            return uploaded_files
            
        except Exception as e:
            logger.error(f"❌ Erro no upload do diretório: {e}")
            raise
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Determina o tipo MIME do arquivo"""
        mime_types = {
            '.txt': 'text/plain',
            '.py': 'text/x-python',
            '.json': 'application/json',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.mp4': 'video/mp4',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif'
        }
        
        suffix = file_path.suffix.lower()
        return mime_types.get(suffix, 'application/octet-stream')
    
    def _determine_target_folder(self, file_path: Path, folder_mapping: Dict[str, List[str]]) -> str:
        """Determina a pasta de destino baseada na extensão do arquivo"""
        suffix = file_path.suffix.lower()
        
        for folder_name, extensions in folder_mapping.items():
            if suffix in extensions:
                return folder_name
        
        return 'data'  # Pasta padrão
    
    def _save_upload_info(self, directory: Path, upload_info: Dict[str, Any]):
        """Salva informações do upload em arquivos locais"""
        try:
            # Salvar URL da pasta principal
            url_file = directory / "drive_url.txt"
            with open(url_file, 'w') as f:
                f.write(upload_info['main_folder_url'])
            
            # Salvar informações completas
            info_file = directory / "upload_info.json"
            with open(info_file, 'w') as f:
                json.dump(upload_info, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Informações do upload salvas em {directory}")
            
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível salvar informações do upload: {e}")

def main():
    """Função principal para teste e uso direto"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload para Google Drive')
    parser.add_argument('--input-dir', required=True, help='Diretório para upload')
    parser.add_argument('--project-name', required=True, help='Nome do projeto')
    parser.add_argument('--credentials', default='google-drive-credentials.json', 
                       help='Arquivo de credenciais')
    
    args = parser.parse_args()
    
    try:
        uploader = DriveUploader(args.credentials)
        result = uploader.upload_directory(Path(args.input_dir), args.project_name)
        
        print(f"\n🎉 Upload concluído com sucesso!")
        print(f"📁 Pasta principal: {result['main_folder_url']}")
        print(f"📊 Total de arquivos: {len(result['files'])}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Erro durante o upload: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
