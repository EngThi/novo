import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive():
    """Upload de arquivos para o Google Drive."""
    print("Iniciando upload para o Google Drive...")
    
    # Carregar credenciais do Google
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS")
    if not credentials_json:
        print("Erro: Credenciais do Google não encontradas!")
        return
    
    # Escrever as credenciais em um arquivo temporário
    with open('temp_credentials.json', 'w') as f:
        f.write(credentials_json)
    
    # Autenticar
    credentials = service_account.Credentials.from_service_account_file(
        'temp_credentials.json',
        scopes=['https://www.googleapis.com/auth/drive']
    )
    
    # Construir serviço
    drive_service = build('drive', 'v3', credentials=credentials)
    
    # Carregar roteiros para determinar o que fazer upload
    with open('data/scripts.json', 'r') as f:
        scripts = json.load(f)
    
    for i, script in enumerate(scripts):
        # Criar pasta para o projeto
        folder_name = f"AutoContent-{script['topic']}"
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
        folder_id = folder.get('id')
        
        print(f"Criada pasta: {folder_name} (ID: {folder_id})")
        
        # Upload do roteiro
        script_path = f"data/final/script_{i}.txt"
        
        # Escrever o roteiro em um arquivo
        with open(script_path, 'w') as f:
            f.write(f"ROTEIRO: {script['topic']}\n\n")
            for ts in script['timestamps']:
                f.write(f"[{ts['start']:.1f}-{ts['end']:.1f}] {ts['text']}\n")
        
        # Upload para o Drive
        file_metadata = {
            'name': f"roteiro-{script['topic']}.txt",
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(script_path, mimetype='text/plain')
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        print(f"Arquivo de roteiro enviado: {file.get('id')}")
        
        # Upload de imagens (simulado)
        # for j in range(5):
        #    image_path = f"data/images/script_{i}/image_{j}.jpg"
        #    if os.path.exists(image_path):
        #        file_metadata = {
        #            'name': f"imagem-{j}.jpg",
        #            'parents': [folder_id]
        #        }
        #        media = MediaFileUpload(image_path, mimetype='image/jpeg')
        #        file = drive_service.files().create(
        #            body=file_metadata,
        #            media_body=media,
        #            fields='id'
        #        ).execute()
        #        print(f"Imagem {j} enviada: {file.get('id')}")
    
    # Remover arquivo de credenciais temporário
    os.remove('temp_credentials.json')
    print("Upload para o Drive concluído com sucesso!")

if __name__ == "__main__":
    upload_to_drive()