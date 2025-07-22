#!/usr/bin/env python3
import os
import sys
import time
import json
import logging
import datetime
import schedule
from dotenv import load_dotenv
import googleapiclient.discovery
from google.oauth2 import service_account
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("pipeline")

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de caminhos
YOUTUBE_AUTOMATION_DIR = Path("youtube_automation")
DRIVE_UPLOADER_DIR = Path("drive-uploader")
OUTPUT_BASE_DIR = YOUTUBE_AUTOMATION_DIR / "output"
CREDENTIALS_PATH = os.getenv("DRIVE_CREDENTIALS_PATH", "google-drive-credentials.json")
SHEETS_TRACKING_ID = os.getenv("SHEETS_TRACKING_ID", "")  # ID da planilha para tracking

class PipelineIntegrado:
    def __init__(self):
        self.today_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.project_name = None
        self.output_dir = None
        self.status_sheet = None
        
        # Verifica se os diretórios necessários existem
        self._check_directories()
        
        # Inicializa conexão com Google Sheets se o ID estiver disponível
        if SHEETS_TRACKING_ID:
            self._initialize_sheets()

    def _check_directories(self):
        """Verifica se os diretórios necessários existem"""
        if not YOUTUBE_AUTOMATION_DIR.exists():
            logger.error(f"Diretório {YOUTUBE_AUTOMATION_DIR} não encontrado!")
            sys.exit(1)
        
        if not DRIVE_UPLOADER_DIR.exists():
            logger.error(f"Diretório {DRIVE_UPLOADER_DIR} não encontrado!")
            sys.exit(1)
            
        # Cria o diretório de output se não existir
        OUTPUT_BASE_DIR.mkdir(exist_ok=True)
    
    def _initialize_sheets(self):
        """Inicializa conexão com Google Sheets para tracking"""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                CREDENTIALS_PATH,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            service = googleapiclient.discovery.build('sheets', 'v4', credentials=credentials)
            self.status_sheet = service.spreadsheets()
            logger.info("Conexão com Google Sheets inicializada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar Google Sheets: {e}")
            self.status_sheet = None
    
    def _update_sheet_status(self, row_index, status, url=None):
        """Atualiza o status na planilha de tracking"""
        if not self.status_sheet or not SHEETS_TRACKING_ID:
            return
        
        try:
            # Atualiza o status
            range_name = f'Produção!D{row_index}'
            body = {
                'values': [[status]]
            }
            self.status_sheet.values().update(
                spreadsheetId=SHEETS_TRACKING_ID,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            # Se houver URL, atualiza também
            if url:
                range_name = f'Produção!E{row_index}'
                body = {
                    'values': [[url]]
                }
                self.status_sheet.values().update(
                    spreadsheetId=SHEETS_TRACKING_ID,
                    range=range_name,
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
                
            logger.info(f"Status atualizado na planilha: {status}")
        except Exception as e:
            logger.error(f"Erro ao atualizar planilha: {e}")
    
    def descobrir_conteudo(self):
        """Executa a descoberta de conteúdo"""
        logger.info("Iniciando descoberta de conteúdo em alta...")
        
        try:
            # Obtém o próximo projeto da planilha de tracking ou gera um novo
            self.project_name = self._obter_proximo_projeto()
            if not self.project_name:
                self.project_name = f"Conteudo_Auto_{self.today_date}"
            
            # Cria diretório de saída específico para este projeto
            self.output_dir = OUTPUT_BASE_DIR / f"{self.today_date}_{self.project_name.replace(' ', '_')}"
            self.output_dir.mkdir(exist_ok=True)
            
            # Executa o script de descoberta de conteúdo
            os.system(f"cd {YOUTUBE_AUTOMATION_DIR} && python content_discovery.py --output-dir {self.output_dir}")
            
            # Atualiza status
            self._update_sheet_status(self.row_index, "Conteúdo Descoberto")
            return True
        except Exception as e:
            logger.error(f"Erro na descoberta de conteúdo: {e}")
            return False
    
    def _obter_proximo_projeto(self):
        """Obtém o próximo projeto da planilha de tracking"""
        if not self.status_sheet or not SHEETS_TRACKING_ID:
            return None
        
        try:
            # Busca projetos pendentes na planilha
            result = self.status_sheet.values().get(
                spreadsheetId=SHEETS_TRACKING_ID,
                range='Produção!A2:D50'  # Ajuste o intervalo conforme sua planilha
            ).execute()
            
            rows = result.get('values', [])
            for i, row in enumerate(rows, start=2):  # Começamos do índice 2 pois A1 é cabeçalho
                # Verifica se há um projeto pendente (status vazio ou "Pendente")
                if len(row) >= 4 and (len(row) < 4 or row[3] == "" or row[3] == "Pendente"):
                    self.row_index = i
                    return row[0] if len(row) > 0 else None
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar próximo projeto: {e}")
            return None
    
    def gerar_roteiro(self):
        """Gera roteiro para o conteúdo"""
        logger.info(f"Gerando roteiro para: {self.project_name}")
        
        try:
            # Executa o script de geração de roteiro
            os.system(f"cd {YOUTUBE_AUTOMATION_DIR} && python script_generator.py --output-dir {self.output_dir}")
            
            # Atualiza status
            self._update_sheet_status(self.row_index, "Roteiro Gerado")
            return True
        except Exception as e:
            logger.error(f"Erro na geração de roteiro: {e}")
            return False
    
    def gerar_narracao(self):
        """Gera narração para o roteiro"""
        logger.info(f"Gerando narração para: {self.project_name}")
        
        try:
            # Executa o script de geração de narração
            os.system(f"cd {YOUTUBE_AUTOMATION_DIR} && python narration_generator.py --output-dir {self.output_dir}")
            
            # Atualiza status
            self._update_sheet_status(self.row_index, "Narração Gerada")
            return True
        except Exception as e:
            logger.error(f"Erro na geração de narração: {e}")
            return False
    
    def processar_imagens(self):
        """Processa imagens para o vídeo"""
        logger.info(f"Processando imagens para: {self.project_name}")
        
        try:
            # Executa o script de processamento de imagens
            os.system(f"cd {YOUTUBE_AUTOMATION_DIR} && python image_processor.py --output-dir {self.output_dir}")
            
            # Atualiza status
            self._update_sheet_status(self.row_index, "Imagens Processadas")
            return True
        except Exception as e:
            logger.error(f"Erro no processamento de imagens: {e}")
            return False
    
    def montar_video(self):
        """Monta o vídeo final"""
        logger.info(f"Montando vídeo final: {self.project_name}")

        try:
            # Executa o script de montagem de vídeo
            os.system(f"cd {YOUTUBE_AUTOMATION_DIR} && python video_assembler.py --output-dir {self.output_dir}")

            # Atualiza status
            self._update_sheet_status(self.row_index, "Vídeo Montado")
            return True
        except Exception as e:
            logger.error(f"Erro na montagem do vídeo: {e}")
            return False

    def upload_drive(self):
        """Upload de arquivos para o Google Drive"""
        logger.info(f"Realizando upload para o Drive: {self.project_name}")

        try:
            # Executa o script de upload do Drive usando o drive_uploader.py local
            result = os.system(f"python drive_uploader.py --input-dir {self.output_dir} --project-name '{self.project_name}'")

            # Obtém URL do Google Drive da saída do upload (se disponível)
            drive_url = None
            url_file = self.output_dir / "drive_url.txt"
            if url_file.exists():
                with open(url_file, 'r') as f:
                    drive_url = f.read().strip()

            # Atualiza status
            self._update_sheet_status(self.row_index, "Upload Concluído", drive_url)
            return result == 0
        except Exception as e:
            logger.error(f"Erro no upload para o Drive: {e}")
            return False
    
    def executar_pipeline_completo(self):
        """Executa o pipeline completo de automação"""
        logger.info("Iniciando execução do pipeline completo...")
        
        # Executa cada etapa do pipeline
        if self.descobrir_conteudo():
            logger.info("✓ Etapa 1: Descoberta de conteúdo concluída")
            
            if self.gerar_roteiro():
                logger.info("✓ Etapa 2: Geração de roteiro concluída")
                
                if self.gerar_narracao():
                    logger.info("✓ Etapa 3: Geração de narração concluída")
                    
                    if self.processar_imagens():
                        logger.info("✓ Etapa 4: Processamento de imagens concluído")
                        
                        if self.montar_video():
                            logger.info("✓ Etapa 5: Montagem de vídeo concluída")

                            if self.upload_drive():
                                logger.info("✓ Etapa 6: Upload para Google Drive concluído")
                                logger.info("Pipeline concluído com sucesso!")
                                return True
                            else:
                                logger.error("✗ Etapa 6: Falha no upload para Google Drive")
                        else:
                            logger.error("✗ Etapa 5: Falha na montagem do vídeo")
                    else:
                        logger.error("✗ Etapa 4: Falha no processamento de imagens")
                else:
                    logger.error("✗ Etapa 3: Falha na geração de narração")
            else:
                logger.error("✗ Etapa 2: Falha na geração de roteiro")
        else:
            logger.error("✗ Etapa 1: Falha na descoberta de conteúdo")
        
        logger.error("Pipeline falhou!")
        return False


def executar_job():
    """Função para executar o pipeline como um job agendado"""
    pipeline = PipelineIntegrado()
    pipeline.executar_pipeline_completo()


if __name__ == "__main__":
    # Verificar se há argumentos para execução programada
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        logger.info("Modo agendado iniciado. Programando execução para 3h da manhã.")
        # Agenda para executar às 3 da manhã
        schedule.every().day.at("03:00").do(executar_job)
        
        # Loop para verificar continuamente o agendamento
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto
    else:
        # Execução direta do pipeline
        pipeline = PipelineIntegrado()
        pipeline.executar_pipeline_completo()