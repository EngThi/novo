
#!/usr/bin/env python3
"""
Monitor de Riscos de Dependências em Tempo Real
Implementa monitoramento contínuo baseado na análise forense
"""

import asyncio
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import queue
import hashlib

class DependencyRiskMonitor:
    """
    Monitor em tempo real para riscos de dependências
    """
    
    def __init__(self, monitoring_interval: int = 3600):  # 1 hora
        self.project_root = Path(__file__).parent
        self.monitoring_interval = monitoring_interval
        self.risk_queue = queue.Queue()
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Cache de hashes para detectar mudanças
        self.dependency_hashes = {}
        self.last_audit = None
        
        # Configurações de risco baseadas na análise forense
        self.risk_thresholds = {
            "critical_vulnerabilities": 0,  # Nenhuma vulnerabilidade crítica aceita
            "high_vulnerabilities": 2,      # Máximo 2 vulnerabilidades altas
            "outdated_critical_packages": 5, # Máximo 5 pacotes críticos desatualizados
            "security_score_minimum": 80    # Score mínimo de segurança
        }
        
        # Pacotes críticos para monitoramento prioritário
        self.critical_packages = [
            "fastapi", "uvicorn", "starlette", "pydantic",
            "anyio", "websockets", "click", "python-dotenv",
            "pip", "setuptools", "wheel", "cryptography", "certifi"
        ]
    
    def calculate_dependency_hash(self) -> str:
        """
        Calcula hash das dependências para detectar mudanças
        """
        try:
            # Hash do requirements.txt
            req_file = self.project_root / "requirements.txt"
            if req_file.exists():
                req_content = req_file.read_text()
            else:
                req_content = ""
            
            # Hash dos pacotes instalados
            result = subprocess.run(
                ["pip", "freeze"],
                capture_output=True, text=True, timeout=60
            )
            installed_packages = result.stdout if result.returncode == 0 else ""
            
            # Combinar conteúdos e gerar hash
            combined_content = req_content + installed_packages
            return hashlib.sha256(combined_content.encode()).hexdigest()
            
        except Exception as e:
            print(f"Erro ao calcular hash de dependências: {e}")
            return ""
    
    def detect_dependency_changes(self) -> bool:
        """
        Detecta se as dependências mudaram desde a última verificação
        """
        current_hash = self.calculate_dependency_hash()
        
        if not self.dependency_hashes:
            self.dependency_hashes["current"] = current_hash
            return True  # Primeira execução
        
        if self.dependency_hashes.get("current") != current_hash:
            self.dependency_hashes["previous"] = self.dependency_hashes.get("current", "")
            self.dependency_hashes["current"] = current_hash
            return True
        
        return False
    
    def run_risk_assessment(self) -> Dict[str, Any]:
        """
        Executa avaliação de riscos abrangente
        """
        print("🔍 Executando avaliação de riscos...")
        
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "dependency_hash": self.calculate_dependency_hash(),
            "vulnerabilities": self.scan_vulnerabilities(),
            "outdated_packages": self.check_outdated_packages(),
            "security_compliance": self.check_security_compliance(),
            "risk_score": 0,
            "recommendations": []
        }
        
        # Calcular score de risco
        assessment["risk_score"] = self.calculate_risk_score(assessment)
        
        # Gerar recomendações
        assessment["recommendations"] = self.generate_recommendations(assessment)
        
        return assessment
    
    def scan_vulnerabilities(self) -> Dict[str, Any]:
        """
        Escaneia vulnerabilidades com pip-audit
        """
        try:
            result = subprocess.run(
                ["pip-audit", "--format", "json", "--desc"],
                capture_output=True, text=True, timeout=180
            )
            
            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get("vulnerabilities", [])
                
                # Categorizar por severidade
                categorized = {
                    "critical": [],
                    "high": [],
                    "medium": [],
                    "low": [],
                    "total": len(vulnerabilities)
                }
                
                for vuln in vulnerabilities:
                    # Análise contextual de severidade
                    severity = self.analyze_vulnerability_severity(vuln)
                    categorized[severity].append(vuln)
                
                return categorized
            else:
                return {"error": result.stderr, "total": 0}
                
        except FileNotFoundError:
            return {"error": "pip-audit não instalado", "total": 0}
        except Exception as e:
            return {"error": str(e), "total": 0}
    
    def analyze_vulnerability_severity(self, vulnerability: Dict[str, Any]) -> str:
        """
        Analisa severidade de vulnerabilidade baseada no contexto
        """
        package = vulnerability.get("package", "").lower()
        description = vulnerability.get("summary", "").lower()
        
        # Vulnerabilidades críticas por contexto
        if package in self.critical_packages:
            if any(keyword in description for keyword in [
                "remote code execution", "rce", "arbitrary code execution",
                "privilege escalation", "authentication bypass"
            ]):
                return "critical"
            elif any(keyword in description for keyword in [
                "denial of service", "dos", "memory corruption",
                "buffer overflow", "injection"
            ]):
                return "high"
        
        # Análise por padrões de descrição
        if any(keyword in description for keyword in [
            "remote code execution", "rce", "arbitrary code"
        ]):
            return "critical"
        elif any(keyword in description for keyword in [
            "privilege escalation", "authentication bypass", "sql injection"
        ]):
            return "high"
        elif any(keyword in description for keyword in [
            "cross-site scripting", "xss", "csrf", "path traversal"
        ]):
            return "medium"
        else:
            return "low"
    
    def check_outdated_packages(self) -> Dict[str, Any]:
        """
        Verifica pacotes desatualizados com foco em críticos
        """
        try:
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format", "json"],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                outdated_packages = json.loads(result.stdout)
                
                # Separar pacotes críticos dos demais
                critical_outdated = [
                    pkg for pkg in outdated_packages 
                    if pkg["name"].lower() in [p.lower() for p in self.critical_packages]
                ]
                
                return {
                    "total": len(outdated_packages),
                    "critical_count": len(critical_outdated),
                    "critical_packages": critical_outdated,
                    "all_packages": outdated_packages
                }
            else:
                return {"error": result.stderr, "total": 0}
                
        except Exception as e:
            return {"error": str(e), "total": 0}
    
    def check_security_compliance(self) -> Dict[str, Any]:
        """
        Verifica compliance com regras de segurança
        """
        from security_enforcement import SecurityEnforcer
        
        enforcer = SecurityEnforcer()
        results = enforcer.scan_project_security()
        
        return {
            "total_violations": results["total_violations"],
            "critical_violations": results["critical_count"],
            "high_violations": results["high_count"],
            "security_score": results["security_score"],
            "compliance_status": results["compliance"]
        }
    
    def calculate_risk_score(self, assessment: Dict[str, Any]) -> int:
        """
        Calcula score de risco (0-100, onde 100 = risco máximo)
        """
        risk_score = 0
        
        # Vulnerabilidades (peso 40%)
        vuln_data = assessment.get("vulnerabilities", {})
        if isinstance(vuln_data, dict) and "total" in vuln_data:
            critical_vulns = len(vuln_data.get("critical", []))
            high_vulns = len(vuln_data.get("high", []))
            medium_vulns = len(vuln_data.get("medium", []))
            
            vuln_score = (critical_vulns * 25) + (high_vulns * 15) + (medium_vulns * 5)
            risk_score += min(40, vuln_score)
        
        # Pacotes desatualizados (peso 20%)
        outdated_data = assessment.get("outdated_packages", {})
        if isinstance(outdated_data, dict):
            critical_outdated = outdated_data.get("critical_count", 0)
            total_outdated = outdated_data.get("total", 0)
            
            outdated_score = (critical_outdated * 4) + (total_outdated * 1)
            risk_score += min(20, outdated_score)
        
        # Compliance de segurança (peso 40%)
        compliance_data = assessment.get("security_compliance", {})
        if isinstance(compliance_data, dict):
            critical_violations = compliance_data.get("critical_violations", 0)
            high_violations = compliance_data.get("high_violations", 0)
            
            compliance_score = (critical_violations * 20) + (high_violations * 10)
            risk_score += min(40, compliance_score)
        
        return min(100, risk_score)
    
    def generate_recommendations(self, assessment: Dict[str, Any]) -> List[str]:
        """
        Gera recomendações baseadas na avaliação de riscos
        """
        recommendations = []
        risk_score = assessment.get("risk_score", 0)
        
        # Recomendações baseadas em vulnerabilidades
        vuln_data = assessment.get("vulnerabilities", {})
        if isinstance(vuln_data, dict):
            critical_vulns = len(vuln_data.get("critical", []))
            high_vulns = len(vuln_data.get("high", []))
            
            if critical_vulns > 0:
                recommendations.append(
                    f"🚨 URGENTE: {critical_vulns} vulnerabilidade(s) crítica(s) detectada(s). "
                    "Atualize imediatamente os pacotes afetados."
                )
            
            if high_vulns > 0:
                recommendations.append(
                    f"⚠️ ALTA PRIORIDADE: {high_vulns} vulnerabilidade(s) de alta severidade. "
                    "Programe atualização para as próximas 24h."
                )
        
        # Recomendações para pacotes desatualizados
        outdated_data = assessment.get("outdated_packages", {})
        if isinstance(outdated_data, dict):
            critical_outdated = outdated_data.get("critical_count", 0)
            if critical_outdated > 0:
                recommendations.append(
                    f"📦 CRÍTICO: {critical_outdated} pacote(s) crítico(s) desatualizado(s). "
                    "Execute: python security_maintenance.py update"
                )
        
        # Recomendações de compliance
        compliance_data = assessment.get("security_compliance", {})
        if isinstance(compliance_data, dict):
            if not compliance_data.get("compliance_status", True):
                recommendations.append(
                    "🛡️ COMPLIANCE: Violações de segurança detectadas. "
                    "Execute: python security_enforcement.py --report"
                )
        
        # Recomendação geral baseada no score
        if risk_score >= 80:
            recommendations.append("🚨 RISCO EXTREMO: Intervenção imediata necessária")
        elif risk_score >= 60:
            recommendations.append("⚠️ RISCO ALTO: Ação necessária em 24h")
        elif risk_score >= 40:
            recommendations.append("📋 RISCO MÉDIO: Monitorar e planejar atualizações")
        elif risk_score <= 20:
            recommendations.append("✅ RISCO BAIXO: Manter monitoramento regular")
        
        return recommendations or ["✅ Nenhuma ação imediata necessária"]
    
    def start_monitoring(self):
        """
        Inicia monitoramento contínuo
        """
        if self.is_monitoring:
            print("⚠️ Monitoramento já está ativo")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print(f"🔍 Monitoramento de riscos iniciado (intervalo: {self.monitoring_interval}s)")
    
    def stop_monitoring(self):
        """
        Para monitoramento contínuo
        """
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⏹️ Monitoramento de riscos parado")
    
    def _monitoring_loop(self):
        """
        Loop principal de monitoramento
        """
        while self.is_monitoring:
            try:
                # Verificar se dependências mudaram
                if self.detect_dependency_changes():
                    print("📦 Mudanças nas dependências detectadas - executando avaliação...")
                    assessment = self.run_risk_assessment()
                    self.process_risk_assessment(assessment)
                
                # Verificar se é hora da avaliação periódica
                if (not self.last_audit or 
                    datetime.now() - self.last_audit > timedelta(seconds=self.monitoring_interval)):
                    
                    print("⏰ Executando avaliação periódica de riscos...")
                    assessment = self.run_risk_assessment()
                    self.process_risk_assessment(assessment)
                    self.last_audit = datetime.now()
                
                # Aguardar próxima verificação
                time.sleep(min(300, self.monitoring_interval // 12))  # Check a cada 5min ou 1/12 do intervalo
                
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                time.sleep(60)  # Aguardar 1 minuto em caso de erro
    
    def process_risk_assessment(self, assessment: Dict[str, Any]):
        """
        Processa resultado da avaliação de riscos
        """
        risk_score = assessment.get("risk_score", 0)
        recommendations = assessment.get("recommendations", [])
        
        # Log do resultado
        print(f"📊 Score de Risco: {risk_score}/100")
        
        # Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.project_root / f"risk_assessment_{timestamp}.json"
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(assessment, f, indent=2, ensure_ascii=False)
        
        # Alertas baseados no score de risco
        if risk_score >= 80:
            print("🚨 ALERTA CRÍTICO: Risco extremamente alto detectado!")
            self.send_critical_alert(assessment)
        elif risk_score >= 60:
            print("⚠️ ALERTA ALTO: Riscos significativos detectados")
        elif risk_score <= 20:
            print("✅ Status: Riscos sob controle")
        
        # Exibir recomendações
        for rec in recommendations[:3]:  # Mostrar apenas as 3 principais
            print(f"   {rec}")
    
    def send_critical_alert(self, assessment: Dict[str, Any]):
        """
        Envia alerta crítico (implementação futura pode incluir notificações)
        """
        print("=" * 60)
        print("🚨 ALERTA CRÍTICO DE SEGURANÇA")
        print("=" * 60)
        
        vuln_data = assessment.get("vulnerabilities", {})
        if isinstance(vuln_data, dict):
            critical_count = len(vuln_data.get("critical", []))
            if critical_count > 0:
                print(f"💣 {critical_count} VULNERABILIDADE(S) CRÍTICA(S) DETECTADA(S)")
        
        compliance_data = assessment.get("security_compliance", {})
        if isinstance(compliance_data, dict):
            critical_violations = compliance_data.get("critical_violations", 0)
            if critical_violations > 0:
                print(f"🛡️ {critical_violations} VIOLAÇÃO(ÕES) CRÍTICA(S) DE SEGURANÇA")
        
        print("🔧 AÇÃO IMEDIATA NECESSÁRIA:")
        for rec in assessment.get("recommendations", []):
            print(f"   • {rec}")
        
        print("=" * 60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor de Riscos de Dependências")
    parser.add_argument("--start", action="store_true", help="Iniciar monitoramento contínuo")
    parser.add_argument("--assess", action="store_true", help="Executar avaliação única")
    parser.add_argument("--interval", type=int, default=3600, help="Intervalo de monitoramento (segundos)")
    
    args = parser.parse_args()
    
    monitor = DependencyRiskMonitor(monitoring_interval=args.interval)
    
    if args.start:
        try:
            monitor.start_monitoring()
            # Manter o programa rodando
            while monitor.is_monitoring:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            print("\n👋 Monitoramento interrompido pelo usuário")
    
    elif args.assess:
        assessment = monitor.run_risk_assessment()
        monitor.process_risk_assessment(assessment)
    
    else:
        print("Uso: python dependency_risk_monitor.py [--start|--assess] [--interval SECONDS]")
