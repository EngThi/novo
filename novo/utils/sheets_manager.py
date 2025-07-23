
#!/usr/bin/env python3
"""
Sistema Avançado de Integração com Google Sheets
Gerencia tracking de projetos e acompanhamento de pipeline
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import googleapiclient.discovery
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class SheetsManager:
    """Gerenciador completo de Google Sheets"""
    
    def __init__(self, credentials_path: str = "google-drive-credentials.json"):
        self.credentials_path = Path(credentials_path)
        self.sheets_id = os.getenv('SHEETS_TRACKING_ID')
        self.service = None
        
        if self.sheets_id and self.credentials_path.exists():
            self._authenticate()
    
    def _authenticate(self):
        """Autentica com Google Sheets API"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                str(self.credentials_path),
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
            logger.info("✅ Conectado ao Google Sheets")
        except Exception as e:
            logger.error(f"Erro na autenticação Sheets: {e}")
            self.service = None
    
    def create_project_entry(self, project_name: str, topic: str) -> Optional[int]:
        """Cria nova entrada de projeto na planilha"""
        if not self.service or not self.sheets_id:
            return None
        
        try:
            # Dados do novo projeto
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            values = [[
                project_name,
                topic,
                timestamp,
                "Iniciado",
                "",  # URL será preenchida depois
                "Automático"
            ]]
            
            # Adicionar linha
            body = {'values': values}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.sheets_id,
                range='Produção!A:F',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            # Calcular índice da linha inserida
            updated_range = result.get('updates', {}).get('updatedRange', '')
            if '!' in updated_range:
                row_part = updated_range.split('!')[-1]
                row_number = int(row_part.split(':')[0][1:])
                logger.info(f"✅ Projeto criado na linha {row_number}")
                return row_number
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao criar entrada do projeto: {e}")
            return None
    
    def update_status(self, row_index: int, status: str, url: Optional[str] = None):
        """Atualiza status do projeto"""
        if not self.service or not self.sheets_id:
            return
        
        try:
            # Atualizar status
            range_name = f'Produção!D{row_index}'
            body = {'values': [[status]]}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.sheets_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            # Atualizar URL se fornecida
            if url:
                range_name = f'Produção!E{row_index}'
                body = {'values': [[url]]}
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.sheets_id,
                    range=range_name,
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
            
            logger.info(f"✅ Status atualizado: {status}")
            
        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}")
    
    def get_pending_projects(self) -> List[Dict[str, Any]]:
        """Obtém projetos pendentes da planilha"""
        if not self.service or not self.sheets_id:
            return []
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range='Produção!A2:F50'
            ).execute()
            
            rows = result.get('values', [])
            pending = []
            
            for i, row in enumerate(rows, start=2):
                if len(row) >= 4:
                    status = row[3] if len(row) > 3 else ""
                    if status in ["", "Pendente", "Aguardando"]:
                        pending.append({
                            'row_index': i,
                            'project_name': row[0] if len(row) > 0 else "",
                            'topic': row[1] if len(row) > 1 else "",
                            'timestamp': row[2] if len(row) > 2 else "",
                            'status': status
                        })
            
            logger.info(f"✅ {len(pending)} projetos pendentes encontrados")
            return pending
            
        except Exception as e:
            logger.error(f"Erro ao buscar projetos pendentes: {e}")
            return []
    
    def log_completion(self, row_index: int, metrics: Dict[str, Any]):
        """Registra conclusão com métricas"""
        if not self.service or not self.sheets_id:
            return
        
        try:
            # Preparar dados de conclusão
            completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Atualizar múltiplas colunas
            updates = [
                {
                    'range': f'Produção!D{row_index}',
                    'values': [['Concluído']]
                },
                {
                    'range': f'Produção!F{row_index}',
                    'values': [[completion_time]]
                }
            ]
            
            # Adicionar métricas se houver colunas extras
            if 'duration' in metrics:
                updates.append({
                    'range': f'Produção!G{row_index}',
                    'values': [[metrics['duration']]]
                })
            
            # Executar atualizações em lote
            body = {'valueInputOption': 'USER_ENTERED', 'data': updates}
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=self.sheets_id,
                body=body
            ).execute()
            
            logger.info("✅ Conclusão registrada com métricas")
            
        except Exception as e:
            logger.error(f"Erro ao registrar conclusão: {e}")
    
    def create_tracking_sheet(self) -> Optional[str]:
        """Cria planilha de tracking se não existir"""
        try:
            # Criar nova planilha
            spreadsheet = {
                'properties': {
                    'title': f'Pipeline Tracking - {datetime.now().strftime("%Y-%m")}'
                },
                'sheets': [{
                    'properties': {
                        'title': 'Produção'
                    }
                }]
            }
            
            sheet = self.service.spreadsheets().create(body=spreadsheet).execute()
            sheet_id = sheet.get('spreadsheetId')
            
            # Adicionar cabeçalhos
            headers = [['Projeto', 'Tópico', 'Início', 'Status', 'URL', 'Tipo', 'Conclusão']]
            body = {'values': headers}
            
            self.service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range='Produção!A1:G1',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            logger.info(f"✅ Planilha de tracking criada: {sheet_id}")
            return sheet_id
            
        except Exception as e:
            logger.error(f"Erro ao criar planilha: {e}")
            return None

def get_sheets_manager() -> SheetsManager:
    """Obtém instância do gerenciador de sheets"""
    return SheetsManager()
