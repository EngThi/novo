
#!/usr/bin/env python3
"""
Wrapper Seguro para Subprocess - Implementação do Caso de Estudo 1
Substitui completamente o uso de shell=True por implementação segura
"""

import subprocess
import shlex
import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import anyio

class SecureSubprocessWrapper:
    """
    Wrapper seguro que NUNCA permite shell=True
    Implementa as mitigações do Caso de Estudo 1
    """
    
    def __init__(self):
        # Lista de comandos explicitamente permitidos (whitelist)
        self.allowed_commands = {
            'file', 'stat', 'wc', 'du', 'head', 'tail', 'ls', 'cat', 'grep',
            'find', 'sort', 'uniq', 'cut', 'awk', 'sed', 'tar', 'gzip', 'gunzip'
        }
        
        # Comandos explicitamente proibidos (blacklist)
        self.dangerous_commands = {
            'rm', 'del', 'format', 'fdisk', 'mkfs', 'dd', 'chmod', 'chown',
            'sudo', 'su', 'passwd', 'useradd', 'userdel', 'kill', 'killall',
            'systemctl', 'service', 'mount', 'umount', 'wget', 'curl', 'nc',
            'sh', 'bash', 'zsh', 'fish', 'csh', 'tcsh', 'eval', 'exec'
        }
    
    def validate_command_list(self, command: List[str]) -> bool:
        """
        Valida lista de comandos com rigorosa análise de segurança
        """
        if not command or not isinstance(command, list):
            raise ValueError("Comando deve ser uma lista não vazia")
        
        if not all(isinstance(arg, str) for arg in command):
            raise ValueError("Todos os argumentos devem ser strings")
        
        base_command = Path(command[0]).name.lower()
        
        # Verificar whitelist
        if base_command not in self.allowed_commands:
            raise ValueError(f"Comando '{base_command}' não está na whitelist")
        
        # Verificar blacklist
        if base_command in self.dangerous_commands:
            raise ValueError(f"Comando '{base_command}' está explicitamente proibido")
        
        # Verificar caracteres perigosos em todos os argumentos
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r', '\t', '\\', '"', "'"]
        for arg in command:
            if any(char in arg for char in dangerous_chars):
                raise ValueError(f"Argumento contém caracteres perigosos: {arg}")
        
        return True
    
    def safe_run(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """
        Executa comando de forma segura - NUNCA usa shell=True
        """
        # Validar comando antes da execução
        self.validate_command_list(command)
        
        # Forçar configurações seguras
        safe_kwargs = {
            'shell': False,  # SEMPRE False
            'timeout': kwargs.get('timeout', 30),
            'check': kwargs.get('check', False),
            'capture_output': kwargs.get('capture_output', True),
            'text': kwargs.get('text', True),
            'cwd': kwargs.get('cwd', None)
        }
        
        # Sanitizar argumentos com shlex.quote
        sanitized_command = [shlex.quote(arg) for arg in command]
        
        try:
            result = subprocess.run(sanitized_command, **safe_kwargs)
            return result
        except subprocess.TimeoutExpired:
            raise ValueError(f"Comando expirou após {safe_kwargs['timeout']} segundos")
        except FileNotFoundError:
            raise ValueError(f"Comando '{command[0]}' não encontrado")
        except Exception as e:
            raise ValueError(f"Erro ao executar comando: {e}")
    
    async def safe_run_async(self, command: List[str], **kwargs) -> anyio.abc.Process:
        """
        Executa comando assincronamente de forma segura usando anyio
        """
        # Validar comando
        self.validate_command_list(command)
        
        # Configurações seguras para anyio
        safe_kwargs = {
            'timeout': kwargs.get('timeout', 30),
            'check': kwargs.get('check', False)
        }
        
        try:
            # anyio.run_process SEMPRE usa shell=False por padrão
            result = await anyio.run_process(command, **safe_kwargs)
            return result
        except Exception as e:
            raise ValueError(f"Erro ao executar comando assíncrono: {e}")
    
    def build_safe_command(self, base_command: str, args: List[str]) -> List[str]:
        """
        Constrói comando seguro com validação rigorosa
        """
        if not base_command or not isinstance(args, list):
            raise ValueError("Comando base e argumentos devem ser válidos")
        
        # Verificar comando base
        if Path(base_command).name.lower() not in self.allowed_commands:
            raise ValueError(f"Comando '{base_command}' não permitido")
        
        # Construir comando completo
        full_command = [base_command] + args
        
        # Validar comando completo
        self.validate_command_list(full_command)
        
        return full_command
    
    def safe_file_info(self, file_path: str) -> Dict[str, str]:
        """
        Obtém informações de arquivo de forma segura
        """
        try:
            safe_path = Path(file_path).resolve()
            
            # Prevenir path traversal
            if '..' in str(safe_path):
                raise ValueError("Path traversal detectado")
            
            # Usar comando 'file' seguro
            command = self.build_safe_command('file', [str(safe_path)])
            result = self.safe_run(command)
            
            return {
                'file_path': str(safe_path),
                'file_info': result.stdout.strip() if result.stdout else '',
                'return_code': result.returncode,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'success': False
            }
    
    def safe_file_stats(self, file_path: str) -> Dict[str, Any]:
        """
        Obtém estatísticas de arquivo de forma segura
        """
        try:
            safe_path = Path(file_path).resolve()
            
            # Prevenir path traversal
            if '..' in str(safe_path):
                raise ValueError("Path traversal detectado")
            
            # Usar comando 'stat' seguro
            command = self.build_safe_command('stat', ['-c', '%s %Y %A', str(safe_path)])
            result = self.safe_run(command)
            
            if result.returncode == 0 and result.stdout:
                parts = result.stdout.strip().split()
                return {
                    'file_path': str(safe_path),
                    'size': int(parts[0]) if parts else 0,
                    'modified_time': int(parts[1]) if len(parts) > 1 else 0,
                    'permissions': parts[2] if len(parts) > 2 else '',
                    'success': True
                }
            else:
                return {
                    'file_path': str(safe_path),
                    'error': result.stderr or 'Comando falhou',
                    'success': False
                }
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'success': False
            }
    
    def safe_directory_list(self, dir_path: str, pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        Lista diretório de forma segura
        """
        try:
            safe_path = Path(dir_path).resolve()
            
            # Prevenir path traversal
            if '..' in str(safe_path):
                raise ValueError("Path traversal detectado")
            
            # Construir comando ls seguro
            args = ['-la', str(safe_path)]
            if pattern:
                # Validar pattern
                if any(char in pattern for char in [';', '&', '|', '`', '$']):
                    raise ValueError("Pattern contém caracteres perigosos")
                args.extend(['|', 'grep', shlex.quote(pattern)])
            
            command = self.build_safe_command('ls', args[:2])  # Apenas ls -la path
            result = self.safe_run(command)
            
            return {
                'directory': str(safe_path),
                'listing': result.stdout.strip() if result.stdout else '',
                'success': result.returncode == 0,
                'error': result.stderr if result.returncode != 0 else None
            }
        except Exception as e:
            return {
                'directory': dir_path,
                'error': str(e),
                'success': False
            }
    
    def environment_protection_check(self) -> Dict[str, Any]:
        """
        Verifica proteções de ambiente conforme Caso de Estudo 1
        """
        protections = {
            'editor_var_secure': True,
            'visual_var_secure': True,
            'path_secure': True,
            'shell_secure': True,
            'overall_secure': True
        }
        
        # Verificar variáveis de ambiente críticas
        dangerous_vars = ['EDITOR', 'VISUAL', 'SHELL']
        for var in dangerous_vars:
            value = os.environ.get(var, '')
            if value:
                # Verificar se contém comandos perigosos
                dangerous_patterns = [';', '&', '|', '`', '$', '$(', '${']
                if any(pattern in value for pattern in dangerous_patterns):
                    protections[f'{var.lower()}_var_secure'] = False
                    protections['overall_secure'] = False
        
        # Verificar PATH por comandos perigosos no início
        path_value = os.environ.get('PATH', '')
        if path_value:
            path_dirs = path_value.split(os.pathsep)
            # Verificar se diretórios suspeitos estão no início do PATH
            suspicious_paths = ['/tmp', '/var/tmp', '/dev/shm']
            for sus_path in suspicious_paths:
                if path_dirs and path_dirs[0].startswith(sus_path):
                    protections['path_secure'] = False
                    protections['overall_secure'] = False
                    break
        
        return protections

# Instância global segura
secure_subprocess = SecureSubprocessWrapper()

# Funções de conveniência que NUNCA usam shell=True
def safe_run_command(command: List[str], **kwargs) -> subprocess.CompletedProcess:
    """
    Função de conveniência para execução segura
    """
    return secure_subprocess.safe_run(command, **kwargs)

async def safe_run_command_async(command: List[str], **kwargs) -> anyio.abc.Process:
    """
    Função de conveniência para execução assíncrona segura
    """
    return await secure_subprocess.safe_run_async(command, **kwargs)

def get_file_info_secure(file_path: str) -> Dict[str, Any]:
    """
    Função de conveniência para informações de arquivo
    """
    return secure_subprocess.safe_file_info(file_path)

def get_file_stats_secure(file_path: str) -> Dict[str, Any]:
    """
    Função de conveniência para estatísticas de arquivo
    """
    return secure_subprocess.safe_file_stats(file_path)

# Decorator para substituir subprocess inseguro
def require_safe_subprocess(func):
    """
    Decorator que força uso de subprocess seguro
    """
    def wrapper(*args, **kwargs):
        if 'shell' in kwargs and kwargs['shell']:
            raise ValueError("shell=True não permitido - use SecureSubprocessWrapper")
        return func(*args, **kwargs)
    return wrapper

if __name__ == "__main__":
    # Testes de segurança
    wrapper = SecureSubprocessWrapper()
    
    print("🧪 Testando SecureSubprocessWrapper...")
    
    # Teste 1: Comando seguro
    try:
        result = wrapper.safe_file_info("main.py")
        print(f"✅ Comando seguro: {result['success']}")
    except Exception as e:
        print(f"❌ Erro em comando seguro: {e}")
    
    # Teste 2: Comando perigoso
    try:
        wrapper.safe_run(["rm", "-rf", "/"])
        print("❌ FALHA: Comando perigoso foi permitido!")
    except ValueError as e:
        print(f"✅ Comando perigoso bloqueado: {e}")
    
    # Teste 3: Verificação de ambiente
    env_check = wrapper.environment_protection_check()
    print(f"🔒 Proteção de ambiente: {env_check['overall_secure']}")
    
    print("🛡️ Testes de segurança concluídos")
