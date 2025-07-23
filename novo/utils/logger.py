
#!/usr/bin/env python3
"""
Sistema de Logging Centralizado e Inteligente
"""

import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class PipelineLogger:
    """Logger centralizado para todo o pipeline"""
    
    def __init__(self, name: str = "pipeline", log_dir: Optional[Path] = None):
        self.name = name
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Evitar duplicação de handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura handlers de logging"""
        
        # Formato das mensagens
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Handler para arquivo
        log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # Adicionar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log de informação"""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log de erro"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """Log de aviso"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Log de debug"""
        self.logger.debug(message)
    
    def success(self, message: str):
        """Log de sucesso (como info com prefixo)"""
        self.logger.info(f"✅ {message}")
    
    def step(self, step_name: str, details: str = ""):
        """Log de etapa do pipeline"""
        message = f"🔄 {step_name}"
        if details:
            message += f" - {details}"
        self.logger.info(message)

# Singleton para usar em todo o projeto
_global_logger = None

def get_logger(name: str = "pipeline") -> PipelineLogger:
    """Obtém logger global"""
    global _global_logger
    if _global_logger is None:
        _global_logger = PipelineLogger(name)
    return _global_logger
