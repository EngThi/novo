# ⚙️ Drive Uploader - Backend (FastAPI)

Servidor Python FastAPI que serve os arquivos estáticos do frontend e fornece APIs para futuras extensões.

## 🎯 Funcionalidades

### ✅ Servidor de Arquivos Estáticos
- **Serve Frontend**: Monta a pasta `frontend/` como arquivos estáticos
- **HTML Support**: Roteamento automático para arquivos HTML
- **CORS Configurado**: Permite requisições do frontend

### ✅ API Endpoints
- **Health Check**: `/api/health` - Status do servidor
- **Configuração**: `/api/config` - Informações públicas
- **OAuth Callback**: `/api/oauth/callback` - Para futuras extensões

### ✅ GitHub Codespaces Ready
- **Detecção Automática**: Identifica ambiente Codespaces
- **URLs Dinâmicas**: Configura CORS automaticamente
- **Port Forwarding**: Suporte a portas públicas

## 📁 Estrutura dos Arquivos

```
backend/
├── main.py           # Aplicação FastAPI principal
├── requirements.txt  # Dependências Python
├── .env.example      # Exemplo de configuração
└── README.md         # Esta documentação
```

## 🚀 Configuração e Execução

### 1. Ambiente Virtual (Recomendado)

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate
```

### 2. Instalar Dependências

```bash
# Instalar bibliotecas
pip install -r requirements.txt

# Ou instalar manualmente:
pip install fastapi uvicorn[standard] python-dotenv python-multipart
```

### 3. Configurar Credenciais

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar com suas credenciais
nano .env  # ou use seu editor preferido
```

#### Arquivo `.env` exemplo:
```bash
# Suas credenciais do Google Cloud Console
GOOGLE_CLIENT_ID=1060201687476-0c6m7fb4ttsmg84uibe6jh8utbmplr11.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

# Configuração do servidor
PORT=8080

# Segurança (altere em produção)
SECRET_KEY=sua-chave-secreta-super-segura-aqui
```

### 4. Executar Servidor

```bash
# Método 1: Usar script principal
python main.py

# Método 2: Usar uvicorn diretamente
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Método 3: Porta customizada
PORT=3000 python main.py
```

**Saída esperada:**
```
🚀 Iniciando Drive Uploader Server...
📋 Client ID: 1060201687476-0c6m...
🔐 Secret configurado: True
💻 Executando localmente
🔒 CORS configurado para: http://localhost:8080, ...
📂 Frontend encontrado: /path/to/frontend
📁 Arquivos estáticos montados: /path/to/frontend
==================================================
🚀 DRIVE UPLOADER - SERVIDOR INICIADO!
==================================================
📊 Porta: 8080
📁 Frontend: /path/to/frontend
🔑 Client ID: 1060201687476-0c6m7fb4ttsmg84uibe6...
🌐 URLs permitidas: 5 configuradas
💻 Local: http://localhost:8080
==================================================
```

## ☁️ GitHub Codespaces

### Setup Automático

No Codespaces, o servidor detecta automaticamente o ambiente e configura:

```bash
# 1. Terminal automático do Codespaces
cd backend

# 2. Configurar ambiente
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurar credenciais
cp .env.example .env
# Edite .env com suas credenciais

# 4. Executar
python main.py
```

### ⚠️ IMPORTANTE: Tornar Porta Pública

Após iniciar o servidor:

1. **Abra aba "PORTS"** no VS Code do Codespaces
2. **Encontre porta 8080** na lista
3. **Clique com botão direito** na porta
4. **Selecione "Port Visibility" > "Public"**
5. **Acesse a URL gerada**: `https://glowing-computing-machine-4jg6wwrp9qjphq5pq.github.dev`

### URLs de Desenvolvimento

O servidor está configurado para aceitar requisições de:

- `http://localhost:8080` (desenvolvimento local)
- `https://glowing-computing-machine-4jg6wwrp9qjphq5pq.github.dev` (seu Codespace)
- Outras URLs detectadas automaticamente

## 📖 API Endpoints

### GET `/api/health`
Verifica status do servidor

**Resposta:**
```json
{
  "status": "ok",
  "message": "Drive Uploader API funcionando!",
  "version": "1.0.0",
  "client_id_configured": true,
  "frontend_path": "/path/to/frontend",
  "codespace": "glowing-computing-machine-4jg6wwrp9qjphq5pq"
}
```

