
#!/usr/bin/env python3
"""
Script de Manutenção de Segurança - Drive Uploader
Executa verificações automáticas de segurança e atualizações
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

class SecurityMaintenance:
    """Classe para manutenção automatizada de segurança"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.log_file = self.project_root / "security_audit.log"
    
    def log_message(self, message: str, level: str = "INFO"):
        """Registra mensagens com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def check_outdated_packages(self):
        """Verifica pacotes desatualizados"""
        self.log_message("Verificando pacotes desatualizados...")
        
        try:
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format", "json"],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                outdated = json.loads(result.stdout)
                if outdated:
                    self.log_message(f"Encontrados {len(outdated)} pacotes desatualizados:", "WARNING")
                    for pkg in outdated:
                        self.log_message(f"  - {pkg['name']}: {pkg['version']} -> {pkg['latest_version']}")
                    return outdated
                else:
                    self.log_message("Todos os pacotes estão atualizados")
                    return []
            else:
                self.log_message(f"Erro ao verificar pacotes: {result.stderr}", "ERROR")
                return None
                
        except Exception as e:
            self.log_message(f"Erro na verificação: {e}", "ERROR")
            return None
    
    def run_security_audit(self):
        """Executa auditoria de segurança com pip-audit"""
        self.log_message("Executando auditoria de segurança...")
        
        try:
            result = subprocess.run(
                ["pip-audit", "--format", "json", "--desc"],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get("vulnerabilities", [])
                
                if vulnerabilities:
                    self.log_message(f"Encontradas {len(vulnerabilities)} vulnerabilidades:", "CRITICAL")
                    for vuln in vulnerabilities:
                        pkg = vuln.get("package", "unknown")
                        vuln_id = vuln.get("id", "unknown")
                        summary = vuln.get("summary", "No summary")
                        self.log_message(f"  - {pkg}: {vuln_id} - {summary}")
                    return vulnerabilities
                else:
                    self.log_message("Nenhuma vulnerabilidade encontrada")
                    return []
            else:
                self.log_message(f"Erro na auditoria: {result.stderr}", "ERROR")
                return None
                
        except FileNotFoundError:
            self.log_message("pip-audit não instalado. Instale com: pip install pip-audit", "WARNING")
            return None
        except Exception as e:
            self.log_message(f"Erro na auditoria: {e}", "ERROR")
            return None
    
    def update_critical_packages(self):
        """Atualiza pacotes críticos de segurança"""
        critical_packages = [
            "pip", "setuptools", "wheel",  # Ferramentas de base
            "fastapi", "uvicorn", "starlette",  # Web framework
            "pydantic", "pydantic-core",  # Validação de dados
            "click", "python-dotenv",  # Utilitários
            "anyio", "httpx",  # Async e HTTP
            "cryptography", "certifi"  # Segurança e certificados
        ]
        
        self.log_message("Atualizando pacotes críticos...")
        
        for package in critical_packages:
            try:
                self.log_message(f"Atualizando {package}...")
                result = subprocess.run(
                    ["pip", "install", "--upgrade", package],
                    capture_output=True, text=True, timeout=300
                )
                
                if result.returncode == 0:
                    if "Successfully installed" in result.stdout:
                        self.log_message(f"✅ {package} atualizado com sucesso")
                    else:
                        self.log_message(f"ℹ️ {package} já estava atualizado")
                else:
                    self.log_message(f"❌ Erro ao atualizar {package}: {result.stderr}", "ERROR")
                    
            except Exception as e:
                self.log_message(f"❌ Erro ao atualizar {package}: {e}", "ERROR")
    
    def generate_security_report(self):
        """Gera relatório consolidado de segurança"""
        self.log_message("Gerando relatório de segurança...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "outdated_packages": self.check_outdated_packages(),
            "vulnerabilities": self.run_security_audit()
        }
        
        report_file = self.project_root / f"security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log_message(f"Relatório salvo em: {report_file}")
        return report
    
    def run_full_maintenance(self):
        """Executa manutenção completa de segurança"""
        self.log_message("=== INICIANDO MANUTENÇÃO DE SEGURANÇA ===")
        
        # 1. Atualizar pacotes críticos
        self.update_critical_packages()
        
        # 2. Gerar relatório
        report = self.generate_security_report()
        
        # 3. Resumo final
        vulnerabilities = report.get("vulnerabilities", [])
        outdated = report.get("outdated_packages", [])
        
        self.log_message("=== RESUMO DA MANUTENÇÃO ===")
        self.log_message(f"Vulnerabilidades encontradas: {len(vulnerabilities) if vulnerabilities else 0}")
        self.log_message(f"Pacotes desatualizados: {len(outdated) if outdated else 0}")
        
        if vulnerabilities:
            self.log_message("⚠️ AÇÃO NECESSÁRIA: Vulnerabilidades detectadas!", "CRITICAL")
        else:
            self.log_message("✅ Nenhuma vulnerabilidade crítica detectada")
        
        self.log_message("=== MANUTENÇÃO CONCLUÍDA ===")

if __name__ == "__main__":
    maintenance = SecurityMaintenance()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "audit":
            maintenance.run_security_audit()
        elif command == "update":
            maintenance.update_critical_packages()
        elif command == "report":
            maintenance.generate_security_report()
        else:
            print("Comandos disponíveis: audit, update, report")
    else:
        maintenance.run_full_maintenance()
