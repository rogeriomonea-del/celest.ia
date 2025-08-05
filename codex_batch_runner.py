#!/usr/bin/env python3
"""
Codex Batch Runner - Automated Code Analysis Tool
Analyzes all Python files in the project using GPT-4o and generates technical reports.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
import logging
from datetime import datetime

# External dependencies
try:
    from dotenv import load_dotenv
    from openai import OpenAI
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("📦 Please install required packages:")
    print("   pip install openai python-dotenv")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('codex_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CodexBatchRunner:
    """Main class for batch code analysis using OpenAI GPT-4o."""
    
    def __init__(self):
        """Initialize the batch runner with OpenAI client and configuration."""
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "❌ OPENAI_API_KEY not found in environment variables.\n"
                "Please create a .env file with your OpenAI API key:\n"
                "OPENAI_API_KEY=your_api_key_here"
            )
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"
        
        # Configuration
        self.project_root = Path.cwd()
        self.reports_dir = self.project_root / "codex_reports"
        self.excluded_patterns = {
            '__pycache__',
            'venv',
            '.venv',
            'site-packages',
            'get-pip',
            'codex_runner',
            '.git',
            'node_modules',
            '.pytest_cache',
            'build',
            'dist',
            'egg-info'
        }
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'analyzed_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'start_time': datetime.now()
        }
        
        # Create reports directory
        self.reports_dir.mkdir(exist_ok=True)
        logger.info(f"📁 Reports will be saved to: {self.reports_dir}")
    
    def should_exclude_path(self, path: Path) -> bool:
        """Check if a path should be excluded from analysis."""
        path_str = str(path).lower()
        
        # Check for excluded patterns
        for pattern in self.excluded_patterns:
            if pattern in path_str:
                return True
        
        # Exclude hidden files and directories
        for part in path.parts:
            if part.startswith('.') and part not in ['.env', '.gitignore']:
                return True
        
        return False
    
    def find_python_files(self) -> List[Path]:
        """Recursively find all Python files in the project."""
        python_files = []
        
        logger.info("🔍 Scanning for Python files...")
        
        for py_file in self.project_root.rglob("*.py"):
            if self.should_exclude_path(py_file):
                logger.debug(f"⏭️  Skipping excluded file: {py_file}")
                self.stats['skipped_files'] += 1
                continue
            
            python_files.append(py_file)
            logger.debug(f"✅ Found Python file: {py_file}")
        
        self.stats['total_files'] = len(python_files)
        logger.info(f"📊 Found {len(python_files)} Python files to analyze")
        
        return python_files
    
    def read_file_content(self, file_path: Path) -> Optional[str]:
        """Read and return the content of a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip empty files
            if not content.strip():
                logger.warning(f"⚠️  Skipping empty file: {file_path}")
                return None
            
            return content
        
        except UnicodeDecodeError:
            logger.error(f"❌ Failed to decode file (encoding issue): {file_path}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to read file {file_path}: {e}")
            return None
    
    def analyze_code_with_gpt4o(self, code_content: str, file_path: Path) -> Optional[str]:
        """Send code to GPT-4o for technical analysis."""
        prompt = f"""Analise e comente tecnicamente o seguinte código Python:

**Arquivo**: {file_path}

**Instruções de Análise**:
1. **Propósito e Funcionalidade**: Explique o que este código faz
2. **Arquitetura e Design**: Analise padrões de design, estrutura de classes, e organização
3. **Qualidade do Código**: Avalie legibilidade, manutenibilidade, e boas práticas
4. **Potenciais Melhorias**: Sugira otimizações, refatorações, ou correções
5. **Segurança**: Identifique possíveis vulnerabilidades ou pontos de atenção
6. **Performance**: Analise eficiência e possíveis gargalos
7. **Dependências**: Comente sobre imports e dependências externas

**Código**:
```python
{code_content}
```

Por favor, forneça uma análise detalhada e técnica em português brasileiro."""

        try:
            logger.debug(f"🤖 Sending request to GPT-4o for: {file_path}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em análise de código Python com vasta experiência em arquitetura de software, boas práticas, e otimização. Forneça análises técnicas detalhadas e construtivas."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.3,
                top_p=0.9
            )
            
            analysis = response.choices[0].message.content
            
            # Log token usage for cost tracking
            usage = response.usage
            logger.debug(f"📊 Token usage - Input: {usage.prompt_tokens}, Output: {usage.completion_tokens}, Total: {usage.total_tokens}")
            
            return analysis
        
        except Exception as e:
            logger.error(f"❌ Failed to analyze {file_path} with GPT-4o: {e}")
            return None
    
    def generate_report_filename(self, file_path: Path) -> str:
        """Generate a report filename based on the original file path."""
        # Get relative path from project root
        try:
            relative_path = file_path.relative_to(self.project_root)
        except ValueError:
            relative_path = file_path
        
        # Convert path to filename
        filename_parts = []
        for part in relative_path.parts[:-1]:  # Exclude the filename itself
            filename_parts.append(part)
        
        # Add the filename without extension
        filename_parts.append(relative_path.stem)
        
        # Join with underscores and add .md extension
        report_name = "_".join(filename_parts).replace("-", "_")
        return f"{report_name}.md"
    
    def save_analysis_report(self, analysis: str, file_path: Path) -> bool:
        """Save the analysis to a markdown report file."""
        try:
            report_filename = self.generate_report_filename(file_path)
            report_path = self.reports_dir / report_filename
            
            # Create report content with metadata
            report_content = f"""# Análise Técnica de Código - {file_path.name}

**📁 Arquivo**: `{file_path}`  
**🕒 Analisado em**: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}  
**🤖 Modelo**: GPT-4o  
**📊 Projeto**: Celest.ia v2 Alpha  

---

{analysis}

---

*Relatório gerado automaticamente pelo Codex Batch Runner*
"""
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"💾 Report saved: {report_path}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to save report for {file_path}: {e}")
            return False
    
    def print_progress(self, current: int, total: int, file_path: Path):
        """Print progress information."""
        percentage = (current / total) * 100
        progress_bar = "█" * int(percentage // 5) + "░" * (20 - int(percentage // 5))
        
        print(f"\r🔄 [{progress_bar}] {percentage:.1f}% ({current}/{total}) - {file_path.name}", end="", flush=True)
    
    def analyze_file(self, file_path: Path, current: int, total: int) -> bool:
        """Analyze a single Python file."""
        try:
            # Print progress
            self.print_progress(current, total, file_path)
            
            # Read file content
            content = self.read_file_content(file_path)
            if content is None:
                self.stats['failed_files'] += 1
                return False
            
            # Skip very large files (>50KB)
            if len(content) > 50000:
                logger.warning(f"⚠️  Skipping large file ({len(content)} chars): {file_path}")
                self.stats['skipped_files'] += 1
                return False
            
            # Analyze with GPT-4o
            analysis = self.analyze_code_with_gpt4o(content, file_path)
            if analysis is None:
                self.stats['failed_files'] += 1
                return False
            
            # Save report
            if self.save_analysis_report(analysis, file_path):
                self.stats['analyzed_files'] += 1
                return True
            else:
                self.stats['failed_files'] += 1
                return False
        
        except Exception as e:
            logger.error(f"❌ Unexpected error analyzing {file_path}: {e}")
            self.stats['failed_files'] += 1
            return False
    
    def print_final_statistics(self):
        """Print final analysis statistics."""
        end_time = datetime.now()
        duration = end_time - self.stats['start_time']
        
        print("\n" + "=" * 60)
        print("📊 ANÁLISE FINALIZADA - ESTATÍSTICAS")
        print("=" * 60)
        print(f"⏰ Duração: {duration}")
        print(f"📁 Total de arquivos encontrados: {self.stats['total_files']}")
        print(f"✅ Arquivos analisados com sucesso: {self.stats['analyzed_files']}")
        print(f"⏭️  Arquivos ignorados: {self.stats['skipped_files']}")
        print(f"❌ Arquivos com erro: {self.stats['failed_files']}")
        print(f"📈 Taxa de sucesso: {(self.stats['analyzed_files']/max(self.stats['total_files'], 1)*100):.1f}%")
        print(f"💾 Relatórios salvos em: {self.reports_dir}")
        print("=" * 60)
        
        if self.stats['analyzed_files'] > 0:
            print("🎉 Análise concluída! Os relatórios estão disponíveis na pasta codex_reports/")
        else:
            print("⚠️  Nenhum arquivo foi analisado com sucesso.")
    
    def run(self):
        """Main execution method."""
        try:
            print("🚀 Iniciando Codex Batch Runner - Análise de Código com GPT-4o")
            print(f"📂 Diretório do projeto: {self.project_root}")
            print(f"🤖 Modelo: {self.model}")
            print("-" * 60)
            
            # Find all Python files
            python_files = self.find_python_files()
            
            if not python_files:
                print("⚠️  Nenhum arquivo Python encontrado para análise.")
                return
            
            # Analyze each file
            print(f"\n🔄 Iniciando análise de {len(python_files)} arquivos...")
            
            for i, file_path in enumerate(python_files, 1):
                self.analyze_file(file_path, i, len(python_files))
            
            print()  # New line after progress bar
            
            # Print final statistics
            self.print_final_statistics()
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Análise interrompida pelo usuário.")
            self.print_final_statistics()
        except Exception as e:
            logger.error(f"❌ Erro fatal durante a execução: {e}")
            print(f"\n❌ Erro fatal: {e}")

def main():
    """Main entry point."""
    try:
        runner = CodexBatchRunner()
        runner.run()
    except Exception as e:
        print(f"❌ Erro durante a inicialização: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
