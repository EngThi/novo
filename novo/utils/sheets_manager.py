import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class SheetsManager:
    def __init__(self):
        """Inicializa o gerenciador de planilhas"""
        self.credentials_path = os.getenv("DRIVE_CREDENTIALS_PATH", "google-drive-credentials.json")
        self.tracking_sheet_id = os.getenv("SHEETS_TRACKING_ID", "")
        self.service = None
        self.sheets = None
        
        if self.tracking_sheet_id:
            self._initialize_service()
    
    def _initialize_service(self):
        """Inicializa o serviço do Google Sheets"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=credentials)
            self.sheets = self.service.spreadsheets()
        except Exception as e:
            print(f"Erro ao inicializar Google Sheets: {e}")
            self.service = None
            self.sheets = None
    
    def create_tracking_sheet(self, title="Automação de Vídeos - Tracking"):
        """Cria uma nova planilha de tracking e configura suas colunas"""
        if not self.service:
            self._initialize_service()
            if not self.service:
                return None
        
        try:
            # Criar nova planilha
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Produção',
                            'gridProperties': {
                                'rowCount': 100,
                                'columnCount': 10
                            }
                        }
                    }
                ]
            }
            
            spreadsheet = self.service.spreadsheets().create(body=spreadsheet).execute()
            sheet_id = spreadsheet['spreadsheetId']
            
            # Configurar cabeçalhos
            headers = [
                ["Título do Projeto", "Data", "Tipo", "Status", "URL", "Timestamp", "Observações"]
            ]
            
            self.sheets.values().update(
                spreadsheetId=sheet_id,
                range='Produção!A1:G1',
                valueInputOption='USER_ENTERED',
                body={'values': headers}
            ).execute()
            
            # Formatar cabeçalhos em negrito
            requests = [{
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {'bold': True},
                            'backgroundColor': {'red': 0.95, 'green': 0.95, 'blue': 0.95}
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat,backgroundColor)'
                }
            }]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={'requests': requests}
            ).execute()
            
            print(f"Planilha de tracking criada com ID: {sheet_id}")
            print(f"Adicione este ID ao seu arquivo .env como SHEETS_TRACKING_ID={sheet_id}")
            
            return sheet_id
        except Exception as e:
            print(f"Erro ao criar planilha de tracking: {e}")
            return None
    
    def add_project(self, title, video_type="Automático"):
        """Adiciona um novo projeto à planilha de tracking"""
        if not self.sheets or not self.tracking_sheet_id:
            print("Serviço do Sheets não inicializado ou ID da planilha não definido")
            return False
            
        import datetime
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # Encontrar próxima linha vazia
            result = self.sheets.values().get(
                spreadsheetId=self.tracking_sheet_id,
                range='Produção!A1:A100'
            ).execute()
            
            values = result.get('values', [])
            next_row = len(values) + 1
            
            # Adicionar novo projeto
            row_data = [
                [title, today, video_type, "Pendente", "", timestamp, ""]
            ]
            
            self.sheets.values().update(
                spreadsheetId=self.tracking_sheet_id,
                range=f'Produção!A{next_row}:G{next_row}',
                valueInputOption='USER_ENTERED',
                body={'values': row_data}
            ).execute()
            
            print(f"Projeto '{title}' adicionado à planilha de tracking")
            return True
        except Exception as e:
            print(f"Erro ao adicionar projeto: {e}")
            return False
    
    def get_pending_projects(self):
        """Obtém lista de projetos pendentes"""
        if not self.sheets or not self.tracking_sheet_id:
            return []
            
        try:
            result = self.sheets.values().get(
                spreadsheetId=self.tracking_sheet_id,
                range='Produção!A2:E100'
            ).execute()
            
            rows = result.get('values', [])
            pending_projects = []
            
            for i, row in enumerate(rows, start=2):
                # Verifica se o status é pendente ou vazio
                if len(row) < 4 or row[3] == "" or row[3] == "Pendente":
                    project = {
                        'title': row[0] if len(row) > 0 else f"Projeto {i}",
                        'date': row[1] if len(row) > 1 else "",
                        'type': row[2] if len(row) > 2 else "Automático",
                        'row': i
                    }
                    pending_projects.append(project)
            
            return pending_projects
        except Exception as e:
            print(f"Erro ao buscar projetos pendentes: {e}")
            return []


if __name__ == "__main__":
    # Script para criar uma planilha de tracking ou adicionar projetos
    import sys
    
    manager = SheetsManager()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "create":
            # Criar nova planilha
            title = sys.argv[2] if len(sys.argv) > 2 else "Automação de Vídeos - Tracking"
            manager.create_tracking_sheet(title)
        
        elif sys.argv[1] == "add" and len(sys.argv) > 2:
            # Adicionar novo projeto
            project_title = sys.argv[2]
            project_type = sys.argv[3] if len(sys.argv) > 3 else "Automático"
            manager.add_project(project_title, project_type)
        
        elif sys.argv[1] == "list":
            # Listar projetos pendentes
            projects = manager.get_pending_projects()
            print(f"Projetos pendentes ({len(projects)}):")
            for p in projects:
                print(f"  - {p['title']} ({p['type']}) [linha {p['row']}]")
    else:
        print("Uso:")
        print("  python sheets_manager.py create [título]")
        print("  python sheets_manager.py add \"Título do Projeto\" [tipo]")
        print("  python sheets_manager.py list")