@echo off
chcp 65001 >nul
cls

echo.
echo ══════════════════════════════════════════════════════
echo   SCOZZIERO ADVOCACIA — Configuração do Painel
echo ══════════════════════════════════════════════════════
echo.

:: ── Verificar Python ──────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERRO: Python não encontrado.
    echo  Baixe em: https://www.python.org/downloads/
    echo  IMPORTANTE: marque "Add Python to PATH" na instalação
    echo.
    pause
    exit /b 1
)
echo  [OK] Python encontrado

:: ── Pedir as chaves ───────────────────────────────────
echo.
echo  Você vai precisar das duas chaves que criou.
echo  Digite com cuidado — os caracteres não aparecem por segurança.
echo.

set /p "ANTHROPIC_KEY=  Cole aqui sua chave da Anthropic (sk-ant-...): "
echo.
set /p "GITHUB_TOK=  Cole aqui seu token do GitHub (ghp_...): "
echo.

if "%ANTHROPIC_KEY%"=="" (
    echo  ERRO: Chave da Anthropic não informada.
    pause
    exit /b 1
)
if "%GITHUB_TOK%"=="" (
    echo  ERRO: Token do GitHub não informado.
    pause
    exit /b 1
)

:: ── Salvar variáveis de ambiente ──────────────────────
echo  Salvando variáveis de ambiente...
setx ANTHROPIC_API_KEY "%ANTHROPIC_KEY%" >nul
setx GITHUB_TOKEN "%GITHUB_TOK%" >nul
echo  [OK] Variáveis salvas

:: ── Instalar dependências Python ──────────────────────
echo.
echo  Instalando bibliotecas Python (aguarde)...
python -m pip install --quiet --upgrade anthropic pymupdf requests
if errorlevel 1 (
    echo  ERRO ao instalar bibliotecas.
    pause
    exit /b 1
)
echo  [OK] Bibliotecas instaladas

:: ── Subir arquivos pro GitHub ─────────────────────────
echo.
echo  Enviando arquivos para o GitHub...
python "%~dp0subir_github.py" "%GITHUB_TOK%"
if errorlevel 1 (
    echo.
    echo  ERRO ao enviar arquivos. Verifique sua conexão e o token.
    pause
    exit /b 1
)

echo.
echo ══════════════════════════════════════════════════════
echo   Configuração concluída com sucesso!
echo.
echo   Próximo passo: ativar o GitHub Pages
echo   Acesse: https://github.com/gnscozziero-lang/acompprocesso/settings/pages
echo   Selecione Branch: main  /  Pasta: / (root)
echo   Clique em Save
echo ══════════════════════════════════════════════════════
echo.
pause
