# Codex Batch Runner - Automated Code Analysis

This script analyzes all Python files in the Celest.ia v2 project using OpenAI's GPT-4o model and generates comprehensive technical reports.

## Features

- 🔍 **Recursive Scanning**: Automatically finds all Python files in the project
- 🤖 **AI Analysis**: Uses GPT-4o for detailed technical code analysis
- 📊 **Progress Tracking**: Real-time progress bar and statistics
- 📝 **Markdown Reports**: Generates detailed reports in `codex_reports/` folder
- 🛡️ **Error Handling**: Continues analysis even if individual files fail
- 📈 **Statistics**: Provides comprehensive analysis statistics
- 🚫 **Smart Filtering**: Excludes cache, virtual environments, and build folders

## Prerequisites

```bash
pip install openai python-dotenv
```

## Environment Setup

1. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

2. Add your OpenAI API key to the `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

```bash
# Run from the project root directory
python codex_batch_runner.py
```

## What Gets Analyzed

The script will analyze all `.py` files in the project, excluding:

- `__pycache__/` directories
- Virtual environments (`venv/`, `.venv/`)
- Package directories (`site-packages/`)
- Build artifacts (`build/`, `dist/`)
- Hidden files and directories (except `.env`, `.gitignore`)
- Files containing "get-pip" or "codex_runner" in the path
- Empty files
- Files larger than 50KB

## Analysis Report Structure

Each report includes:

1. **File Metadata**: Path, analysis date, model used
2. **Purpose and Functionality**: What the code does
3. **Architecture and Design**: Design patterns and structure
4. **Code Quality**: Readability, maintainability, best practices
5. **Potential Improvements**: Optimization suggestions
6. **Security**: Vulnerability identification
7. **Performance**: Efficiency analysis
8. **Dependencies**: Import and external dependency analysis

## Output Structure

```
codex_reports/
├── src_core_config.md
├── src_core_database.md
├── src_scrapers_base_scraper.md
├── src_api_main.md
└── ...
```

## Example Report

```markdown
# Análise Técnica de Código - config.py

**📁 Arquivo**: `src/core/config.py`  
**🕒 Analisado em**: 05/08/2025 às 14:30:15  
**🤖 Modelo**: GPT-4o  
**📊 Projeto**: Celest.ia v2 Alpha  

---

## Propósito e Funcionalidade
Este código implementa um sistema de configuração...

## Arquitetura e Design
O arquivo utiliza o padrão Singleton através da classe...

## Qualidade do Código
O código demonstra boas práticas...

...
```

## Statistics Tracking

The script tracks and reports:

- Total files found
- Successfully analyzed files
- Skipped files (empty, too large, excluded)
- Failed files (errors during processing)
- Analysis duration
- Success rate

## Error Handling

- **File Reading Errors**: Skips files with encoding issues
- **API Errors**: Logs OpenAI API failures and continues
- **Large Files**: Automatically skips files over 50KB
- **Network Issues**: Handles connection timeouts gracefully
- **Keyboard Interrupt**: Graceful shutdown with partial statistics

## Cost Optimization

- Uses temperature=0.3 for consistent, focused analysis
- Limits max_tokens=4000 to control costs
- Skips empty and oversized files
- Logs token usage for cost tracking

## Logging

Logs are written to both:
- Console output (with progress bars)
- `codex_analysis.log` file

## Example Output

```
🚀 Iniciando Codex Batch Runner - Análise de Código com GPT-4o
📂 Diretório do projeto: /Users/user/Celest.ia-v2-Alpha
🤖 Modelo: gpt-4o
------------------------------------------------------------
🔍 Scanning for Python files...
📊 Found 23 Python files to analyze

🔄 Iniciando análise de 23 arquivos...
🔄 [████████████████████] 100.0% (23/23) - main.py

============================================================
📊 ANÁLISE FINALIZADA - ESTATÍSTICAS
============================================================
⏰ Duração: 0:05:42
📁 Total de arquivos encontrados: 23
✅ Arquivos analisados com sucesso: 21
⏭️  Arquivos ignorados: 1
❌ Arquivos com erro: 1
📈 Taxa de sucesso: 91.3%
💾 Relatórios salvos em: /Users/user/Celest.ia-v2-Alpha/codex_reports
============================================================
🎉 Análise concluída! Os relatórios estão disponíveis na pasta codex_reports/
```

## Troubleshooting

### Missing Dependencies
```bash
❌ Missing required dependencies: No module named 'openai'
📦 Please install required packages:
   pip install openai python-dotenv
```

### Missing API Key
```bash
❌ OPENAI_API_KEY not found in environment variables.
Please create a .env file with your OpenAI API key:
OPENAI_API_KEY=your_api_key_here
```

### Rate Limits
If you hit OpenAI rate limits, the script will log errors but continue processing other files. You can run the script again to process failed files.

## Customization

You can modify the script to:

- Change the analysis prompt in `analyze_code_with_gpt4o()`
- Adjust file size limits in `analyze_file()`
- Add more exclusion patterns in `excluded_patterns`
- Modify the GPT-4o parameters (temperature, max_tokens)
- Change the report format in `save_analysis_report()`

## Integration with Development Workflow

Consider running this script:
- Before major releases for code review
- After significant refactoring
- As part of documentation generation
- For onboarding new team members
- During code audits
