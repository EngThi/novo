# Pipeline Integrado: YouTube Automation + Google Drive Uploader

Este projeto automatiza a criação de vídeos baseados em um tópico e faz o upload do resultado final (vídeo e todos os assets) para o Google Drive, preservando a estrutura de pastas.

## Funcionalidades

- **Geração Automática de Vídeo**: Cria um vídeo completo a partir de um único tema, incluindo roteiro (placeholder), narração (TTS), imagens e montagem final.
- **Estrutura Organizada**: Salva todos os arquivos gerados em uma pasta de projeto única e bem-estruturada (ex: `output/2025-07-20_Misterios_do_Folclore_Brasileiro/`).
- **Upload para o Google Drive**: Envia a pasta inteira do projeto para a sua conta do Google Drive, recriando a hierarquia de pastas (`assets`, `final`, etc.).
- **Autenticação Simplificada**: O sistema de autenticação com o Google Drive é feito via console na primeira execução e o token é salvo para usos futuros.

## Como Usar

### 1. Pré-requisitos

- Python 3.9+
- Conta do Google

### 2. Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <URL_DO_REPOSITORIO>
    cd <NOME_DO_DIRETORIO>
    ```

2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # No Windows: .\venv\Scripts\activate
    ```

3.  **Instale as dependências:**
    O projeto possui dois módulos com dependências separadas. Instale ambas:
    ```bash
    pip install -r youtube_automation/requirements.txt
    pip install -r drive-uploader/backend/requirements.txt
    ```

### 3. Configuração

1.  **Credenciais do Google Drive:**
    - Acesse o [Google Cloud Console](https://console.cloud.google.com/).
    - Crie um novo projeto ou selecione um existente.
    - Ative a **API do Google Drive**.
    - Vá para "Credenciais", clique em "Criar Credenciais" e selecione "ID do cliente OAuth".
    - Escolha "Aplicativo para computador".
    - Faça o download do arquivo JSON de credenciais. **Renomeie este arquivo para `google-drive-credentials.json`** e coloque-o na raiz do projeto.

2.  **Arquivo de Ambiente (`.env`):**
    - Crie um arquivo chamado `.env` na raiz do projeto.
    - Adicione a seguinte linha, apontando para o seu arquivo de credenciais:
      ```
      DRIVE_CREDENTIALS_PATH="google-drive-credentials.json"
      ```

### 4. Execução do Pipeline

Com o ambiente virtual ativado e as configurações prontas, execute o pipeline com um único comando:

```bash
python pipeline_integrado.py
```

- **Na primeira vez**, você será solicitado a seguir um link no seu terminal para autorizar o acesso à sua conta do Google Drive. Após a autorização, um arquivo `token.json` será criado, e as execuções futuras serão automáticas.

- Opcionalmente, você pode mudar o tema do vídeo editando a variável `VIDEO_TOPIC` no arquivo `pipeline_integrado.py`.

### 5. Resultado

Após a execução, você encontrará:

- Uma nova pasta em `youtube_automation/output/` contendo todos os arquivos do vídeo.
- Uma nova pasta no seu Google Drive com o mesmo nome, contendo todos os arquivos e subpastas do projeto.
