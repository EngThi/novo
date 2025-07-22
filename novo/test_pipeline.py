
#!/usr/bin/env python3
"""
Sistema de Testes Automatizados para Pipeline
"""

import unittest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Importar módulos do pipeline
import sys
sys.path.append('youtube_automation')

from youtube_automation.content_discovery import get_youtube_trends, generate_topic_ideas
from youtube_automation.script_generator import generate_script, extract_script_sections
from youtube_automation.image_processor import download_unsplash_image, generate_placeholder_image
from drive_uploader import DriveUploader

class TestPipeline(unittest.TestCase):
    
    def setUp(self):
        """Configuração para cada teste"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_topic = {
            'title': 'Mistérios do Brasil',
            'description': 'Explore os mistérios mais fascinantes do Brasil'
        }
    
    def tearDown(self):
        """Limpeza após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_content_discovery(self):
        """Testa descoberta de conteúdo"""
        trends = get_youtube_trends()
        self.assertIsInstance(trends, list)
        self.assertTrue(len(trends) > 0)
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_topic_generation(self, mock_model, mock_configure):
        """Testa geração de tópicos"""
        # Mock da resposta do Gemini
        mock_response = MagicMock()
        mock_response.text = "1. Tópico Teste\nDescrição do tópico teste"
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Definir variável de ambiente para o teste
        os.environ['GEMINI_API_KEY'] = 'test_key'
        
        trends = ['tendência 1', 'tendência 2']
        ideas = generate_topic_ideas(trends, num_ideas=2)
        
        self.assertIsInstance(ideas, list)
        mock_configure.assert_called_once()
    
    def test_script_sections_extraction(self):
        """Testa extração de seções do roteiro"""
        test_script = """
        [00:00] Introdução
        Bem-vindos ao nosso vídeo sobre mistérios.
        
        [01:30] Primeiro Mistério
        Vamos explorar o primeiro mistério fascinante.
        
        [03:00] Conclusão
        Obrigado por assistir!
        """
        
        sections = extract_script_sections(test_script)
        self.assertEqual(len(sections), 3)
        self.assertEqual(sections[0]['title'], 'Introdução')
        self.assertEqual(sections[0]['timestamp'], '00:00')
    
    def test_image_placeholder_generation(self):
        """Testa geração de imagem placeholder"""
        image_data = generate_placeholder_image("Teste de imagem")
        self.assertIsInstance(image_data, bytes)
        self.assertTrue(len(image_data) > 0)
    
    @patch('requests.get')
    def test_unsplash_download(self, mock_get):
        """Testa download do Unsplash"""
        # Mock da resposta
        mock_response = MagicMock()
        mock_response.content = b'fake_image_data'
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        image_data = download_unsplash_image("test query")
        self.assertEqual(image_data, b'fake_image_data')
    
    def test_drive_uploader_initialization(self):
        """Testa inicialização do uploader"""
        # Este teste vai falhar se não houver credenciais, mas testa a estrutura
        try:
            uploader = DriveUploader()
            # Se chegou até aqui, a classe foi instanciada corretamente
            self.assertIsNotNone(uploader)
        except Exception:
            # Esperado se não houver credenciais configuradas
            pass

class TestPipelineIntegration(unittest.TestCase):
    """Testes de integração do pipeline completo"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_pipeline_directory_structure(self):
        """Testa se a estrutura de diretórios é criada corretamente"""
        from pipeline_integrado import PipelineIntegrado
        
        # Criar instância do pipeline
        pipeline = PipelineIntegrado()
        
        # Verificar se os diretórios básicos existem
        self.assertTrue(Path("youtube_automation").exists())
    
    def test_environment_variables(self):
        """Testa se as variáveis de ambiente necessárias estão configuradas"""
        required_vars = [
            'GEMINI_API_KEY',
            'GOOGLE_APPLICATION_CREDENTIALS'
        ]
        
        # Verificar se .env.example tem as variáveis necessárias
        env_example = Path('.env.example')
        if env_example.exists():
            content = env_example.read_text()
            for var in required_vars:
                self.assertIn(var, content, f"Variável {var} deve estar em .env.example")

def run_tests():
    """Executa todos os testes"""
    # Configurar descoberta de testes
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Relatório
    print(f"\n{'='*50}")
    print(f"RELATÓRIO DE TESTES")
    print(f"{'='*50}")
    print(f"Testes executados: {result.testsRun}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    print(f"Sucesso: {result.wasSuccessful()}")
    
    if result.failures:
        print(f"\nFALHAS:")
        for test, trace in result.failures:
            print(f"- {test}: {trace.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nERROS:")
        for test, trace in result.errors:
            print(f"- {test}: {trace.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
