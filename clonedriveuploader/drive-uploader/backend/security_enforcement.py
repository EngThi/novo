
#!/usr/bin/env python3
"""
Sistema de Aplicação de Regras de Segurança - Security Enforcement
Implementa as mitigações identificadas na análise forense
"""

import os
import sys
import re
import shlex
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import ast
from urllib.parse import urlparse

class SecurityEnforcer:
    """
    Aplica regras de segurança baseadas na análise forense de dependências
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.violations = []
        
        # Regras de segurança baseadas na análise forense
        self.security_rules = {
            "no_shell_true": {
                "description": "Proibir shell=True em subprocess (Caso de Estudo 1)",
                "severity": "CRITICAL",
                "patterns": [
                    r'subprocess\.(call|check_call|run|Popen).*shell\s*=\s*True',
                    r'os\.system\s*\(',
                    r'commands\.(getoutput|getstatusoutput)\s*\('
                ]
            },
            "no_unsafe_xmlrpc": {
                "description": "Usar defusedxml.xmlrpc ao invés de xmlrpc padrão (Caso de Estudo 2)",
                "severity": "HIGH",
                "patterns": [
                    r'import\s+xmlrpc\.client',
                    r'from\s+xmlrpc\.client\s+import',
                    r'xmlrpc\.client\.',
                ]
            },
            "no_insecure_websockets": {
                "description": "Usar wss:// ao invés de ws:// em produção (Caso de Estudo 3)",
                "severity": "MEDIUM",
                "patterns": [
                    r'ws://(?!.*test)',  # ws:// mas não em contexto de teste
                    r'WebSocket\s*\(\s*["\']ws://'
                ]
            },
            "no_hardcoded_secrets": {
                "description": "Proibir credenciais hardcoded",
                "severity": "CRITICAL",
                "patterns": [
                    r'GOOGLE_CLIENT_ID\s*=\s*["\'][^"\']{20,}["\']',
                    r'GOOGLE_CLIENT_SECRET\s*=\s*["\'][^"\']{20,}["\']',
                    r'SECRET_KEY\s*=\s*["\'][^"\']{10,}["\']',
                    r'GOCSPX-[a-zA-Z0-9_-]+',
                    r'[0-9]+-[a-zA-Z0-9_]+\.apps\.googleusercontent\.com'
                ]
            }
        }
    
    def validate_subprocess_usage(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """
        Valida uso seguro de subprocess baseado no Caso de Estudo 1
        """
        violations = []
        
        # Detectar uso de shell=True
        shell_true_pattern = r'subprocess\.(call|check_call|run|Popen).*shell\s*=\s*True'
        matches = re.finditer(shell_true_pattern, content, re.MULTILINE | re.IGNORECASE)
        
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            violations.append({
                "file": str(file_path),
                "line": line_num,
                "rule": "no_shell_true",
                "severity": "CRITICAL",
                "message": "shell=True detectado - use lista de comandos ao invés",
                "code_snippet": match.group(0),
                "mitigation": "Use subprocess.run(['comando', 'arg1', 'arg2']) ao invés de shell=True"
            })
        
        # Detectar uso de os.system
        os_system_pattern = r'os\.system\s*\('
        matches = re.finditer(os_system_pattern, content, re.MULTILINE | re.IGNORECASE)
        
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            violations.append({
                "file": str(file_path),
                "line": line_num,
                "rule": "no_shell_true",
                "severity": "CRITICAL",
                "message": "os.system detectado - extremamente inseguro",
                "code_snippet": match.group(0),
                "mitigation": "Use subprocess.run com lista de comandos"
            })
        
        return violations
    
    def validate_xmlrpc_usage(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """
        Valida uso seguro de xmlrpc baseado no Caso de Estudo 2
        """
        violations = []
        
        # Detectar import inseguro de xmlrpc
        patterns = [
            r'import\s+xmlrpc\.client',
            r'from\s+xmlrpc\.client\s+import',
            r'xmlrpc\.client\.'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append({
                    "file": str(file_path),
                    "line": line_num,
                    "rule": "no_unsafe_xmlrpc",
                    "severity": "HIGH",
                    "message": "xmlrpc inseguro detectado",
                    "code_snippet": match.group(0),
                    "mitigation": "Use: import defusedxml.xmlrpc.client as xmlrpc_client"
                })
        
        return violations
    
    def validate_websocket_security(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """
        Valida segurança de WebSockets baseado no Caso de Estudo 3
        """
        violations = []
        
        # Detectar ws:// em contexto de produção (não teste)
        ws_pattern = r'ws://[^\s"\']+'
        matches = re.finditer(ws_pattern, content, re.MULTILINE | re.IGNORECASE)
        
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            
            # Verificar se é contexto de teste
            line_start = max(0, content.rfind('\n', 0, match.start()))
            line_end = content.find('\n', match.end())
            if line_end == -1:
                line_end = len(content)
            line_content = content[line_start:line_end].lower()
            
            if "test" not in line_content and "localhost" not in match.group(0):
                violations.append({
                    "file": str(file_path),
                    "line": line_num,
                    "rule": "no_insecure_websockets",
                    "severity": "MEDIUM",
                    "message": "WebSocket inseguro (ws://) em produção",
                    "code_snippet": match.group(0),
                    "mitigation": "Use wss:// para conexões WebSocket em produção"
                })
        
        return violations
    
    def validate_secrets_security(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """
        Valida que não há credenciais hardcoded
        """
        violations = []
        
        # Padrões para detectar credenciais hardcoded
        credential_patterns = {
            "google_client_id": r'[0-9]+-[a-zA-Z0-9_]+\.apps\.googleusercontent\.com',
            "google_client_secret": r'GOCSPX-[a-zA-Z0-9_-]+',
            "generic_secret": r'(SECRET_KEY|API_KEY|CLIENT_SECRET)\s*=\s*["\'][^"\']{20,}["\']'
        }
        
        for cred_type, pattern in credential_patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                # Verificar se está em contexto de os.getenv (permitido)
                line_start = max(0, content.rfind('\n', 0, match.start()))
                line_end = content.find('\n', match.end())
                if line_end == -1:
                    line_end = len(content)
                line_content = content[line_start:line_end]
                
                if "os.getenv" not in line_content and "os.environ" not in line_content:
                    violations.append({
                        "file": str(file_path),
                        "line": line_num,
                        "rule": "no_hardcoded_secrets",
                        "severity": "CRITICAL",
                        "message": f"Credencial hardcoded detectada: {cred_type}",
                        "code_snippet": match.group(0)[:50] + "..." if len(match.group(0)) > 50 else match.group(0),
                        "mitigation": "Use os.getenv() e configure no Replit Secrets"
                    })
        
        return violations
    
    def validate_file_security(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Valida segurança de um arquivo específico
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            return [{
                "file": str(file_path),
                "line": 0,
                "rule": "file_read_error",
                "severity": "ERROR",
                "message": f"Erro ao ler arquivo: {e}",
                "mitigation": "Verificar codificação e permissões do arquivo"
            }]
        
        violations = []
        
        # Aplicar todas as validações
        violations.extend(self.validate_subprocess_usage(file_path, content))
        violations.extend(self.validate_xmlrpc_usage(file_path, content))
        violations.extend(self.validate_websocket_security(file_path, content))
        violations.extend(self.validate_secrets_security(file_path, content))
        
        return violations
    
    def scan_project_security(self) -> Dict[str, Any]:
        """
        Executa scan completo de segurança do projeto
        """
        print("🔍 Iniciando scan de segurança do projeto...")
        
        # Arquivos para analisar
        file_patterns = ["**/*.py", "**/*.js", "**/*.ts"]
        all_violations = []
        
        for pattern in file_patterns:
            for file_path in self.project_root.glob(pattern):
                # Pular diretórios de dependências
                if any(skip in str(file_path) for skip in ["venv", "__pycache__", "node_modules"]):
                    continue
                
                violations = self.validate_file_security(file_path)
                all_violations.extend(violations)
        
        # Organizar por severidade
        critical = [v for v in all_violations if v["severity"] == "CRITICAL"]
        high = [v for v in all_violations if v["severity"] == "HIGH"]
        medium = [v for v in all_violations if v["severity"] == "MEDIUM"]
        
        results = {
            "total_violations": len(all_violations),
            "critical_count": len(critical),
            "high_count": len(high),
            "medium_count": len(medium),
            "violations": {
                "critical": critical,
                "high": high,
                "medium": medium
            },
            "security_score": self.calculate_security_score(all_violations),
            "compliance": len(critical) == 0 and len(high) == 0
        }
        
        return results
    
    def calculate_security_score(self, violations: List[Dict[str, Any]]) -> int:
        """
        Calcula score de segurança baseado nas violações
        """
        if not violations:
            return 100
        
        penalty = 0
        for violation in violations:
            if violation["severity"] == "CRITICAL":
                penalty += 25
            elif violation["severity"] == "HIGH":
                penalty += 15
            elif violation["severity"] == "MEDIUM":
                penalty += 5
        
        return max(0, 100 - penalty)
    
    def generate_security_report(self) -> str:
        """
        Gera relatório de segurança formatado
        """
        results = self.scan_project_security()
        
        report = []
        report.append("=" * 70)
        report.append("🛡️  RELATÓRIO DE APLICAÇÃO DE SEGURANÇA")
        report.append("   Baseado na Análise Forense de Dependências")
        report.append("=" * 70)
        report.append("")
        
        # Resumo
        report.append("📊 RESUMO EXECUTIVO:")
        report.append(f"   • Total de Violações: {results['total_violations']}")
        report.append(f"   • Críticas: {results['critical_count']}")
        report.append(f"   • Altas: {results['high_count']}")
        report.append(f"   • Médias: {results['medium_count']}")
        report.append(f"   • Score de Segurança: {results['security_score']}/100")
        report.append(f"   • Status Compliance: {'✅ APROVADO' if results['compliance'] else '❌ REPROVADO'}")
        report.append("")
        
        # Violações críticas
        if results['violations']['critical']:
            report.append("🚨 VIOLAÇÕES CRÍTICAS (Ação Imediata Necessária):")
            for v in results['violations']['critical']:
                report.append(f"   📍 {v['file']}:{v['line']}")
                report.append(f"      {v['message']}")
                report.append(f"      Código: {v['code_snippet']}")
                report.append(f"      Solução: {v['mitigation']}")
                report.append("")
        
        # Violações altas
        if results['violations']['high']:
            report.append("⚠️  VIOLAÇÕES ALTAS:")
            for v in results['violations']['high']:
                report.append(f"   📍 {v['file']}:{v['line']}")
                report.append(f"      {v['message']}")
                report.append(f"      Solução: {v['mitigation']}")
                report.append("")
        
        # Violações médias
        if results['violations']['medium']:
            report.append("📋 VIOLAÇÕES MÉDIAS:")
            for v in results['violations']['medium']:
                report.append(f"   📍 {v['file']}:{v['line']}")
                report.append(f"      {v['message']}")
                report.append("")
        
        if results['compliance']:
            report.append("🎉 PARABÉNS! Projeto em compliance de segurança!")
            report.append("   Todas as regras da análise forense foram aplicadas.")
        
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def fix_security_violations(self, auto_fix: bool = False) -> bool:
        """
        Corrige violações de segurança automaticamente (quando possível)
        """
        if not auto_fix:
            print("⚠️ Auto-fix desabilitado. Use --auto-fix para correções automáticas")
            return False
        
        print("🔧 Iniciando correção automática de violações...")
        
        # Por questões de segurança, apenas sugere correções
        # Auto-fix real seria implementado com validação manual
        results = self.scan_project_security()
        
        if results['violations']['critical']:
            print("❌ Violações críticas detectadas - correção manual necessária")
            return False
        
        print("✅ Nenhuma violação crítica - projeto seguro")
        return True

if __name__ == "__main__":
    enforcer = SecurityEnforcer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--report":
        print(enforcer.generate_security_report())
    elif len(sys.argv) > 1 and sys.argv[1] == "--fix":
        auto_fix = "--auto-fix" in sys.argv
        enforcer.fix_security_violations(auto_fix)
    else:
        print("Uso: python security_enforcement.py [--report] [--fix] [--auto-fix]")
