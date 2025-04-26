import os
import sys
import inspect # Para obter o caminho do script de forma mais robusta

class ProjectDocumenter:
    """
    Classe para documentar a estrutura de pastas e o conteúdo dos arquivos
    de um projeto em um arquivo Markdown. O projeto é a pasta onde
    o script está localizado.
    """

    def __init__(self, output_file: str = "documents.md"):
        """
        Inicializa o documentador. Determina automaticamente a pasta do projeto
        como sendo a pasta onde este script está localizado.

        Args:
            output_file (str): O nome do arquivo de saída Markdown.
        """
        # Obter o diretório onde o script está localizado
        # Usar inspect é geralmente mais confiável que __file__ em alguns cenários
        try:
            # __file__ é o caminho do arquivo sendo executado
            script_path = os.path.abspath(__file__)
        except NameError:
            # Se __file__ não estiver definido (ex: execução interativa), use CWD
            print("[AVISO] Não foi possível determinar o caminho do script via __file__, usando o diretório de trabalho atual (CWD).")
            script_path = os.path.abspath(os.getcwd())

        self.project_path = os.path.dirname(script_path)
        self.script_filename = os.path.basename(script_path) # Nome do arquivo .py
        self.output_file = output_file
        # O arquivo de saída será criado na pasta do projeto (pasta do script)
        self.output_filepath = os.path.join(self.project_path, self.output_file)

        print(f"[*] Pasta do projeto definida como: {self.project_path}")
        print(f"[*] Arquivo de saída será: {self.output_filepath}")
        print(f"[*] Script atual ({self.script_filename}) e o arquivo de saída ({self.output_file}) serão ignorados na documentação.")


    def _generate_tree_structure(self) -> str:
        """
        Gera uma representação em string da estrutura de diretórios e arquivos,
        formatada para Markdown. Similar a 'tree /f /a'. Ignora o script e o output.
        """
        print("[*] Gerando estrutura de árvore...")
        tree_string_list = [] # Usaremos uma lista para construir a árvore
        start_level = self.project_path.count(os.sep)

        for root, dirs, files in os.walk(self.project_path, topdown=True):
            # Ignorar diretórios comuns que não queremos documentar (opcional, mas útil)
            dirs[:] = [d for d in dirs if d not in ['.git', '.vscode', 'target', 'build', '__pycache__', 'node_modules', '.idea']]
            # Ignorar o próprio script e o arquivo de saída da listagem de arquivos
            files_filtered = [f for f in files if f != self.script_filename and f != self.output_file]

            # Só processa se o diretório não for vazio após filtrar ou se tiver arquivos filtrados
            if dirs or files_filtered:
                level = root.count(os.sep) - start_level
                indent = '    ' * level
                # Adiciona o diretório à lista
                # Evita adicionar a raiz duas vezes se estiver no nível 0 e for o início
                if level >= 0: # Sempre adiciona, a formatação cuidará da raiz depois
                    relative_root = os.path.relpath(root, self.project_path)
                    # Mostra '.' para a própria pasta raiz na árvore
                    dir_display_name = os.path.basename(root) if relative_root != '.' else '.'
                    tree_string_list.append(f"{indent}- `{dir_display_name}/`")

                # Adiciona os arquivos filtrados à lista
                sub_indent = '    ' * (level + 1)
                for f in files_filtered:
                    tree_string_list.append(f"{sub_indent}- `{f}`")


        # Junta a lista em uma string formatada
        tree_output = f"# Estrutura de Pastas e Arquivos\n\n"
        # Adiciona a raiz manualmente se a lista não estiver vazia
        if tree_string_list:
            # O primeiro item da lista já será a raiz formatada ('- `./`')
            tree_output += tree_string_list[0] + "\n" # Adiciona o primeiro item (raiz)
            # Adiciona o restante da árvore
            for item in tree_string_list[1:]:
                tree_output += item + "\n"
        else:
            tree_output += "Nenhuma pasta ou arquivo encontrado (além do script e output).\n"


        print("[+] Estrutura de árvore gerada.")
        return tree_output

    def _extract_and_write_file_contents(self, file_handle):
        """
        Percorre os arquivos, lê o conteúdo e escreve no arquivo de saída.
        Ignora o próprio script e o arquivo de saída.
        """
        print("[*] Iniciando extração de conteúdo dos arquivos...")
        file_handle.write("\n\n# Conteúdo dos Arquivos\n")

        files_processed = 0
        files_errors = 0

        for root, dirs, files in os.walk(self.project_path):
            # Ignorar diretórios comuns (opcional, mas útil)
            dirs[:] = [d for d in dirs if d not in ['.git', '.vscode', 'target', 'build', '__pycache__', 'node_modules', '.idea']]

            for filename in files:
                # Ignora o próprio script e o arquivo de saída final
                if filename == self.script_filename or filename == self.output_file:
                    print(f"    -> Ignorando: {filename}")
                    continue

                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, self.project_path)

                print(f"    -> Processando: {relative_path}")
                content = "Erro ao ler o conteúdo do arquivo." # Default
                try:
                    # Tenta ler com UTF-8, ignora erros de decodificação
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    files_processed += 1

                except Exception as e:
                    content = f"Erro ao ler o arquivo: {str(e)}"
                    print(f"[!] Erro ao ler o arquivo {relative_path}: {e}")
                    files_errors += 1


                # Escreve no arquivo markdown
                try:
                    file_handle.write("\n---\n\n") # Separador
                    file_handle.write(f"## Caminho: `{relative_path}`\n\n")

                    # Detecta extensão para syntax highlight (simples)
                    _, ext = os.path.splitext(filename)
                    lang = ext.lstrip('.') if ext else ''
                    # Mapeamento extenso de extensões para hints de linguagem Markdown
                    lang_map = {
                        # Java Ecosystem
                        'java': 'java',
                        'kt': 'kotlin',         # Kotlin
                        'kts': 'kotlin',        # Kotlin Script
                        'scala': 'scala',       # Scala
                        'groovy': 'groovy',     # Groovy
                        'gradle': 'groovy',     # Gradle scripts (pode ser Kotlin também, mas Groovy é comum)
                        'xml': 'xml',           # Maven POMs, Spring XML, WSDL, XSD, Android Layouts, etc.
                        'properties': 'properties', # Arquivos .properties padrão Java
                        'jsp': 'jsp',           # JavaServer Pages
                        'tag': 'jsp',           # Arquivos de Tag JSP
                        'tld': 'xml',           # Tag Library Descriptor
                        'wsdl': 'xml',          # Web Services Description Language
                        'xsd': 'xml',           # XML Schema Definition
                        'ftl': 'ftl',           # FreeMarker Template Language
                        'vm': 'velocity',       # Velocity Template Language
                        'mf': 'text',           # Manifest file (META-INF/MANIFEST.MF)
                        'feature': 'gherkin',   # Cucumber/BDD feature files
                        'jks': '',              # Java KeyStore (binário, ignorar)
                        'class': '',            # Java bytecode (binário, ignorar)
                        'jar': '',              # Java Archive (binário, ignorar)
                        'war': '',              # Web Application Archive (binário, ignorar)
                        'ear': '',              # Enterprise Application Archive (binário, ignorar)

                        # Python Ecosystem
                        'py': 'python',
                        'pyw': 'python',        # Python script (sem console no Windows)
                        'pyc': '',              # Bytecode Python compilado (binário, ignorar)
                        'pyd': '',              # Extensão C Python (binário, ignorar)
                        'pyo': '',              # Bytecode Python otimizado (binário, ignorar)
                        'pyx': 'cython',        # Cython
                        'pxd': 'cython',        # Arquivo de definição Cython
                        'ini': 'ini',           # Arquivos de configuração INI
                        'cfg': 'ini',           # Arquivos de configuração (frequentemente formato INI)
                        'conf': 'ini',          # Arquivos de configuração (frequentemente formato INI ou similar)
                        'toml': 'toml',         # TOML (usado em pyproject.toml)
                        'rst': 'rst',           # reStructuredText (documentação Sphinx)
                        'tpl': 'html',          # Template genérico (muitas vezes similar a HTML)
                        'mako': 'mako',         # Templates Mako
                        'jinja': 'jinja',       # Templates Jinja (pode ser HTML, XML, etc.)
                        'jinja2': 'jinja',
                        'env': 'bash',          # Arquivo de variáveis de ambiente (geralmente sintaxe de shell)
                        '.env': 'bash',         # Comum nomear com ponto antes
                        'requirements.txt': 'text', # Dependências Pip
                        'pipfile': 'toml',      # Dependências Pipenv
                        'pipfile.lock': 'json', # Lockfile Pipenv
                        'setup.py': 'python',   # Script de setup Setuptools
                        'cfg': 'ini',           # setup.cfg

                        # Web Development (Comum em ambos ecossistemas)
                        'html': 'html',
                        'htm': 'html',
                        'css': 'css',
                        'scss': 'scss',         # SASS/SCSS
                        'sass': 'sass',
                        'less': 'less',         # LESS CSS pre-processor
                        'js': 'javascript',
                        'jsx': 'jsx',           # JavaScript XML (React)
                        'ts': 'typescript',     # TypeScript
                        'tsx': 'tsx',           # TypeScript XML (React)
                        'json': 'json',         # Formato de dados JSON
                        'yaml': 'yaml',         # YAML (configuração, dados)
                        'yml': 'yaml',          # YAML (alternativa de extensão)
                        'vue': 'vue',           # Componentes Vue.js
                        'svelte': 'svelte',     # Componentes Svelte

                        # Scripting & Shell
                        'sh': 'bash',           # Script de Shell (Bash é um bom padrão)
                        'bash': 'bash',
                        'zsh': 'zsh',
                        'ksh': 'ksh',
                        'csh': 'csh',
                        'fish': 'fish',
                        'ps1': 'powershell',    # PowerShell
                        'bat': 'batch',         # Windows Batch
                        'cmd': 'batch',         # Windows Batch

                        # Databases & Data
                        'sql': 'sql',           # SQL queries
                        'ddl': 'sql',           # Data Definition Language (SQL)
                        'dml': 'sql',           # Data Manipulation Language (SQL)
                        'csv': 'csv',           # Comma Separated Values
                        'tsv': 'tsv',           # Tab Separated Values
                        'jsonl': 'json',        # JSON Lines

                        # Documentação & Texto
                        'md': 'markdown',
                        'markdown': 'markdown',
                        'txt': 'text',          # Arquivo de texto puro
                        'log': 'log',           # Arquivos de log
                        'tex': 'latex',         # LaTeX
                        'bib': 'bibtex',        # BibTeX
                        'adoc': 'asciidoc',     # AsciiDoc
                        'asciidoc': 'asciidoc',

                        # Build & Config (Geral)
                        'dockerfile': 'dockerfile', # Docker configuration
                        'dockerignore': 'text', # Docker ignore file
                        'makefile': 'makefile', # Make build system
                        'cmake': 'cmake',       # CMake build system
                        'cmakelists.txt': 'cmake',
                        'gitignore': 'gitignore', # Git ignore file
                        'gitattributes': 'text',  # Git attributes file
                        'gitmodules': 'ini',      # Git submodules config
                        'editorconfig': 'ini',    # EditorConfig files
                        'nginx': 'nginx',         # Configuração Nginx
                        'conf': 'nginx',          # Frequentemente usado para config Nginx/Apache
                        'httpd': 'apache',        # Configuração Apache
                        'htaccess': 'apache',     # Configuração Apache por diretório
                        'tf': 'terraform',        # Terraform configuration
                        'hcl': 'terraform',       # HashiCorp Configuration Language

                        # Outros Formatos Comuns
                        'plantuml': 'plantuml', # Diagramas PlantUML
                        'puml': 'plantuml',
                        'drawio': 'xml',        # Diagramas Draw.io (baseados em XML)
                        'svg': 'xml',           # Scalable Vector Graphics (XML)
                        'vsdx': '',             # Visio (binário, ignorar)
                        'pdf': '',              # PDF (binário, ignorar)
                        'png': '', 'jpg': '', 'jpeg': '', 'gif': '', 'bmp': '', 'ico': '', # Imagens (binário, ignorar)
                        'zip': '', 'gz': '', 'tar': '', 'rar': '', # Arquivos comprimidos (binário, ignorar)
                        # Adicione mais conforme necessário...
                    }
                    code_lang = lang_map.get(lang.lower(), '') # Usa o mapeamento ou vazio se não encontrado

                    file_handle.write(f"``` {code_lang}\n")
                    file_handle.write(content)
                    file_handle.write("\n```\n")

                except Exception as write_e:
                    print(f"[!] Erro ao escrever dados do arquivo {relative_path} no markdown: {write_e}")
                    files_errors += 1

        print(f"[+] Extração concluída. Arquivos processados: {files_processed}. Erros de leitura/escrita: {files_errors}.")


    def generate_documentation(self):
        """
        Orquestra a geração da documentação completa.
        O arquivo de saída é sempre sobrescrito.
        """
        print(f"[*] Iniciando a geração do arquivo: {self.output_filepath}")
        try:
            # 1. Gerar a estrutura da árvore
            tree_structure = self._generate_tree_structure()

            # 2. Abrir o arquivo de saída em modo 'w' (write), que sobrescreve ou cria o arquivo
            with open(self.output_filepath, 'w', encoding='utf-8') as md_file:
                # Escrever a árvore
                md_file.write(tree_structure)

                # Escrever o conteúdo dos arquivos
                self._extract_and_write_file_contents(md_file)

            print(f"\n[SUCCESS] Documentação gerada com sucesso em '{self.output_filepath}'")

        except IOError as e:
            print(f"[ERROR] Erro de I/O ao escrever no arquivo '{self.output_filepath}': {e}", file=sys.stderr)
        except ValueError as e: # Captura o erro do __init__ se o caminho for inválido
            print(f"[ERROR] {e}", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] Ocorreu um erro inesperado durante a geração: {e}", file=sys.stderr)


# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    print("="*50)
    print("Iniciando Gerador de Documentação de Projeto")
    print("="*50)
    try:
        # Cria a instância do documentador (sem argumentos necessários)
        documenter = ProjectDocumenter()
        # Gera a documentação
        documenter.generate_documentation()
    except Exception as e:
        # Captura erros que podem ocorrer na inicialização do ProjectDocumenter também
        print(f"Erro fatal na execução: {e}", file=sys.stderr)

    print("\nScript finalizado.")