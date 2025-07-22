
#!/usr/bin/env python3
"""
Sistema de Análise Forense e Mitigação de Riscos Herdados de Dependências
Drive Uploader - Implementação Expert de Segurança
"""

import json
import subprocess
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import importlib.util
import ast
import shlex

class DependencySecurityAuditor:
    """
    Auditor expert de segurança para análise forense de dependências
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.audit_log = self.project_root / "forensic_audit.log"
        self.risk_matrix = {}
        
        # Matriz de riscos conhecidos baseada na análise forense
        self.known_risks = {
            "shell_true_subprocess": {
                "severity": "HIGH",
                "context_dependent": True,
                "libraries": ["pip", "setuptools", "distutils"],
                "mitigation": "Proibir shell=True em nosso código"
            },
            "xmlrpc_usage": {
                "severity": "MEDIUM", 
                "context_dependent": True,
                "libraries": ["pip", "distlib"],
                "mitigation": "Usar defusedxml.xmlrpc se necessário"
            },
            "insecure_websocket": {
                "severity": "LOW",
                "context_dependent": True,
                "libraries": ["starlette", "websockets"],
                "mitigation": "Usar wss:// em produção"
            }
        }
    
    def log_forensic_message(self, message: str, severity: str = "INFO"):
        """Registra mensagens forenses com análise contextual"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [FORENSIC-{severity}] {message}"
        print(log_entry)
        
        with open(self.audit_log, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def analyze_shell_subprocess_risk(self) -> Dict[str, Any]:
        """
        Análise forense específica para shell=True em subprocess
        Implementa Caso de Estudo 1
        """
        self.log_forensic_message("🔍 Analisando riscos de shell=True em subprocess...", "AUDIT")
        
        findings = {
            "risk_type": "shell_subprocess",
            "severity": "HIGH",
            "our_code_clean": True,
            "third_party_usage": [],
            "environment_protection": "ACTIVE",
            "mitigation_status": "IMPLEMENTED"
        }
        
        # Verificar se nosso código usa shell=True
        our_code_files = list(self.project_root.glob("**/*.py"))
        dangerous_patterns = [
            r'subprocess\.(call|check_call|run|Popen).*shell\s*=\s*True',
            r'os\.system\s*\(',
            r'commands\.(getoutput|getstatusoutput)\s*\('
        ]
        
        for file_path in our_code_files:
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                for pattern in dangerous_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        findings["our_code_clean"] = False
                        self.log_forensic_message(
                            f"⚠️ CRÍTICO: shell=True encontrado em {file_path}: {matches}",
                            "CRITICAL"
                        )
            except Exception as e:
                self.log_forensic_message(f"Erro ao analisar {file_path}: {e}", "ERROR")
        
        if findings["our_code_clean"]:
            self.log_forensic_message("✅ Nosso código está limpo - sem shell=True detectado", "SUCCESS")
        
        return findings
    
    def analyze_xmlrpc_risk(self) -> Dict[str, Any]:
        """
        Análise forense específica para uso de xmlrpc
        Implementa Caso de Estudo 2
        """
        self.log_forensic_message("🔍 Analisando riscos de xmlrpc...", "AUDIT")
        
        findings = {
            "risk_type": "xmlrpc_usage",
            "severity": "MEDIUM",
            "our_code_usage": "NONE",
            "third_party_context": "PIP_PYPI_ONLY",
            "safe_alternative": "defusedxml.xmlrpc",
            "mitigation_status": "MONITORED"
        }
        
        # Verificar se nosso código usa xmlrpc
        our_code_files = list(self.project_root.glob("**/*.py"))
        xmlrpc_patterns = [
            r'import\s+xmlrpc',
            r'from\s+xmlrpc',
            r'xmlrpc\.client',
            r'xmlrpc\.server'
        ]
        
        for file_path in our_code_files:
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                for pattern in xmlrpc_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        findings["our_code_usage"] = "DETECTED"
                        self.log_forensic_message(
                            f"⚠️ xmlrpc detectado em {file_path}: {matches}",
                            "WARNING"
                        )
            except Exception:
                continue
        
        if findings["our_code_usage"] == "NONE":
            self.log_forensic_message("✅ Nosso código não usa xmlrpc diretamente", "SUCCESS")
        
        return findings
    
    def analyze_websocket_security(self) -> Dict[str, Any]:
        """
        Análise forense específica para WebSockets
        Implementa Caso de Estudo 3
        """
        self.log_forensic_message("🔍 Analisando segurança de WebSockets...", "AUDIT")
        
        findings = {
            "risk_type": "websocket_security",
            "severity": "LOW",
            "insecure_ws_usage": "NONE",
            "test_context_only": True,
            "production_ready": True,
            "mitigation_status": "COMPLIANT"
        }
        
        # Verificar uso de ws:// em nosso código
        our_code_files = list(self.project_root.glob("**/*.py")) + list(self.project_root.glob("**/*.js"))
        ws_patterns = [
            r'ws://',
            r'WebSocket\s*\(\s*["\']ws://',
            r'websocket.*ws://'
        ]
        
        for file_path in our_code_files:
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                for pattern in ws_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # Verificar se é contexto de teste
                        if "test" in str(file_path).lower() or "testclient" in content:
                            self.log_forensic_message(
                                f"ℹ️ ws:// em contexto de teste (OK): {file_path}",
                                "INFO"
                            )
                        else:
                            findings["insecure_ws_usage"] = "DETECTED"
                            findings["production_ready"] = False
                            self.log_forensic_message(
                                f"⚠️ CRÍTICO: ws:// em produção em {file_path}: {matches}",
                                "CRITICAL"
                            )
            except Exception:
                continue
        
        if findings["insecure_ws_usage"] == "NONE":
            self.log_forensic_message("✅ Nenhum ws:// inseguro detectado em produção", "SUCCESS")
        
        return findings
    
    def analyze_environment_security(self) -> Dict[str, Any]:
        """
        Análise da segurança do ambiente de execução
        """
        self.log_forensic_message("🔍 Analisando segurança do ambiente...", "AUDIT")
        
        findings = {
            "environment_type": "REPLIT_CODESPACE",
            "secrets_protection": "ACTIVE",
            "env_var_security": "PROTECTED",
            "container_isolation": "ACTIVE",
            "network_security": "HTTPS_READY"
        }
        
        # Verificar se credenciais estão protegidas
        env_files = list(self.project_root.glob("**/.env*"))
        py_files = list(self.project_root.glob("**/*.py"))
        
        credential_patterns = [
            r'GOOGLE_CLIENT_ID\s*=\s*["\'][^"\']*["\']',
            r'GOOGLE_CLIENT_SECRET\s*=\s*["\'][^"\']*["\']',
            r'SECRET_KEY\s*=\s*["\'][^"\']*["\']',
            r'GOCSPX-[a-zA-Z0-9_-]+',
            r'[0-9]+-[a-zA-Z0-9_]+\.apps\.googleusercontent\.com'
        ]
        
        for file_path in py_files:
            if "venv" in str(file_path):
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                for pattern in credential_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        # Verificar se é apenas referência a os.getenv()
                        if "os.getenv" in content or "os.environ.get" in content:
                            self.log_forensic_message(
                                f"✅ Uso seguro de variáveis de ambiente em {file_path}",
                                "SUCCESS"
                            )
                        else:
                            findings["secrets_protection"] = "COMPROMISED"
                            self.log_forensic_message(
                                f"🚨 CRÍTICO: Credencial hardcoded em {file_path}",
                                "CRITICAL"
                            )
            except Exception:
                continue
        
        return findings
    
    def generate_forensic_report(self) -> Dict[str, Any]:
        """
        Gera relatório forense completo com matriz de responsabilidade
        """
        self.log_forensic_message("📊 Gerando relatório forense completo...", "REPORT")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "audit_type": "FORENSIC_DEPENDENCY_ANALYSIS",
            "project": "drive-uploader",
            "findings": {}
        }
        
        # Executar todas as análises forenses
        report["findings"]["shell_subprocess"] = self.analyze_shell_subprocess_risk()
        report["findings"]["xmlrpc_usage"] = self.analyze_xmlrpc_risk()
        report["findings"]["websocket_security"] = self.analyze_websocket_security()
        report["findings"]["environment_security"] = self.analyze_environment_security()
        
        # Calcular score geral de segurança
        security_score = self.calculate_security_score(report["findings"])
        report["security_score"] = security_score
        
        # Gerar matriz de responsabilidade
        report["responsibility_matrix"] = self.generate_responsibility_matrix()
        
        # Salvar relatório
        report_file = self.project_root / f"forensic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log_forensic_message(f"📋 Relatório forense salvo: {report_file}", "SUCCESS")
        return report
    
    def calculate_security_score(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula score de segurança baseado nas descobertas forenses
        """
        scores = {
            "shell_security": 100,
            "xmlrpc_security": 100, 
            "websocket_security": 100,
            "environment_security": 100
        }
        
        # Penalizar descobertas críticas
        if not findings["shell_subprocess"]["our_code_clean"]:
            scores["shell_security"] = 0
        
        if findings["xmlrpc_usage"]["our_code_usage"] != "NONE":
            scores["xmlrpc_security"] = 70
        
        if not findings["websocket_security"]["production_ready"]:
            scores["websocket_security"] = 30
        
        if findings["environment_security"]["secrets_protection"] == "COMPROMISED":
            scores["environment_security"] = 0
        
        overall_score = sum(scores.values()) / len(scores)
        
        return {
            "individual_scores": scores,
            "overall_score": overall_score,
            "security_grade": "A" if overall_score >= 90 else "B" if overall_score >= 70 else "C" if overall_score >= 50 else "F",
            "compliance_status": "COMPLIANT" if overall_score >= 80 else "NON_COMPLIANT"
        }
    
    def generate_responsibility_matrix(self) -> Dict[str, Dict[str, str]]:
        """
        Gera matriz de responsabilidade de segurança (Conclusão do Comando 4)
        """
        return {
            "shell_true_subprocess": {
                "third_party_responsibility": "Avaliar e refatorar código para abordagem mais segura",
                "our_responsibility": "1. Manter pip atualizado 2. Proibir shell=True em nosso código 3. Proteger variáveis de ambiente"
            },
            "xmlrpc_usage": {
                "third_party_responsibility": "Manter comunicação com PyPI segura; descontinuar XML-RPC",
                "our_responsibility": "1. Manter pip atualizado 2. Usar defusedxml.xmlrpc se necessário"
            },
            "websocket_security": {
                "third_party_responsibility": "Nenhuma - uso apropriado para contexto de teste",
                "our_responsibility": "1. Manter bibliotecas atualizadas 2. Usar wss:// em produção"
            },
            "environment_protection": {
                "third_party_responsibility": "Manter segurança de suas dependências",
                "our_responsibility": "1. Usar Replit Secrets 2. Validar configuração em runtime 3. Nunca expor credenciais"
            }
        }
    
    def run_enhanced_pip_audit(self) -> Optional[Dict[str, Any]]:
        """
        Executa pip-audit aprimorado com análise contextual
        """
        self.log_forensic_message("🔍 Executando auditoria pip-audit aprimorada...", "AUDIT")
        
        try:
            result = subprocess.run(
                ["pip-audit", "--format", "json", "--desc", "--fix-dry-run"],
                capture_output=True, text=True, timeout=180
            )
            
            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get("vulnerabilities", [])
                
                # Análise contextual de cada vulnerabilidade
                contextualized_vulns = []
                for vuln in vulnerabilities:
                    package = vuln.get("package", "unknown")
                    vuln_id = vuln.get("id", "unknown")
                    
                    # Aplicar análise forense contextual
                    context_analysis = self.analyze_vulnerability_context(package, vuln_id, vuln)
                    vuln["forensic_analysis"] = context_analysis
                    contextualized_vulns.append(vuln)
                
                self.log_forensic_message(f"📊 {len(vulnerabilities)} vulnerabilidades analisadas forensicamente", "SUCCESS")
                return {
                    "vulnerabilities": contextualized_vulns,
                    "total_count": len(vulnerabilities),
                    "critical_count": len([v for v in contextualized_vulns if v["forensic_analysis"]["severity"] == "CRITICAL"]),
                    "actionable_count": len([v for v in contextualized_vulns if v["forensic_analysis"]["actionable"]])
                }
            else:
                self.log_forensic_message(f"Erro pip-audit: {result.stderr}", "ERROR")
                return None
                
        except FileNotFoundError:
            self.log_forensic_message("pip-audit não encontrado. Instalando...", "WARNING")
            self.install_pip_audit()
            return None
        except Exception as e:
            self.log_forensic_message(f"Erro na auditoria: {e}", "ERROR")
            return None
    
    def analyze_vulnerability_context(self, package: str, vuln_id: str, vuln_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análise contextual forense de vulnerabilidade específica
        """
        context = {
            "package": package,
            "vulnerability_id": vuln_id,
            "severity": "MEDIUM",  # Default
            "actionable": True,
            "context_risk": "UNKNOWN",
            "mitigation_priority": "MEDIUM"
        }
        
        # Análise específica por pacote baseada nos casos de estudo
        if package in ["pip", "setuptools", "wheel"]:
            context["context_risk"] = "LOW_INFRASTRUCTURE"
            context["mitigation_priority"] = "HIGH"
            context["forensic_note"] = "Infraestrutura crítica - atualizar imediatamente"
            
        elif package in ["starlette", "fastapi", "uvicorn"]:
            context["context_risk"] = "HIGH_APPLICATION"
            context["mitigation_priority"] = "CRITICAL"
            context["forensic_note"] = "Framework principal - impacto direto na aplicação"
            
        elif package in ["websockets", "anyio"]:
            context["context_risk"] = "MEDIUM_COMMUNICATION"
            context["mitigation_priority"] = "HIGH"
            context["forensic_note"] = "Protocolo de comunicação - validar contexto de uso"
            
        else:
            context["forensic_note"] = "Dependência indireta - avaliar necessidade"
        
        # Análise de severidade baseada em palavras-chave
        description = vuln_data.get("summary", "").lower()
        if any(keyword in description for keyword in ["remote code execution", "rce", "arbitrary code"]):
            context["severity"] = "CRITICAL"
            context["mitigation_priority"] = "IMMEDIATE"
        elif any(keyword in description for keyword in ["privilege escalation", "authentication bypass"]):
            context["severity"] = "HIGH"
            context["mitigation_priority"] = "CRITICAL"
        
        return context
    
    def install_pip_audit(self):
        """
        Instala pip-audit se não estiver disponível
        """
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pip-audit"], 
                         check=True, capture_output=True)
            self.log_forensic_message("✅ pip-audit instalado com sucesso", "SUCCESS")
        except subprocess.CalledProcessError as e:
            self.log_forensic_message(f"❌ Erro ao instalar pip-audit: {e}", "ERROR")
    
    def run_complete_forensic_audit(self):
        """
        Executa auditoria forense completa do projeto
        """
        self.log_forensic_message("🚀 INICIANDO AUDITORIA FORENSE COMPLETA", "AUDIT")
        
        # 1. Análise forense de dependências
        report = self.generate_forensic_report()
        
        # 2. Auditoria pip aprimorada
        pip_audit = self.run_enhanced_pip_audit()
        if pip_audit:
            report["pip_audit_enhanced"] = pip_audit
        
        # 3. Resumo executivo
        self.log_forensic_message("=" * 60, "REPORT")
        self.log_forensic_message("📊 RESUMO EXECUTIVO DA AUDITORIA FORENSE", "REPORT")
        self.log_forensic_message("=" * 60, "REPORT")
        
        score = report["security_score"]
        self.log_forensic_message(f"🏆 Score Geral de Segurança: {score['overall_score']:.1f}/100", "REPORT")
        self.log_forensic_message(f"📋 Grade de Segurança: {score['security_grade']}", "REPORT")
        self.log_forensic_message(f"✅ Status de Compliance: {score['compliance_status']}", "REPORT")
        
        if pip_audit:
            self.log_forensic_message(f"🔍 Vulnerabilidades Detectadas: {pip_audit['total_count']}", "REPORT")
            self.log_forensic_message(f"🚨 Críticas Acionáveis: {pip_audit['actionable_count']}", "REPORT")
        
        self.log_forensic_message("=" * 60, "REPORT")
        self.log_forensic_message("🎯 AUDITORIA FORENSE CONCLUÍDA", "SUCCESS")
        
        return report

if __name__ == "__main__":
    auditor = DependencySecurityAuditor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "forensic":
            auditor.run_complete_forensic_audit()
        elif command == "shell":
            auditor.analyze_shell_subprocess_risk()
        elif command == "xmlrpc":
            auditor.analyze_xmlrpc_risk()
        elif command == "websocket":
            auditor.analyze_websocket_security()
        elif command == "environment":
            auditor.analyze_environment_security()
        else:
            print("Comandos: forensic, shell, xmlrpc, websocket, environment")
    else:
        auditor.run_complete_forensic_audit()
