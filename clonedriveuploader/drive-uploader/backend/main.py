#!/usr/bin/env python3
"""
Drive Uploader - Backend FastAPI
Serve arquivos estáticos e fornece endpoints para callback OAuth2 se necessário
"""

import os
import shlex
import re
import subprocess
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import anyio

# Carrega variáveis de ambiente
load_dotenv()

# === FUNÇÕES DE SEGURANÇA ===
def validate_and_sanitize_input(user_input: str, input_type: str = "general") -> str:
    """
    Valida e sanitiza entrada do usuário para prevenir injeção de comando
    """
    if not user_input:
        raise HTTPException(status_code=400, detail="Entrada não pode estar vazia")
    
    # Remove caracteres perigosos - lista expandida
    dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r', '\t', '\\', '"', "'"]
    for char in dangerous_chars:
        if char in user_input:
            raise HTTPException(status_code=400, detail=f"Caractere não permitido: {char}")
    
    # Validações específicas por tipo
    if input_type == "filename":
        # Para nomes de arquivo, permitir apenas caracteres alfanuméricos, pontos, hífens e underscores
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_")
        if not all(c in allowed_chars for c in user_input):
            raise HTTPException(status_code=400, detail="Nome de arquivo contém caracteres inválidos")
        
        # Verificar extensões permitidas
        allowed_extensions = ['.txt', '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.doc', '.docx', '.xls', '.xlsx']
        if not any(user_input.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido")
        
        # Validar tamanho do nome do arquivo
        if len(user_input) > 255:
            raise HTTPException(status_code=400, detail="Nome de arquivo muito longo")
    
    # Usar shlex.quote para escape adicional se necessário
    return shlex.quote(user_input) if input_type == "command_arg" else user_input

async def safe_run_process(command: List[str], **kwargs) -> subprocess.CompletedProcess:
    """
    Executa processo de forma segura usando anyio.run_process
    Sempre usa shell=False e lista de comandos para prevenir injeção
    """
    if not command or not isinstance(command, list):
        raise ValueError("Comando deve ser uma lista não vazia")
    
    # Lista de comandos permitidos (whitelist)
    ALLOWED_COMMANDS = ['file', 'stat', 'wc', 'du', 'head', 'tail', 'ls']
    
    # Verificar se o comando base está na whitelist
    base_command = command[0].lower()
    if base_command not in ALLOWED_COMMANDS:
        raise ValueError(f"Comando não permitido: {base_command}")
    
    # Validar cada argumento do comando
    for arg in command:
        if not isinstance(arg, str):
            raise ValueError("Todos os argumentos devem ser strings")
        
        # Lista expandida de caracteres perigosos
        dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '<', '>', '\n', '\r', '\t', '\\']
        if any(char in arg for char in dangerous_chars):
            raise ValueError(f"Argumento contém caracteres perigosos: {arg}")
        
        # Usar shlex.quote para escape adicional em argumentos de arquivo
        if len(command) > 1 and arg != command[0]:  # Não escapar o comando base
            command[command.index(arg)] = shlex.quote(arg)
    
    try:
        # Sempre usar shell=False e timeout para segurança
        kwargs.setdefault('timeout', 30)
        kwargs.setdefault('shell', False)
        kwargs.setdefault('check', False)
        
        return await anyio.run_process(command, **kwargs)
    except Exception as e:
        raise RuntimeError(f"Erro ao executar comando seguro: {e}")

def validate_file_path(file_path: str) -> Path:
    """
    Valida caminho de arquivo para prevenir path traversal
    """
    try:
        safe_path = Path(file_path).resolve()
        
        # Verificar se não há tentativa de path traversal
        if '..' in str(safe_path) or not str(safe_path).startswith(os.getcwd()):
            raise HTTPException(status_code=400, detail="Caminho de arquivo não permitido")
        
        return safe_path
    except Exception:
        raise HTTPException(status_code=400, detail="Caminho de arquivo inválido")

