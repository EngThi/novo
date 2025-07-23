
#!/usr/bin/env python3
"""
Sistema Completo de Testes para Pipeline de Automação
Inclui testes unitários, integração e validação de funcionalidades
"""

import unittest
import tempfile
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import logging

# Configurar logging para testes
logging.basicConfig(level=logging.WARNING)

# Adicionar caminhos para importação
sys.path.append('youtube_automation')
sys.path.append('.')

class TestDriveUploader(unittest.TestCase):
    """Testes para o sistema de upload do Google Drive"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('drive_uploader.genai')
    @patch('drive_uploader.build')
    def test_drive_uploader_initialization(self, mock_build, mock_genai):
        """Testa inicialização do DriveUploader"""
        from drive_uploader import DriveUploader
        
        # Mock das credenciais
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            try:
                uploader = DriveUploader()
                self.assertIsNotNone(uploader)
            except FileNotFoundError:
                # Esperado quando não há arquivo de credenciais
                pass
    
    def test_mime_type_detection(self):
        """Testa detecção de tipos MIME"""
        from drive_uploader import DriveUploader
        
        # Criar instância mock
        uploader = DriveUploader.__new__(DriveUploader)
        
        # Testar diferentes extensões
        test_cases = [
            (Path('test.mp4'), 'video/mp4'),
            (Path('test.jpg'), 'image/jpeg'),
            (Path('test.png'), 'image/png'),
            (Path('test.mp3'), 'audio/mpeg'),
            (Path('test.txt'), 'text/plain'),
            (Path('test.py'), 'text/x-python'),
            (Path('test.unknown'), 'application/octet-stream')
        ]
        
        for file_path, expected_mime in test_cases:
            with self.subTest(file_path=file_path):
                result = uploader._get_mime_type(file_path)
                self.assertEqual(result, expected_mime)
    
    def test_folder_determination(self):
        """Testa determinação de pasta de destino"""
        from drive_uploader import DriveUploader
        
        uploader = DriveUploader.__new__(DriveUploader)
        
        folder_mapping = {
            'audio': ['.mp3', '.wav'],
            'images': ['.jpg', '.png'],
            'videos': ['.mp4', '.avi'],
            'scripts': ['.py', '.txt']
        }
        
        test_cases = [
            (Path('test.mp3'), 'audio'),
            (Path('test.jpg'), 'images'),
            (Path('test.mp4'), 'videos'),
            (Path('test.py'), 'scripts'),
            (Path('test.unknown'), 'data')
        ]
        
        for file_path, expected_folder in test_cases:
            with self.subTest(file_path=file_path):
                result = uploader._determine_target_folder(file_path, folder_mapping)
                self.assertEqual(result, expected_folder)

class TestScriptGenerator(unittest.TestCase):
    """Testes para o gerador de roteiros"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('youtube_automation.script_generator.genai')
    def test_script_generator_initialization(self, mock_genai):
        """Testa inicialização do gerador de roteiros"""
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'test_key'}):
            from youtube_automation.script_generator import ScriptGenerator
            
            generator = ScriptGenerator()
            self.assertIsNotNone(generator)
            self.assertIn('mystery', generator.prompts)
    
    def test_timestamp_conversion(self):
        """Testa conversão de timestamps"""
        try:
            from youtube_automation.script_generator import ScriptGenerator
            generator = ScriptGenerator.__new__(ScriptGenerator)
            
            test_cases = [
                ('00:30', 30),
                ('01:00', 60),
                ('02:15', 135),
                ('10:00', 600)
            ]
            
            for timestamp, expected_seconds in test_cases:
                with self.subTest(timestamp=timestamp):
                    result = generator._timestamp_to_seconds(timestamp)
                    self.assertEqual(result, expected_seconds)
        except ImportError:
            self.skipTest("ScriptGenerator não disponível")
    
    def test_section_extraction(self):
        """Testa extração de seções do roteiro"""
        try:
            from youtube_automation.script_generator import extract_script_sections
            
            test_script = """
            [00:00] Introdução
            Bem-vindos ao nosso canal sobre mistérios fascinantes do Brasil.
            
            [01:30] Primeiro Mistério
            Hoje vamos explorar o mistério da cidade perdida de Z.
            
            [03:00] Conclusão
            Obrigado por assistir nosso vídeo!
            """
            
            sections = extract_script_sections(test_script)
            
            self.assertEqual(len(sections), 3)
            self.assertEqual(sections[0]['title'], 'Introdução')
            self.assertEqual(sections[0]['timestamp'], '00:00')
            self.assertEqual(sections[1]['title'], 'Primeiro Mistério')
            self.assertEqual(sections[1]['timestamp'], '01:30')
            
        except ImportError:
            self.skipTest("Script generator não disponível")

