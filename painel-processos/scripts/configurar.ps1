# Scozziero Advocacia — Configuração do Painel de Processos
# Execute com: clique direito → "Executar com PowerShell"

$Host.UI.RawUI.WindowTitle = "Scozziero Advocacia — Configuração"
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  SCOZZIERO ADVOCACIA - Configuracao do Painel" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# ── Localizar Python ──────────────────────────────────
Write-Host "  Procurando Python instalado..." -ForegroundColor Yellow

$pythonCmd = $null
$candidatos = @(
    "python",
    "python3",
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "$env:LOCALAPPDATA\Microsoft\WindowsApps\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe"
)

foreach ($c in $candidatos) {
    try {
        $ver = & $c --version 2>&1
        if ($ver -match "Python") {
            $pythonCmd = $c
            Write-Host "  [OK] Python encontrado: $ver" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Host ""
    Write-Host "  ERRO: Python nao encontrado." -ForegroundColor Red
    Write-Host "  Baixe em: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  Na instalacao, marque 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "  Pressione Enter para fechar"
    exit 1
}

# ── Pedir as chaves ───────────────────────────────────
Write-Host ""
Write-Host "  Voce precisara das duas chaves que criou." -ForegroundColor Yellow
Write-Host ""

$anthropicKey = Read-Host "  Cole aqui sua chave da Anthropic (sk-ant-...)"
$githubToken  = Read-Host "  Cole aqui seu token do GitHub    (ghp_...)"

if (-not $anthropicKey -or -not $githubToken) {
    Write-Host "  ERRO: Chaves nao informadas." -ForegroundColor Red
    Read-Host "  Pressione Enter para fechar"
    exit 1
}

# ── Salvar variáveis de ambiente ──────────────────────
Write-Host ""
Write-Host "  Salvando variaveis de ambiente..." -ForegroundColor Yellow
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $anthropicKey, "User")
[System.Environment]::SetEnvironmentVariable("GITHUB_TOKEN", $githubToken, "User")
$env:ANTHROPIC_API_KEY = $anthropicKey
$env:GITHUB_TOKEN = $githubToken
Write-Host "  [OK] Variaveis salvas" -ForegroundColor Green

# ── Instalar dependências ─────────────────────────────
Write-Host ""
Write-Host "  Instalando bibliotecas Python (aguarde)..." -ForegroundColor Yellow
& $pythonCmd -m pip install --quiet --upgrade anthropic pymupdf requests 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    # Tentar com pip direto
    & $pythonCmd -m pip install anthropic pymupdf requests
}
Write-Host "  [OK] Bibliotecas instaladas" -ForegroundColor Green

# ── Subir arquivos pro GitHub ─────────────────────────
Write-Host ""
Write-Host "  Enviando arquivos para o GitHub..." -ForegroundColor Yellow

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$subirScript = Join-Path $scriptDir "subir_github.py"

& $pythonCmd $subirScript $githubToken

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  ERRO ao enviar arquivos." -ForegroundColor Red
    Write-Host "  Verifique sua conexao com a internet e o token do GitHub." -ForegroundColor Yellow
    Read-Host "  Pressione Enter para fechar"
    exit 1
}

# ── Conclusão ─────────────────────────────────────────
Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "  Configuracao concluida com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "  Proximo passo: ativar o GitHub Pages" -ForegroundColor Cyan
Write-Host "  Acesse o link abaixo e siga as instrucoes:" -ForegroundColor Cyan
Write-Host "  https://github.com/gnscozziero-lang/acompprocesso/settings/pages" -ForegroundColor White
Write-Host ""
Write-Host "  Selecione: Branch main / pasta root / clique Save" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Read-Host "  Pressione Enter para fechar"