# === CONFIGURAÇÕES ===
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
CODESPACE_NAME = os.getenv("CODESPACE_NAME", "")
PORT = int(os.getenv("PORT", "5000"))
SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-super-segura-aqui")

print("🚀 Iniciando Drive Uploader Server...")

# VALIDAÇÃO CRÍTICA DE SEGREDOS
if not GOOGLE_CLIENT_ID:
    print("❌ ERRO FATAL: GOOGLE_CLIENT_ID não configurado!")
    print("🔧 Configure o Client ID no Replit Secrets com a chave 'GOOGLE_CLIENT_ID'")
    raise ValueError("GOOGLE_CLIENT_ID é obrigatório")

if not GOOGLE_CLIENT_SECRET:
    print("❌ ERRO FATAL: GOOGLE_CLIENT_SECRET não configurado!")
    print("🔧 Configure o Client Secret no Replit Secrets com a chave 'GOOGLE_CLIENT_SECRET'")
    raise ValueError("GOOGLE_CLIENT_SECRET é obrigatório")

# Log seguro (não expor credenciais)
print(f"📋 Client ID: {GOOGLE_CLIENT_ID[:20]}...{GOOGLE_CLIENT_ID[-4:]} ✅")
print(f"🔐 Client Secret: {'*' * 20}...{GOOGLE_CLIENT_SECRET[-4:]} ✅")

# Criar aplicação FastAPI
app = FastAPI(
    title="Drive Uploader API",
    description="Backend para aplicação de upload ao Google Drive",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# === CONFIGURAR CORS ===
origins = [
    "http://localhost:5000",
    "http://127.0.0.1:5000", 
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

# Adicionar URL do Codespaces se disponível
if CODESPACE_NAME:
    codespace_url = f"https://{CODESPACE_NAME}-5000.app.github.dev"
    origins.append(codespace_url)
    print(f"🌐 Codespace URL: {codespace_url}")
else:
    print("💻 Executando localmente")

# URL específica do usuário
user_codespace = ""
origins.append(user_codespace)
print(f"🎯 URL do usuário: {user_codespace}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adicionar middleware de headers de segurança
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Headers de segurança críticos
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self' https://accounts.google.com https://www.googleapis.com; "
        "script-src 'self' 'unsafe-inline' https://accounts.google.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:;"
    )
    
    # Só adicionar HSTS em HTTPS
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

print(f"🔒 CORS configurado para: {', '.join(origins)}")

# === VERIFICAR ESTRUTURA DE PASTAS ===
current_dir = Path(__file__).parent
frontend_path = current_dir.parent / "frontend"

if not frontend_path.exists():
    print(f"⚠️ Pasta frontend não encontrada: {frontend_path}")
    # Criar pasta frontend se não existir
    frontend_path.mkdir(exist_ok=True)
    print(f"📁 Pasta frontend criada: {frontend_path}")
else:
    print(f"📂 Frontend encontrado: {frontend_path}")

# === ROTAS DA API ===

@app.get("/api/health")
async def health_check():
    """Endpoint de verificação de saúde com validação de segurança"""
    
    # Verificações de segurança
    security_checks = {
        "client_id_configured": bool(GOOGLE_CLIENT_ID),
        "client_secret_configured": bool(GOOGLE_CLIENT_SECRET),
        "secret_key_configured": bool(SECRET_KEY and len(SECRET_KEY) >= 16),
        "client_id_format_valid": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_ID.endswith('.apps.googleusercontent.com')),
        "https_ready": bool(request.url.scheme == "https" if 'request' in locals() else True)
    }
    
    overall_security = all(security_checks.values())
    
    return {
        "status": "ok" if overall_security else "warning",
        "message": "Drive Uploader API funcionando!" if overall_security else "Configuração de segurança incompleta",
        "version": "1.0.0",
        "security": {
            "overall_secure": overall_security,
            "checks": security_checks,
            "recommendations": [
                "Configure GOOGLE_CLIENT_ID no Replit Secrets" if not security_checks["client_id_configured"] else None,
                "Configure GOOGLE_CLIENT_SECRET no Replit Secrets" if not security_checks["client_secret_configured"] else None,
                "Configure SECRET_KEY com pelo menos 16 caracteres" if not security_checks["secret_key_configured"] else None,
                "Verifique formato do Client ID" if not security_checks["client_id_format_valid"] else None
            ]
        },
        "environment": {
            "frontend_path": str(frontend_path),
            "codespace": CODESPACE_NAME or "local",
            "port": PORT
        }
    }

@app.get("/api/config")
async def get_config():
    """Retorna configurações públicas (sem secrets)"""
    
    # Validação adicional em runtime
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500, 
            detail="Configuração OAuth não disponível. Client ID não configurado."
        )
    
    # Validar formato do Client ID (deve terminar com .apps.googleusercontent.com)
    if not GOOGLE_CLIENT_ID.endswith('.apps.googleusercontent.com'):
        raise HTTPException(
            status_code=500,
            detail="Client ID inválido. Verifique a configuração no Google Console."
        )
    
    return {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uris": origins,
        "scopes": [
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/userinfo.profile"
        ],
        "configured": True,
        "environment": "codespace" if CODESPACE_NAME else "local"
    }

