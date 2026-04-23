# Configuração do Painel de Processos — Scozziero Advocacia

Siga estes passos **uma única vez** para deixar o sistema funcionando.

---

## PASSO 1 — Criar token de acesso no GitHub

O sistema precisa de permissão para publicar o arquivo de dados no GitHub.

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token (classic)"**
3. Em **Note**, escreva: `Painel Processos Scozziero`
4. Em **Expiration**, selecione **"No expiration"**
5. Em **Select scopes**, marque apenas: ✅ `repo`
6. Clique em **"Generate token"**
7. **COPIE o token gerado** (começa com `ghp_...`) — ele só aparece uma vez!

---

## PASSO 2 — Criar conta e chave na Anthropic (Claude)

O script usa Claude para analisar os PDFs. Você precisa de uma chave de API.

1. Acesse: https://console.anthropic.com
2. Crie uma conta gratuita (ou faça login se já tiver)
3. Acesse **"API Keys"** no menu
4. Clique em **"Create Key"**
5. Dê o nome: `Painel Processos`
6. **COPIE a chave gerada** (começa com `sk-ant-...`)

> O uso da API tem custo por documento analisado. Para PDFs jurídicos típicos, o custo por análise é de aproximadamente R$ 0,05–0,20.

---

## PASSO 3 — Configurar as variáveis de ambiente no Windows

As chaves precisam ser salvas no sistema para o script encontrá-las.

1. Pressione `Win + R`, digite `sysdm.cpl` e pressione Enter
2. Vá na aba **"Avançado"** → **"Variáveis de Ambiente"**
3. Em **"Variáveis do usuário"**, clique em **"Novo"** duas vezes:

   | Nome da variável | Valor |
   |---|---|
   | `ANTHROPIC_API_KEY` | `sk-ant-...` (sua chave da Anthropic) |
   | `GITHUB_TOKEN` | `ghp_...` (seu token do GitHub) |

4. Clique em **OK** e feche a janela

---

## PASSO 4 — Instalar Python e as dependências

1. Baixe o Python em: https://www.python.org/downloads/
   - Na instalação, marque ✅ **"Add Python to PATH"**

2. Abra o **Prompt de Comando** (Win + R → `cmd`) e execute:
   ```
   pip install anthropic pymupdf requests
   ```

---

## PASSO 5 — Enviar os arquivos para o GitHub

Na pasta `painel-processos` que foi criada, você precisa fazer o upload para o repositório `gnscozziero-lang/acompprocesso`.

**Opção A — Via GitHub Desktop (mais fácil):**
1. Baixe o GitHub Desktop: https://desktop.github.com/
2. Clone o repositório `gnscozziero-lang/acompprocesso`
3. Copie a pasta `painel-processos` para dentro do repositório clonado
4. No GitHub Desktop, clique em **"Commit to main"** e depois **"Push origin"**

**Opção B — Via upload no site:**
1. Acesse https://github.com/gnscozziero-lang/acompprocesso
2. Crie a pasta `painel-processos` pelo botão **"Add file"**
3. Faça upload de cada arquivo da pasta

---

## PASSO 6 — Ativar o GitHub Pages

1. Acesse o repositório: https://github.com/gnscozziero-lang/acompprocesso
2. Clique em **Settings** → **Pages**
3. Em **Source**, selecione **"Deploy from a branch"**
4. Em **Branch**, selecione **main** e pasta **/root**
5. Clique em **Save**

Após alguns minutos, o painel estará disponível em:
**https://gnscozziero-lang.github.io/acompprocesso/painel-processos/**

---

## PASSO 7 — Executar a análise pela primeira vez

1. Coloque PDFs de processos na pasta:
   `C:\Users\Guilherme\OneDrive - Aépio\Documentos\Controle IA Processos\Acomp.Processual`

2. Abra o **Prompt de Comando** e execute:
   ```
   python "C:\Users\Guilherme\OneDrive - Aépio\Documentos\Controle IA Processos\Acomp.Processual\painel-processos\scripts\analisar_processos.py"
   ```

3. O script vai:
   - Ler todos os PDFs da pasta
   - Analisar cada um com Claude
   - Publicar os resultados no GitHub automaticamente

---

## PASSO 8 — Agendar execução diária automática

Para o painel atualizar sozinho todo dia:

1. Abra o **Agendador de Tarefas** (Win + R → `taskschd.msc`)
2. Clique em **"Criar Tarefa Básica..."**
3. Configure:
   - Nome: `Painel Processos Scozziero`
   - Disparador: **Diariamente** às **08:00**
   - Ação: **Iniciar um programa**
   - Programa: `python`
   - Argumentos: `"C:\Users\Guilherme\OneDrive - Aépio\Documentos\Controle IA Processos\Acomp.Processual\painel-processos\scripts\analisar_processos.py"`
4. Clique em **Concluir**

---

## USO NO DIA A DIA

- **Adicionar processo:** Coloque o PDF na pasta `Acomp.Processual` e aguarde a próxima execução automática (ou execute o script manualmente)
- **Atualizar processo:** Substitua o PDF pelo novo e o sistema detectará a mudança
- **Remover processo:** Delete o PDF da pasta. Na próxima execução, o sistema não incluirá o processo removido
- **Acessar o painel:** Abra o link no celular ou computador

---

## SUPORTE

Em caso de dúvidas, abra o Cowork e descreva o problema — o assistente pode ajudar a diagnosticar e corrigir.