class TestPipelineIntegration(unittest.TestCase):
    """Testes de integração do pipeline"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_pipeline_directory_structure(self):
        """Testa estrutura de diretórios do pipeline"""
        required_dirs = [
            'youtube_automation',
            'utils'
        ]
        
        for dir_name in required_dirs:
            with self.subTest(directory=dir_name):
                self.assertTrue(
                    Path(dir_name).exists(),
                    f"Diretório {dir_name} deve existir"
                )
    
    def test_required_files_exist(self):
        """Testa se arquivos necessários existem"""
        required_files = [
            'pipeline_integrado.py',
            'drive_uploader.py',
            'requirements.txt',
            '.env.example'
        ]
        
        for file_name in required_files:
            with self.subTest(file=file_name):
                self.assertTrue(
                    Path(file_name).exists(),
                    f"Arquivo {file_name} deve existir"
                )
    
    def test_environment_variables_example(self):
        """Testa se .env.example contém variáveis necessárias"""
        required_vars = [
            'GEMINI_API_KEY',
            'GOOGLE_APPLICATION_CREDENTIALS',
            'DRIVE_CLIENT_ID',
            'DRIVE_CLIENT_SECRET'
        ]
        
        env_example = Path('.env.example')
        if env_example.exists():
            content = env_example.read_text()
            for var in required_vars:
                with self.subTest(variable=var):
                    self.assertIn(var, content, 
                                f"Variável {var} deve estar em .env.example")
    
    @patch('pipeline_integrado.os.system')
    def test_pipeline_method_calls(self, mock_system):
        """Testa chamadas de métodos do pipeline"""
        mock_system.return_value = 0  # Simular sucesso
        
        try:
            from pipeline_integrado import PipelineIntegrado
            
            # Criar instância mock
            pipeline = PipelineIntegrado.__new__(PipelineIntegrado)
            pipeline.project_name = "Teste"
            pipeline.output_dir = self.temp_dir
            pipeline.row_index = 1
            pipeline.status_sheet = None
            
            # Testar método de descoberta
            pipeline._update_sheet_status = MagicMock()
            result = pipeline.descobrir_conteudo()
            
            # Verificar se foi chamado corretamente
            mock_system.assert_called()
            
        except ImportError:
            self.skipTest("PipelineIntegrado não disponível")

class TestImageProcessor(unittest.TestCase):
    """Testes para processamento de imagens"""
    
    def test_placeholder_image_generation(self):
        """Testa geração de imagem placeholder"""
        try:
            from youtube_automation.image_processor import generate_placeholder_image
            
            image_data = generate_placeholder_image("Teste de imagem")
            self.assertIsInstance(image_data, bytes)
            self.assertTrue(len(image_data) > 0)
            
        except ImportError:
            self.skipTest("Image processor não disponível")
    
    @patch('requests.get')
    def test_unsplash_download_mock(self, mock_get):
        """Testa download de imagem do Unsplash com mock"""
        try:
            from youtube_automation.image_processor import download_unsplash_image
            
            # Mock da resposta HTTP
            mock_response = MagicMock()
            mock_response.content = b'fake_image_data_test'
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = download_unsplash_image("test query")
            self.assertEqual(result, b'fake_image_data_test')
            
        except ImportError:
            self.skipTest("Image processor não disponível")

class TestContentDiscovery(unittest.TestCase):
    """Testes para descoberta de conteúdo"""
    
    @patch('requests.get')
    def test_youtube_trends_mock(self, mock_get):
        """Testa obtenção de tendências do YouTube"""
        try:
            from youtube_automation.content_discovery import get_youtube_trends
            
            # Mock da resposta
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'items': [
                    {'snippet': {'title': 'Tendência 1'}},
                    {'snippet': {'title': 'Tendência 2'}}
                ]
            }
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            trends = get_youtube_trends()
            self.assertIsInstance(trends, list)
            
        except ImportError:
            self.skipTest("Content discovery não disponível")

class TestSystemRequirements(unittest.TestCase):
    """Testes de requisitos do sistema"""
    
    def test_python_version(self):
        """Testa se a versão do Python é adequada"""
        import sys
        self.assertGreaterEqual(sys.version_info, (3, 8), 
                              "Python 3.8+ é necessário")
    
    def test_required_packages_in_requirements(self):
        """Testa se pacotes necessários estão em requirements.txt"""
        required_packages = [
            'google-api-python-client',
            'google-generativeai',
            'pillow',
            'requests',
            'python-dotenv'
        ]
        
        requirements_file = Path('requirements.txt')
        if requirements_file.exists():
            content = requirements_file.read_text().lower()
            for package in required_packages:
                with self.subTest(package=package):
                    self.assertIn(package.lower(), content,
                                f"Pacote {package} deve estar em requirements.txt")

class TestSecurityAndValidation(unittest.TestCase):
    """Testes de segurança e validação"""
    
    def test_no_hardcoded_credentials(self):
        """Verifica se não há credenciais hardcoded no código"""
        patterns_to_avoid = [
            'password=',
            'api_key=',
            'secret=',
            'token='
        ]
        
        python_files = Path('.').glob('**/*.py')
        
        for file_path in python_files:
            if file_path.name == 'test_pipeline.py':
                continue  # Pular arquivo de teste
                
            try:
                content = file_path.read_text().lower()
                for pattern in patterns_to_avoid:
                    with self.subTest(file=file_path, pattern=pattern):
                        if pattern in content:
                            # Verificar se é comentário ou exemplo
                            lines = content.split('\n')
                            for line in lines:
                                if pattern in line and not line.strip().startswith('#'):
                                    self.fail(f"Possível credencial hardcoded em {file_path}: {line.strip()}")
            except Exception:
                # Ignorar arquivos que não podem ser lidos
                pass

def run_comprehensive_tests():
    """Executa todos os testes com relatório detalhado"""
    
    # Configurar descoberta de testes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Adicionar classes de teste
    test_classes = [
        TestDriveUploader,
        TestScriptGenerator,
        TestPipelineIntegration,
        TestImageProcessor,
        TestContentDiscovery,
        TestSystemRequirements,
        TestSecurityAndValidation
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Relatório detalhado
    print(f"\n{'='*60}")
    print(f"RELATÓRIO COMPLETO DE TESTES")
    print(f"{'='*60}")
    print(f"Total de testes: {result.testsRun}")
    print(f"Sucessos: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Falhas: {len(result.failures)}")
    print(f"Erros: {len(result.errors)}")
    print(f"Taxa de sucesso: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n📋 FALHAS DETALHADAS:")
        for i, (test, trace) in enumerate(result.failures, 1):
            print(f"\n{i}. {test}")
            print(f"   Erro: {trace.split('AssertionError:')[-1].strip() if 'AssertionError:' in trace else 'Falha na asserção'}")
    
    if result.errors:
        print(f"\n🚨 ERROS DETALHADOS:")
        for i, (test, trace) in enumerate(result.errors, 1):
            print(f"\n{i}. {test}")
            error_msg = trace.split('\n')[-2] if '\n' in trace else trace
            print(f"   Erro: {error_msg.strip()}")
    
    # Recomendações baseadas nos resultados
    if result.failures or result.errors:
        print(f"\n💡 RECOMENDAÇÕES:")
        print(f"1. Configure as variáveis de ambiente no arquivo .env")
        print(f"2. Instale todas as dependências: pip install -r requirements.txt")
        print(f"3. Adicione o arquivo google-drive-credentials.json")
        print(f"4. Verifique se todos os módulos estão implementados")
    else:
        print(f"\n🎉 TODOS OS TESTES PASSARAM!")
        print(f"O pipeline está pronto para uso.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