@app.get("/api/oauth/callback")
async def oauth_callback(request: Request):
    """Callback OAuth2 (se necessário no futuro)"""
    # Por enquanto, apenas redireciona para a página principal
    # Implementação futura pode processar códigos de autorização aqui
    return RedirectResponse(url="/")

@app.post("/api/validate-file")
async def validate_file(request: Request):
    """Valida arquivo antes do upload para o Google Drive"""
    try:
        data = await request.json()
        filename = data.get("filename", "")
        
        # Validar nome do arquivo
        safe_filename = validate_and_sanitize_input(filename, "filename")
        
        return {
            "valid": True,
            "sanitized_filename": safe_filename,
            "message": "Arquivo válido para upload"
        }
    except HTTPException as e:
        return {
            "valid": False,
            "error": e.detail,
            "message": "Arquivo rejeitado por questões de segurança"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "message": "Erro na validação do arquivo"
        }

@app.post("/api/process-file")
async def process_file_safely(request: Request):
    """
    Exemplo de processamento seguro de arquivo usando anyio.run_process
    """
    try:
        data = await request.json()
        filename = data.get("filename", "")
        operation = data.get("operation", "info")
        
        # Validar nome do arquivo
        safe_filename = validate_and_sanitize_input(filename, "filename")
        safe_path = validate_file_path(safe_filename)
        
        # Verificar se o arquivo existe
        if not safe_path.exists():
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Operações permitidas - usando lista de comandos (seguro)
        if operation == "info":
            # Usar 'file' para obter informações do arquivo
            result = await safe_run_process(["file", str(safe_path)])
            output = result.stdout.decode() if result.stdout else ""
            
        elif operation == "size":
            # Usar 'stat' para obter tamanho do arquivo
            result = await safe_run_process(["stat", "-c", "%s", str(safe_path)])
            output = result.stdout.decode().strip() if result.stdout else "0"
            
        else:
            raise HTTPException(status_code=400, detail="Operação não suportada")
        
        return {
            "success": True,
            "filename": safe_filename,
            "operation": operation,
            "output": output,
            "return_code": result.returncode
        }
        
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erro no processamento do arquivo"
        }

