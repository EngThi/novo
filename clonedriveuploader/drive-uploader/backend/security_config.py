
"""
Configurações de Segurança - Drive Uploader
Centraliza todas as validações e configurações de segurança
"""

import shlex
import re
from typing import List, Dict, Any
from pathlib import Path

class SecurityConfig:
    """Configurações centralizadas de segurança"""
    
    # Caracteres perigosos que devem ser bloqueados
    DANGEROUS_CHARS = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r', '\t']
    
    # Extensões de arquivo permitidas
    ALLOWED_EXTENSIONS = [
        '.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',
        '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.wav', '.aac', '.m4a', '.ogg',
        '.zip', '.rar', '.tar', '.gz'
    ]
    
    # Extensões específicas para mídia
    MEDIA_EXTENSIONS = ['.mp3', '.mp4', '.avi', '.mov', '.wmv', '.wav', '.aac', '.m4a', '.ogg']
    
    # Tamanho máximo de arquivo (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    # Padrão para nomes de arquivo seguros
    SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Valida se o nome do arquivo é seguro"""
        if not filename or len(filename) > 255:
            return False
        
        # Verificar caracteres perigosos
        for char in SecurityConfig.DANGEROUS_CHARS:
            if char in filename:
                return False
        
        # Verificar padrão seguro
        if not SecurityConfig.SAFE_FILENAME_PATTERN.match(filename):
            return False
        
        # Verificar extensão
        return any(filename.lower().endswith(ext) for ext in SecurityConfig.ALLOWED_EXTENSIONS)
    
    @staticmethod
    def sanitize_command_arg(arg: str) -> str:
        """Sanitiza argumentos para comandos do sistema"""
        return shlex.quote(str(arg))
    
    @staticmethod
    def validate_path(path: str) -> Path:
        """Valida e resolve path de forma segura"""
        safe_path = Path(path).resolve()
        
        # Verificar se não há tentativa de path traversal
        if '..' in str(safe_path) or str(safe_path).startswith('/'):
            raise ValueError("Path traversal detectado")
        
        return safe_path
    
    @staticmethod
    def validate_command_list(command: list) -> bool:
        """
        Valida lista de comandos para anyio.run_process com validação rigorosa
        """
        if not command or not isinstance(command, list):
            return False
        
        # Verificar se todos os itens são strings
        if not all(isinstance(arg, str) for arg in command):
            return False
        
        # Lista de comandos explicitamente permitidos (whitelist)
        allowed_commands = ['file', 'stat', 'wc', 'du', 'head', 'tail', 'ls']
        if command[0].lower() not in allowed_commands:
            return False
        
        # Lista expandida de caracteres perigosos
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r', '\t', '\\', '"', "'"]
        
        # Verificar caracteres perigosos em cada argumento
        for arg in command:
            if any(char in arg for char in dangerous_chars):
                return False
        
        # Verificar comandos explicitamente perigosos
        dangerous_commands = [
            'rm', 'del', 'format', 'fdisk', 'mkfs', 'dd', 'chmod', 'chown',
            'sudo', 'su', 'passwd', 'useradd', 'userdel', 'kill', 'killall',
            'systemctl', 'service', 'mount', 'umount', 'wget', 'curl', 'nc'
        ]
        if command[0].lower() in dangerous_commands:
            return False
        
        return True
    
    @staticmethod
    def build_safe_command(base_command: str, args: list) -> list:
        """
        Constrói comando seguro para anyio.run_process com validação rigorosa
        """
        if not base_command or not isinstance(args, list):
            raise ValueError("Comando base e argumentos devem ser válidos")
        
        # Verificar se o comando base está na whitelist
        allowed_commands = ['file', 'stat', 'wc', 'du', 'head', 'tail', 'ls']
        if base_command.lower() not in allowed_commands:
            raise ValueError(f"Comando não permitido: {base_command}")
        
        command = [base_command]
        

    
    @staticmethod
    def validate_media_filename(filename: str) -> bool:
        """Valida nome de arquivo de mídia especificamente"""
        if not filename or len(filename) > 255:
            return False
        
        # Verificar caracteres perigosos
        for char in SecurityConfig.DANGEROUS_CHARS:
            if char in filename:
                return False
        
        # Padrão específico para arquivos de mídia
        media_pattern = re.compile(r'^[a-zA-Z0-9\s\._-]+\.(mp3|mp4|avi|mov|wmv|wav|aac|m4a|ogg)$', re.IGNORECASE)
        return bool(media_pattern.match(filename))
    
    @staticmethod
    def sanitize_subprocess_command(command_list: list) -> list:
        """
        Sanitiza lista de comandos para subprocess com validação rigorosa
        """
        if not isinstance(command_list, list):
            raise ValueError("Comando deve ser uma lista")
        
        sanitized = []
        for arg in command_list:
            if not isinstance(arg, str):
                raise ValueError("Todos os argumentos devem ser strings")
            
            # Verificar caracteres extremamente perigosos
            dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r']
            if any(char in arg for char in dangerous_chars):
                raise ValueError(f"Argumento contém caracteres perigosos: {arg}")
            
            sanitized.append(arg)
        
        return sanitized


        # Validar e sanitizar cada argumento
        for arg in args:
            if not isinstance(arg, str):
                raise ValueError("Todos os argumentos devem ser strings")
            
            # Verificar caracteres perigosos antes do escape
            dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r', '\t', '\\']
            if any(char in arg for char in dangerous_chars):
                raise ValueError(f"Argumento contém caracteres perigosos: {arg}")
            
            # Usar shlex.quote para escape seguro
            safe_arg = shlex.quote(arg)
            command.append(safe_arg)
        
        # Validar comando final (sem shlex.quote para validação)
        temp_command = [base_command] + args
        if not SecurityConfig.validate_command_list(temp_command):
            raise ValueError("Comando contém elementos perigosos")
        
        return command
    
    @staticmethod
    def validate_editor_input(content: str) -> str:
        """
        Valida conteúdo para uso com click.edit() prevenindo injeção
        """
        if not content or not isinstance(content, str):
            raise ValueError("Conteúdo deve ser uma string válida")
        
        # Limitar tamanho do conteúdo (10MB max)
        if len(content) > 10 * 1024 * 1024:
            raise ValueError("Conteúdo muito grande para edição")
        
        # Remover caracteres de controle perigosos
        safe_content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        
        return safe_content
    
    @staticmethod
    def validate_url_for_launch(url: str) -> str:
        """
        Valida URL para uso com click.launch() prevenindo injeção
        """
        if not url or not isinstance(url, str):
            raise ValueError("URL deve ser uma string válida")
        
        # Verificar protocolo permitido
        allowed_protocols = ['http://', 'https://', 'mailto:']
        if not any(url.lower().startswith(proto) for proto in allowed_protocols):
            raise ValueError("Protocolo de URL não permitido")
        
        # Verificar caracteres perigosos em URL
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r', '\t', '\\', '"', "'"]
        if any(char in url for char in dangerous_chars):
            raise ValueError("URL contém caracteres perigosos")
        
        # Validar formato básico de URL
        if not re.match(r'^https?://[^\s]+$|^mailto:[^\s]+$', url):
            raise ValueError("Formato de URL inválido")
        
        return url
    
    @staticmethod
    def validate_pager_content(content: str) -> str:
        """
        Valida conteúdo para uso com click.echo_via_pager() prevenindo injeção
        """
        if not content or not isinstance(content, str):
            raise ValueError("Conteúdo deve ser uma string válida")
        
        # Limitar tamanho do conteúdo (50MB max para pager)
        if len(content) > 50 * 1024 * 1024:
            raise ValueError("Conteúdo muito grande para paginação")
        
        # Remover caracteres de controle perigosos mas manter quebras de linha
        safe_content = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)
        
        return safe_content

# Configurações específicas para Google Drive
GOOGLE_DRIVE_SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/userinfo.profile'
]

# Comandos permitidos para anyio.run_process
ALLOWED_COMMANDS = [
    'file',      # Obter informações de arquivo
    'stat',      # Estatísticas de arquivo
    'du',        # Uso de disco
    'wc',        # Contar linhas/palavras
    'head',      # Mostrar início do arquivo
    'tail',      # Mostrar final do arquivo
    'ls',        # Listar arquivos (com restrições)
]

# Configurações para anyio.run_process
ANYIO_PROCESS_CONFIG = {
    'timeout': 30,  # Timeout de 30 segundos
    'check': False,  # Não levantar exceção em código de saída não-zero
    'shell': False,  # SEMPRE False para segurança
}

# Headers de segurança para respostas HTTP
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
}
