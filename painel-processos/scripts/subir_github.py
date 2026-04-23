#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script auxiliar: envia os arquivos do painel para o GitHub.
Chamado automaticamente pelo configurar.bat
"""
import sys, os, json, base64, requests

REPO = "gnscozziero-lang/acompprocesso"
BRANCH = "main"

# Arquivos a enviar: (caminho local relativo ao script, caminho no repo)
ARQUIVOS = [
    ("../index.html",             "painel-processos/index.html"),
    ("../dados/processos.json",   "painel-processos/dados/processos.json"),
    ("analisar_processos.py",     "painel-processos/scripts/analisar_processos.py"),
    ("configurar.bat",            "painel-processos/scripts/configurar.bat"),
    ("subir_github.py",           "painel-processos/scripts/subir_github.py"),
    ("../SETUP.md",               "painel-processos/SETUP.md"),
]

def enviar_arquivo(token, caminho_local, caminho_repo):
    if not os.path.exists(caminho_local):
        print(f"   AVISO: arquivo não encontrado localmente: {caminho_local}")
        return False

    with open(caminho_local, "rb") as f:
        conteudo = f.read()
    conteudo_b64 = base64.b64encode(conteudo).decode("utf-8")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{REPO}/contents/{caminho_repo}"

    # Verificar se o arquivo já existe (para obter o SHA)
    resp_get = requests.get(url, headers=headers)
    sha = resp_get.json().get("sha") if resp_get.status_code == 200 else None

    payload = {
        "message": f"Configuração inicial — {caminho_repo}",
        "content": conteudo_b64,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha

    resp = requests.put(url, headers=headers, json=payload)
    if resp.status_code in (200, 201):
        return True
    else:
        print(f"   ERRO ao enviar {caminho_repo}: {resp.status_code} — {resp.text[:200]}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Token não fornecido.")
        sys.exit(1)

    token = sys.argv[1]
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"   Repositório: {REPO}")
    print(f"   Enviando {len(ARQUIVOS)} arquivo(s)...\n")

    sucesso = 0
    for caminho_rel, caminho_repo in ARQUIVOS:
        caminho_local = os.path.join(base_dir, caminho_rel)
        nome = os.path.basename(caminho_repo)
        ok = enviar_arquivo(token, caminho_local, caminho_repo)
        if ok:
            print(f"   [OK] {nome}")
            sucesso += 1
        else:
            print(f"   [ERRO] {nome}")

    print(f"\n   {sucesso}/{len(ARQUIVOS)} arquivos enviados com sucesso.")
    if sucesso < len(ARQUIVOS):
        sys.exit(1)

if __name__ == "__main__":
    main()
