
# 🔒 Guia de Configuração Segura - Drive Uploader

## 📋 Configuração Obrigatória de Segredos

### 1. Acessar Replit Secrets
1. No painel lateral esquerdo, clique no ícone 🔑 **"Secrets"**
2. Ou use Ctrl+Shift+P e digite "Secrets"

### 2. Configurar Credenciais Google OAuth

**GOOGLE_CLIENT_ID**
- **Key**: `GOOGLE_CLIENT_ID`
- **Value**: Seu Client ID do Google Console (ex: `123456-abc.apps.googleusercontent.com`)

**GOOGLE_CLIENT_SECRET**
- **Key**: `GOOGLE_CLIENT_SECRET` 
- **Value**: Seu Client Secret do Google Console (ex: `GOCSPX-abc123...`)

### 3. Configurar Chave de Segurança

**SECRET_KEY**
- **Key**: `SECRET_KEY`
- **Value**: Uma string aleatória longa (mín. 32 caracteres)
- **Exemplo**: `minha-super-chave-secreta-aleatoria-2025`

## ⚠️ Verificações de Segurança Implementadas

### ✅ Validações Automáticas
- Client ID formato válido (.apps.googleusercontent.com)
- Secrets obrigatórios presentes
- Headers de segurança aplicados
- CSP (Content Security Policy) configurado
- Logs sanitizados (sem exposição de credenciais)

### ✅ Proteções Implementadas
- **XSS Protection**: Headers X-XSS-Protection
- **Clickjacking**: X-Frame-Options: DENY  
- **MIME Sniffing**: X-Content-Type-Options: nosniff
- **Content Security Policy**: Restringe recursos externos
- **Credential Validation**: Verificação em runtime

## 🚨 Regras de Ouro

1. **NUNCA** commite credenciais no código
2. **SEMPRE** use Replit Secrets para informações sensíveis
3. **SEMPRE** valide credenciais antes de usar
4. **NUNCA** exponha secrets em logs
5. **SEMPRE** use HTTPS em produção

## 🔍 Como Verificar se Está Seguro

### Buscar por Vazamentos
```bash
# No terminal do Replit, execute:
grep -r "GOCSPX-" drive-uploader/
grep -r "apps.googleusercontent.com" drive-uploader/ --exclude="*.md"
```

**Resultado esperado**: Nenhum resultado encontrado (arquivos MD são documentação)

### Testar Aplicação
1. Execute o servidor: `cd drive-uploader/backend && python main.py`
2. Verifique logs: Deve mostrar "✅" para credenciais
3. Acesse aplicação: Client ID deve carregar do servidor

## 📞 Solução de Problemas

### "Client ID não configurado"
- Verifique se `GOOGLE_CLIENT_ID` está no Replit Secrets
- Formato correto: `123456-abc.apps.googleusercontent.com`

### "Client Secret não configurado"  
- Verifique se `GOOGLE_CLIENT_SECRET` está no Replit Secrets
- Formato correto: `GOCSPX-abc123def456...`

### "Configuração OAuth não disponível"
- Reinicie o servidor após configurar secrets
- Verifique se não há erros no console

---
**🛡️ Status de Segurança: BLINDADO ✅**