### GET `/api/config`
Retorna configurações públicas (sem secrets)

**Resposta:**
```json
{
  "client_id": "1060201687476-0c6m7fb4ttsmg84uibe6jh8utbmplr11.apps.googleusercontent.com",
  "redirect_uris": ["http://localhost:8080", "https://..."],
  "scopes": [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/userinfo.profile"
  ]
}
```

### GET `/api/docs`
Documentação interativa da API (Swagger UI)

### GET `/api/redoc`
Documentação alternativa da API (ReDoc)

## 🔧 Personalização

### Alterar Porta

```bash
# Método 1: Variável de ambiente
export PORT=3000
python main.py

# Método 2: Arquivo .env
PORT=3000

# Método 3: Linha de comando
PORT=3000 python main.py
```

### Adicionar CORS Origins

```python
# Em main.py, adicione URLs:
origins = [
    "http://localhost:8080",
    "https://meusite.com",        # ← Adicione suas URLs
    "https://app.exemplo.com"     # ← Aqui
]
```

### Endpoints Customizados

```python
# Adicione em main.py:
@app.get("/api/custom")
async def custom_endpoint():
    return {"message": "Meu endpoint customizado!"}
```

## 🐛 Solução de Problemas

### ❌ "Port already in use"
**Problema**: Porta 8080 já está sendo usada

```bash
# Solução 1: Usar porta diferente
PORT=3000 python main.py

# Solução 2: Matar processo na porta 8080 (Linux/Mac)
lsof -ti:8080 | xargs kill -9

# Solução 3: Verificar processos (Windows)
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### ❌ "ModuleNotFoundError: No module named 'fastapi'"
**Problema**: Dependências não instaladas

```bash
# Solução:
pip install -r requirements.txt

# Ou verificar ambiente virtual ativo:
which python  # Deve apontar para venv
```

### ❌ "Frontend files not found"
**Problema**: Pasta frontend não existe

```bash
# Solução: Verificar estrutura do projeto
project/
├── frontend/     ← Deve existir
│   ├── index.html
│   └── ...
└── backend/
    ├── main.py   ← Você está aqui
    └── ...
```

### ❌ CORS Errors
**Problema**: Requisições bloqueadas por CORS

```python
# Solução: Adicionar origem em main.py
origins = [
    "http://localhost:8080",
    "https://sua-url-aqui.com"  # ← Adicione sua URL
]
```

## 📊 Dependências

### Principais Bibliotecas

```python
fastapi==0.104.1          # Framework web moderno
uvicorn[standard]==0.24.0 # Servidor ASGI de alta performance
python-dotenv==1.0.0      # Carregamento de variáveis de ambiente
python-multipart==0.0.6   # Suporte a multipart/form-data
```

### Recursos Incluídos

- ✅ **Hot Reload**: Reinicialização automática durante desenvolvimento
- ✅ **Documentação Automática**: Swagger UI e ReDoc
- ✅ **Validação de Dados**: Pydantic integrado
- ✅ **Async Support**: Suporte completo a operações assíncronas

## 🚀 Deploy para Produção

### Configurações de Produção

```bash
# Variáveis de ambiente recomendadas
export GOOGLE_CLIENT_ID="client-id-producao"
export GOOGLE_CLIENT_SECRET="secret-producao"  
export SECRET_KEY="chave-super-segura-256-bits"
export PORT=80
```

### Servidor de Produção

```bash
# Usar Gunicorn para produção
pip install gunicorn

# Executar com múltiplos workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080
```

### Docker (Exemplo)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
WORKDIR /app/backend
EXPOSE 8080
CMD ["python", "main.py"]
```

## 📈 Monitoramento

### Health Check

```bash
# Verificar se servidor está funcionando
curl http://localhost:8080/api/health

# Resposta esperada:
# {"status":"ok","message":"Drive Uploader API funcionando!",...}
```

### Logs

```bash
# Visualizar logs em tempo real
python main.py

# Com nível de log específico
uvicorn main:app --log-level debug
```

## 🆘 Suporte

### Links Úteis
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Python Dotenv](https://pypi.org/project/python-dotenv/)

### Debugging

```python
# Adicionar logs de debug em main.py:
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

**FastAPI Server para Drive Uploader - Configurado com suas credenciais ✅**