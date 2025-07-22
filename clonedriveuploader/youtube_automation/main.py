import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import google_auth_oauthlib.flow
import json

app = FastAPI()

# Configuração do OAuth
oauth_config = json.loads(os.environ['GOOGLE_OAUTH_SECRETS'])
oauth_flow = google_auth_oauthlib.flow.Flow.from_client_config(
    oauth_config,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]
)

@app.get("/api/config")
async def get_config():
    """Retorna configurações públicas (sem secrets)"""
    return {
        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
        "redirect_uris": os.getenv('REDIRECT_URIS'),
        "scopes": [
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
    }

@app.get("/api/oauth/callback")
async def oauth_callback():
    """Callback OAuth2 (se necessário no futuro)"""
    return RedirectResponse(url="/")

@app.get("/")
async def root():
    """Redireciona para o frontend"""
    return RedirectResponse(url="/index.html")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)