@app.post("/api/safe-edit")
async def safe_edit_content(request: Request):
    """
    Endpoint para edição segura de conteúdo usando Click de forma segura
    """
    try:
        from security_config import SecurityConfig
        import click
        
        data = await request.json()
        content = data.get("content", "")
        
        # Validar conteúdo antes de usar com click.edit()
        safe_content = SecurityConfig.validate_editor_input(content)
        
        # Usar click.edit() de forma segura
        # O click.edit() cria arquivo temporário interno, que é seguro
        edited_content = click.edit(safe_content)
        
        if edited_content is None:
            return {
                "success": False,
                "message": "Edição cancelada pelo usuário"
            }
        
        return {
            "success": True,
            "edited_content": edited_content,
            "message": "Conteúdo editado com sucesso"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erro na edição do conteúdo"
        }

@app.post("/api/safe-launch")
async def safe_launch_url(request: Request):
    """
    Endpoint para abertura segura de URLs usando Click de forma segura
    """
    try:
        from security_config import SecurityConfig
        import click
        
        data = await request.json()
        url = data.get("url", "")
        
        # Validar URL antes de usar com click.launch()
        safe_url = SecurityConfig.validate_url_for_launch(url)
        
        # Usar click.launch() de forma segura
        result = click.launch(safe_url, wait=False)
        
        return {
            "success": True,
            "url": safe_url,
            "result": result,
            "message": "URL aberta com sucesso"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erro ao abrir URL"
        }

# === ROTA RAIZ ===
@app.get("/")
async def root():
    """Redireciona para o frontend"""
    return RedirectResponse(url="/index.html")

# === MONTAR ARQUIVOS ESTÁTICOS ===
try:
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
    print(f"📁 Arquivos estáticos montados: {frontend_path}")
except Exception as e:
    print(f"❌ Erro ao montar arquivos estáticos: {e}")

    # Criar arquivo index.html básico se não existir
    index_file = frontend_path / "index.html"
    if not index_file.exists():
        basic_html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Drive Uploader - Configuração Necessária</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 40px; text-align: center; }
        .error { color: #ea4335; background: #fce8e6; padding: 20px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="error">
        <h1>🚧 Configuração Necessária</h1>
        <p>Os arquivos do frontend não foram encontrados.</p>
        <p>Certifique-se de que a pasta 'frontend' existe com os arquivos corretos.</p>
        <hr>
        <p><strong>API Status:</strong> Funcionando ✅</p>
        <p><strong>Client ID:</strong> Configurado """ + ('✅' if GOOGLE_CLIENT_ID else '❌') + """</p>
        <p><strong>Modo:</strong> """ + (CODESPACE_NAME or "Local") + """</p>
    </div>
</body>
</html>"""

        index_file.write_text(basic_html, encoding='utf-8')
        print(f"📝 Arquivo index.html básico criado")

# === EVENTO DE INICIALIZAÇÃO ===
@app.on_event("startup")
async def startup_event():
    print("=" * 50)
    print("🚀 DRIVE UPLOADER - SERVIDOR INICIADO!")
    print("=" * 50)
    print(f"📊 Porta: {PORT}")
    print(f"📁 Frontend: {frontend_path}")
    print(f"🔑 Client ID: {GOOGLE_CLIENT_ID[:30]}...")
    print(f"🌐 URLs permitidas: {len(origins)} configuradas")

    if CODESPACE_NAME:
        print(f"☁️ Codespace: {user_codespace}")
        print(f"⚠️ IMPORTANTE: Torne a porta {PORT} PÚBLICA no Codespaces!")
    else:
        print(f"💻 Local: http://localhost:{PORT}")

    print("=" * 50)
    print("📖 Documentação da API: /api/docs")
    print("🔍 Health Check: /api/health")
    print("⚙️ Configuração: /api/config")
    print("=" * 50)

# === MAIN ===
if __name__ == "__main__":
    print(f"🌐 Iniciando servidor na porta {PORT}...")
    print(f"🔗 Acesse: http://localhost:{PORT}")

    if CODESPACE_NAME:
        print(f"☁️ Codespace: {user_codespace}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=True,
        log_level="info"
    )
