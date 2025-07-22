#!/usr/bin/env python3
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Carregar variáveis de ambiente
load_dotenv()

class SheetsTracker:
    def __init__(self):
        """Inicializa o tracker de Google Sheets"""
        self.credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.tracking_sheet_id = os.getenv("SHEETS_TRACKING_ID")
        self.service = None
        
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializa o serviço do Google Sheets"""
        try:
            if not self.credentials_path or not os.path.exists(self.credentials_path):
                print(f"Arquivo de credenciais não encontrado: {self.credentials_path}")
                return
            
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            self.service = build('sheets', 'v4', credentials=credentials)
            print("Serviço do Google Sheets inicializado com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar serviço do Google Sheets: {e}")
    
    def create_tracking_sheet(self, title="Automação de Vídeos - Pipeline"):
        """Cria uma nova planilha de tracking"""
        if not self.service:
            print("Serviço do Google Sheets não inicializado")
            return None
        
        try:
            # Criar planilha
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Pipeline',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 10
                            }
                        }
                    }
                ]
            }
            
            response = self.service.spreadsheets().create(body=spreadsheet).execute()
            sheet_id = response['spreadsheetId']
            
            # Configurar cabeçalhos
            headers = [
                ["Data", "Tópico", "Status", "Etapa Atual", "Duração (s)", "URL Drive", "Erros", "Timestamp"]
            ]
            
            self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range='Pipeline!A1:H1',
                valueInputOption='RAW',
                body={'values': headers}
            ).execute()
            
            # Formatar cabeçalhos
            requests = [
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': 0,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8},
                                'textFormat': {'bold': True}
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                }
            ]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=sheet_id,
                body={'requests': requests}
            ).execute()
            
            print(f"Planilha criada com ID: {sheet_id}")
            print(f"Adicione este ID ao .env como SHEETS_TRACKING_ID={sheet_id}")
            
            return sheet_id
            
        except Exception as e:
            print(f"Erro ao criar planilha: {e}")
            return None
    
    def update_status(self, topic, status, step, duration=None, drive_url=None, errors=None):
        """Atualiza o status do pipeline na planilha"""
        if not self.service or not self.tracking_sheet_id:
            print("Serviço ou ID da planilha não configurados")
            return False
        
        try:
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # Verificar se já existe uma linha para este tópico e data
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.tracking_sheet_id,
                range='Pipeline!A:B'
            ).execute()
            
            rows = result.get('values', [])
            row_index = None
            
            for i, row in enumerate(rows):
                if len(row) >= 2 and row[0] == date and row[1] == topic:
                    row_index = i + 1  # +1 porque as planilhas são 1-indexadas
                    break
            
            # Se não encontrou, adicionar nova linha
            if row_index is None:
                row_index = len(rows) + 1
            
            # Preparar dados
            row_data = [
                date, 
                topic, 
                status, 
                step, 
                duration if duration is not None else "", 
                drive_url if drive_url else "",
                errors if errors else "",
                timestamp
            ]
            
            # Atualizar planilha
            self.service.spreadsheets().values().update(
                spreadsheetId=self.tracking_sheet_id,
                range=f'Pipeline!A{row_index}:H{row_index}',
                valueInputOption='RAW',
                body={'values': [row_data]}
            ).execute()
            
            print(f"Status atualizado para {topic}: {status} ({step})")
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar status: {e}")
            return False


if __name__ == "__main__":
    import sys
    
    tracker = SheetsTracker()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "create":
            # Criar nova planilha
            title = sys.argv[2] if len(sys.argv) > 2 else "Automação de Vídeos - Pipeline"
            tracker.create_tracking_sheet(title)
        
        elif sys.argv[1] == "update" and len(sys.argv) > 3:
            # Atualizar status
            topic = sys.argv[2]
            status = sys.argv[3]
            step = sys.argv[4] if len(sys.argv) > 4 else "Executando"
            tracker.update_status(topic, status, step)
    else:
        print("Uso:")
        print("  python sheets_tracker.py create [título]")
        print("  python sheets_tracker.py update \"Título do Vídeo\" \"Status\" \"Etapa\"")