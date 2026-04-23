#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║       SCOZZIERO ADVOCACIA — Analisador de Processos          ║
║   Lê PDFs da pasta, analisa com Claude e publica no GitHub   ║
╚══════════════════════════════════════════════════════════════╝

COMO USAR:
  1. Configure as variáveis na seção CONFIGURAÇÃO abaixo
  2. Instale as dependências: pip install anthropic pymupdf requests
  3. Execute: python analisar_processos.py

PARA RODAR AUTOMATICAMENTE (diariamente):
  Windows — Agendador de Tarefas:
    Ação: python "C:\...\analisar_processos.py"
    Horário: todo dia às 8h
"""

import os
import json
import hashlib
import base64
import datetime
import requests
import sys

# ══════════════════════════════════════════════════════════
# CONFIGURAÇÃO — edite estas variáveis
# ══════════════════════════════════════════════════════════

# Pasta local com os PDFs dos processos
PASTA_PROCESSOS = r"C:\Users\Guilherme\OneDrive - Aépio\Documentos\Controle IA Processos\Acomp.Processual"

# Repositório no GitHub (usuário/repositório)
GITHUB_REPO = "gnscozziero-lang/acompprocesso"
GITHUB_BRANCH = "main"

# Caminho do arquivo JSON dentro do repositório
CAMINHO_JSON_REPO = "painel-processos/dados/processos.json"

# Arquivo local para armazenar hashes (detecta mudanças nos PDFs)
ARQUIVO_HASHES = os.path.join(os.path.dirname(__file__), "cache_hashes.json")

# Variáveis de ambiente (configure no sistema ou crie um arquivo .env)
# ANTHROPIC_API_KEY — chave da API Claude (https://console.anthropic.com)
# GITHUB_TOKEN — token de acesso ao GitHub (https://github.com/settings/tokens)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

# ══════════════════════════════════════════════════════════
# FIM DA CONFIGURAÇÃO
# ══════════════════════════════════════════════════════════

def verificar_dependencias():
    """Verifica se todas as bibliotecas necessárias estão instaladas."""
    faltando = []
    for pkg, nome in [("anthropic", "anthropic"), ("fitz", "pymupdf"), ("requests", "requests")]:
        try:
            __import__(pkg)
        except ImportError:
            faltando.append(nome)
    if faltando:
        print(f"\n❌ Bibliotecas não instaladas: {', '.join(faltando)}")
        print(f"   Execute: pip install {' '.join(faltando)}\n")
        sys.exit(1)

def verificar_configuracao():
    """Verifica se as variáveis de configuração estão preenchidas."""
    erros = []
    if not ANTHROPIC_API_KEY:
        erros.append("ANTHROPIC_API_KEY não configurada")
    if not GITHUB_TOKEN:
        erros.append("GITHUB_TOKEN não configurado")
    if not os.path.isdir(PASTA_PROCESSOS):
        erros.append(f"Pasta não encontrada: {PASTA_PROCESSOS}")
    if erros:
        print("\n❌ Configuração incompleta:")
        for e in erros:
            print(f"   • {e}")
        print("\n   Consulte o arquivo SETUP.md para instruções de configuração.\n")
        sys.exit(1)

def hash_arquivo(caminho):
    """Calcula o hash MD5 de um arquivo para detectar mudanças."""
    h = hashlib.md5()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            h.update(bloco)
    return h.hexdigest()

def carregar_hashes():
    """Carrega o cache de hashes de arquivos já analisados."""
    if os.path.exists(ARQUIVO_HASHES):
        with open(ARQUIVO_HASHES, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_hashes(hashes):
    """Salva o cache de hashes atualizado."""
    with open(ARQUIVO_HASHES, "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)

def extrair_texto_pdf(caminho):
    """Extrai o texto de um arquivo PDF usando PyMuPDF."""
    import fitz
    texto = []
    try:
        doc = fitz.open(caminho)
        for pagina in doc:
            texto.append(pagina.get_text())
        doc.close()
        conteudo = "\n".join(texto).strip()
        # Limitar a 15.000 caracteres para não sobrecarregar a API
        return conteudo[:15000] if len(conteudo) > 15000 else conteudo
    except Exception as e:
        return f"[Erro ao extrair texto: {e}]"

def analisar_processo_com_claude(nome_arquivo, texto_pdf):
    """
    Envia o texto do PDF para o Claude e recebe a análise estruturada.
    Retorna um dicionário com os dados extraídos.
    """
    import anthropic

    cliente = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""Você é um assistente jurídico especializado em direito processual brasileiro.
Analise o documento abaixo e extraia as informações processuais de forma estruturada.

DOCUMENTO: {nome_arquivo}
CONTEÚDO:
{texto_pdf}

Responda EXCLUSIVAMENTE em JSON válido, sem texto adicional, seguindo exatamente esta estrutura:
{{
  "numero_processo": "número completo no formato CNJ (0000000-00.0000.0.00.0000) ou null se não encontrado",
  "partes": {{
    "cliente": "nome completo do cliente do escritório (inferir pelo contexto)",
    "adverso": "nome da parte adversa",
    "polo": "ativo ou passivo (posição do cliente)"
  }},
  "tipo": "área do direito (Cível, Trabalhista, Consumerista, Previdenciário, Criminal, etc.)",
  "tribunal": "sigla do tribunal (TJSP, TRT, STJ, etc.)",
  "vara": "identificação da vara ou juízo",
  "status": "em_andamento | aguardando | encerrado | recurso | execucao",
  "fase_atual": "fase processual atual (ex: Conhecimento, Instrução, Sentença, Recurso, Execução)",
  "ultima_movimentacao": {{
    "data": "AAAA-MM-DD ou null",
    "descricao": "descrição objetiva da última movimentação relevante"
  }},
  "proximas_acoes": [
    {{
      "acao": "nome curto da ação necessária",
      "prazo": "AAAA-MM-DD ou null se sem prazo definido",
      "urgencia": "urgente (≤3 dias) | atencao (4-10 dias) | ok (>10 dias)",
      "descricao": "detalhamento da ação necessária e fundamentação"
    }}
  ],
  "observacoes": "resumo do contexto do processo em 2-3 frases objetivas"
}}

REGRAS IMPORTANTES:
- Datas SEMPRE no formato AAAA-MM-DD
- Se o prazo for calculado a partir de uma data de decisão, some os dias úteis
- Liste TODAS as ações necessárias, mesmo as sem prazo definido
- proximas_acoes deve conter no mínimo 1 item se o processo estiver ativo
- Se o processo estiver encerrado, proximas_acoes pode ser []
- Para prazos processuais: intimação → citar tipo de prazo (contestação=15 dias, recurso ordinário=15 dias, etc.)
- O campo "cliente" deve ser a parte que o escritório Scozziero Advocacia representa"""

    try:
        resposta = cliente.messages.create(
            model="claude-opus-4-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        texto_resposta = resposta.content[0].text.strip()
        # Remover possíveis marcadores de código markdown
        if texto_resposta.startswith("```"):
            linhas = texto_resposta.split("\n")
            texto_resposta = "\n".join(linhas[1:-1])
        return json.loads(texto_resposta)
    except json.JSONDecodeError as e:
        print(f"   ⚠ Erro ao decodificar JSON da resposta: {e}")
        return None
    except Exception as e:
        print(f"   ⚠ Erro na chamada à API Claude: {e}")
        return None

def buscar_json_atual_do_github():
    """Busca o arquivo processos.json atual do GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CAMINHO_JSON_REPO}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        dados = resp.json()
        conteudo = base64.b64decode(dados["content"]).decode("utf-8")
        return json.loads(conteudo), dados["sha"]
    elif resp.status_code == 404:
        return {"ultima_atualizacao": "", "processos": []}, None
    else:
        raise Exception(f"Erro ao acessar GitHub: {resp.status_code} — {resp.text}")

def publicar_json_no_github(dados_json, sha_atual=None):
    """Publica o arquivo processos.json atualizado no GitHub."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CAMINHO_JSON_REPO}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    conteudo_encoded = base64.b64encode(
        json.dumps(dados_json, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": f"Atualização automática do painel — {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
        "content": conteudo_encoded,
        "branch": GITHUB_BRANCH
    }
    if sha_atual:
        payload["sha"] = sha_atual

    resp = requests.put(url, headers=headers, json=payload)
    if resp.status_code in (200, 201):
        return True
    else:
        raise Exception(f"Erro ao publicar no GitHub: {resp.status_code} — {resp.text}")

def gerar_id_processo(nome_arquivo, numero_processo):
    """Gera um ID único para o processo."""
    base = (numero_processo or nome_arquivo).encode("utf-8")
    return hashlib.md5(base).hexdigest()[:12]

def main():
    print("\n" + "═" * 60)
    print("  SCOZZIERO ADVOCACIA — Analisador de Processos")
    print("═" * 60)
    print(f"  Data/Hora: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"  Pasta: {PASTA_PROCESSOS}\n")

    verificar_dependencias()
    verificar_configuracao()

    # Listar PDFs na pasta
    pdfs = [f for f in os.listdir(PASTA_PROCESSOS) if f.lower().endswith(".pdf")]
    if not pdfs:
        print("⚠  Nenhum arquivo PDF encontrado na pasta.")
        print("   Adicione os PDFs dos processos e execute novamente.\n")
        return

    print(f"  📁 {len(pdfs)} PDF(s) encontrado(s)\n")

    # Carregar hashes anteriores (para detectar mudanças)
    hashes_anteriores = carregar_hashes()
    hashes_novos = {}
    arquivos_modificados = []

    for pdf in pdfs:
        caminho = os.path.join(PASTA_PROCESSOS, pdf)
        h = hash_arquivo(caminho)
        hashes_novos[pdf] = h
        if hashes_anteriores.get(pdf) != h:
            arquivos_modificados.append(pdf)

    if not arquivos_modificados:
        print("  ✅ Nenhum arquivo novo ou modificado. Painel já está atualizado.\n")
        return

    print(f"  🔄 {len(arquivos_modificados)} arquivo(s) novo(s) ou modificado(s):\n")

    # Buscar dados atuais do GitHub
    print("  📡 Conectando ao GitHub...")
    try:
        dados_atuais, sha_atual = buscar_json_atual_do_github()
    except Exception as e:
        print(f"  ❌ Erro ao acessar GitHub: {e}\n")
        return

    # Criar índice dos processos existentes por ID
    indice_processos = {p["id"]: p for p in dados_atuais.get("processos", []) if "id" in p}

    # Analisar cada arquivo modificado
    for i, nome_pdf in enumerate(arquivos_modificados, 1):
        caminho = os.path.join(PASTA_PROCESSOS, nome_pdf)
        print(f"  [{i}/{len(arquivos_modificados)}] Analisando: {nome_pdf}")

        texto = extrair_texto_pdf(caminho)
        if not texto or len(texto) < 50:
            print(f"       ⚠ Texto insuficiente extraído. Pulando.")
            continue

        print(f"       📄 {len(texto)} caracteres extraídos. Enviando ao Claude...")
        analise = analisar_processo_com_claude(nome_pdf, texto)

        if not analise:
            print(f"       ❌ Falha na análise. Pulando.")
            continue

        # Construir registro completo
        id_processo = gerar_id_processo(nome_pdf, analise.get("numero_processo"))
        registro = {
            "id": id_processo,
            "arquivo_origem": nome_pdf,
            "ultima_analise": datetime.datetime.now().isoformat(),
            **analise
        }

        # Atualizar ou inserir no índice
        indice_processos[id_processo] = registro
        print(f"       ✅ Análise concluída: {analise.get('numero_processo', 'nº não identificado')}")

    # Montar JSON final
    dados_finais = {
        "ultima_atualizacao": datetime.datetime.now().isoformat(),
        "total_arquivos_analisados": len(hashes_novos),
        "processos": list(indice_processos.values())
    }

    # Publicar no GitHub
    print(f"\n  📤 Publicando {len(dados_finais['processos'])} processo(s) no GitHub...")
    try:
        publicar_json_no_github(dados_finais, sha_atual)
        salvar_hashes(hashes_novos)
        print(f"\n  ✅ Painel atualizado com sucesso!")
        print(f"     Acesse: https://{GITHUB_REPO.split('/')[0]}.github.io/{GITHUB_REPO.split('/')[1]}/painel-processos/")
    except Exception as e:
        print(f"\n  ❌ Erro ao publicar: {e}")

    print("\n" + "═" * 60 + "\n")

if __name__ == "__main__":
    main()
