# 📤 Drive Uploader - Frontend

Interface web moderna para upload de arquivos diretamente ao Google Drive usando OAuth2.

## 🎯 Funcionalidades

### ✅ Autenticação
- **OAuth2 Seguro**: Login com Google Identity Services
- **Informações do Usuário**: Nome, foto e email exibidos
- **Logout Completo**: Revogação de tokens

### ✅ Upload de Arquivos
- **Drag & Drop**: Arraste arquivos diretamente
- **Seleção Múltipla**: Escolha vários arquivos simultaneamente
- **Progresso em Tempo Real**: Barras de progresso individuais
- **Links Diretos**: Acesso imediato aos arquivos no Drive

### ✅ Interface Responsiva
- **Design Moderno**: Interface limpa e profissional
- **Mobile Friendly**: Funciona perfeitamente em celulares
- **Animações Suaves**: Experiência de usuário premium

## 📁 Estrutura dos Arquivos

```
frontend/
├── index.html      # Página de login/autorização
├── upload.html     # Página principal de upload
├── script.js       # Lógica JavaScript (OAuth2 + Upload)
├── style.css       # Estilos CSS modernos
└── README.md       # Esta documentação
```

## ⚙️ Configuração Rápida

### 1. Configurar Credenciais do Google

**Edite `script.js` linha 5:**
```javascript
const CONFIG = {
    CLIENT_ID: '', // ✅ Suas credenciais
    SCOPE: 'https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/userinfo.profile',
    // ...
};
```

### 2. Google Cloud Console

#### a) Authorized JavaScript Origins
Adicione essas URLs no seu OAuth client:
- `http://localhost:8080` (desenvolvimento)
- `https://glowing-computing-machine-4jg6wwrp9qjphq5pq.github.dev` (seu Codespace)

#### b) APIs Necessárias
Ative essas APIs no seu projeto:
- ✅ **Google Drive API**
- ✅ **Google+ API** (para informações do usuário)

### 3. Testar Localmente

```bash
# Servir com Live Server (VS Code)
# Ou qualquer servidor estático na porta 8080
python -m http.server 8080
```

**Acesse**: `http://localhost:8080`

## 🚀 Como Usar

### Fluxo do Usuário

1. **Acesse** `index.html`
2. **Clique** em "Autorizar Google Drive"
3. **Faça login** com sua conta Google
4. **Autorize** as permissões solicitadas
5. **Redirecionado** para `upload.html` automaticamente
6. **Arraste arquivos** ou use "Escolher Arquivos"
7. **Clique** em "Fazer Upload"
8. **Acompanhe** o progresso em tempo real
9. **Acesse** links diretos para os arquivos

### Recursos Disponíveis

- ✅ **Multi-upload**: Upload de vários arquivos simultaneamente
- ✅ **Progresso Visual**: Barra de progresso para cada arquivo
- ✅ **Links Diretos**: Botões para abrir arquivos no Google Drive
- ✅ **Tratamento de Erros**: Mensagens claras em caso de problemas
- ✅ **Logout Seguro**: Revoga tokens e limpa sessão

## 🔧 Personalização

### Alterar Escopos de Permissão

```javascript
// Para acesso completo ao Drive:
SCOPE: 'https://www.googleapis.com/auth/drive',

// Para apenas arquivos criados pela app (padrão - mais seguro):
SCOPE: 'https://www.googleapis.com/auth/drive.file',
```

### Upload para Pasta Específica

```javascript
// Em script.js, função uploadFile, altere metadata:
const metadata = {
    name: file.name,
    parents: ['1A2B3C4D5E6F7G8H'] // ID da pasta no Google Drive
};
```

### Customizar Cores

```css
/* Em style.css, altere as variáveis: */
:root {
    --primary-color: #4285f4;    /* Azul Google */
    --success-color: #34a853;    /* Verde */
    --error-color: #ea4335;      /* Vermelho */
    /* ... */
}
```

## 🐛 Solução de Problemas

### ❌ "Origin not authorized"
**Solução**: Adicione sua URL no Google Cloud Console
1. Acesse: https://console.cloud.google.com/apis/credentials
2. Edite seu OAuth client ID
3. Em "Authorized JavaScript origins", adicione:
   - `http://localhost:8080`
   - `https://seu-codespace-8080.app.github.dev`

### ❌ "CLIENT_ID not found"
**Solução**: Configure CLIENT_ID no script.js
```javascript
// Linha 5 do script.js:
CLIENT_ID: 'SEU_CLIENT_ID_REAL_AQUI',
```

### ❌ "Upload failed 401"
**Solução**: Token inválido
1. Verifique se Google Drive API está ativada
2. Faça logout e login novamente
3. Verifique escopos de permissão

### ❌ "CORS Error"
**Solução**: Use servidor web adequado
- ❌ Não abra arquivos HTML diretamente no browser
- ✅ Use Live Server, http-server ou similar
- ✅ Use o backend FastAPI fornecido

## 📱 Compatibilidade

### Navegadores Suportados
- ✅ **Chrome** 60+ (recomendado)
- ✅ **Firefox** 60+
- ✅ **Safari** 12+
- ✅ **Edge** 79+

### Dispositivos
- ✅ **Desktop**: Funcionalidade completa
- ✅ **Mobile**: Interface adaptada, drag & drop limitado
- ✅ **Tablet**: Experiência otimizada

## 🔒 Segurança

### Permissões Mínimas
O app solicita apenas:
- `drive.file`: Acesso aos arquivos que criar (não a todo o Drive)
- `userinfo.profile`: Nome e foto do usuário

### Client-side Only
- ✅ **Sem servidor**: Tokens não são armazenados em servidor
- ✅ **Temporário**: Access tokens expiram em 1 hora
- ✅ **Revogação**: Logout revoga tokens explicitamente

## 📊 Estatísticas

- **Total de linhas**: ~800 linhas de código
- **JavaScript**: ~500 linhas (lógica principal)
- **CSS**: ~300 linhas (estilos responsivos)  
- **HTML**: ~100 linhas (2 páginas)
- **Compatibilidade**: 95%+ navegadores modernos

## 🆘 Suporte

### Documentação Oficial
- [Google Drive API v3](https://developers.google.com/drive/api/v3/reference)
- [Google Identity Services](https://developers.google.com/identity/gsi/web)

### Links Úteis
- [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
- [Google Cloud Console](https://console.cloud.google.com/)
- [Drive API Explorer](https://developers.google.com/drive/api/v3/reference)

---

**Desenvolvido com ❤️ usando Google Drive API v3 e JavaScript moderno.**