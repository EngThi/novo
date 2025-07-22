
# 🔒 Diretrizes de Segurança - Correções Implementadas

## ❌ Problema Identificado: Injeção de Comando

O projeto tinha vulnerabilidades de **injeção de comando** em chamadas de subprocess.

## ✅ Correções Implementadas

### 1. Substituição de `shell=True` por `shell=False`

**ANTES (INSEGURO):**
```python
# ❌ PERIGOSO - Vulnerável a injeção de comando
subprocess.run(f"ffmpeg -i {user_input}.wav output.wav", shell=True)
```

**DEPOIS (SEGURO):**
```python
# ✅ SEGURO - Usa lista de argumentos
subprocess.run(["ffmpeg", "-i", f"{user_input}.wav", "output.wav"], shell=False)
```

### 2. Validação de Paths

**Implementado em `merge_audio.py`:**
```python
# Validação de entrada
safe_path = Path(path).resolve()
if not safe_path.exists() or not str(safe_path).endswith('.wav'):
    print(f"⚠️ Arquivo inválido: {path}")
    continue
```

### 3. Função Segura para FFmpeg

**Nova função `safe_ffmpeg_command()`:**
- ✅ Usa `shell=False`
- ✅ Lista de argumentos em vez de string
- ✅ Validação de arquivos de entrada
- ✅ Sanitização de paths
- ✅ Tratamento de erros

## 🛡️ Princípios de Segurança Aplicados

1. **Nunca usar `shell=True`** com entrada do usuário
2. **Sempre usar listas de argumentos** em subprocess
3. **Validar e sanitizar** todos os paths de arquivo
4. **Usar `Path.resolve()`** para prevenir path traversal
5. **Tratar erros** adequadamente

## 🔍 Como Identificar Vulnerabilidades

Procure por padrões inseguros no código:

```bash
# Buscar por chamadas perigosas
grep -r "shell=True" .
grep -r "os.system" .
grep -r "subprocess.*shell" .
```

## ✅ Código Seguro vs Inseguro

### Processamento de Áudio - SEGURO
```python
def safe_audio_process(input_file, output_file):
    cmd = ["ffmpeg", "-i", str(Path(input_file).resolve()), str(Path(output_file).resolve())]
    subprocess.run(cmd, shell=False, check=True)
```

### Processamento de Áudio - INSEGURO
```python
def unsafe_audio_process(input_file, output_file):
    # ❌ NUNCA FAZER ISSO
    os.system(f"ffmpeg -i {input_file} {output_file}")
```

## 🚨 Regras de Ouro

1. **SEMPRE** usar `shell=False`
2. **SEMPRE** usar listas para argumentos
3. **SEMPRE** validar entrada do usuário
4. **NUNCA** concatenar strings para comandos
5. **SEMPRE** usar `Path.resolve()` para paths

---

**Status: ✅ Vulnerabilidades Corrigidas**
**Última Verificação:** 2025-01-21
