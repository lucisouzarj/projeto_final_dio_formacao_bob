# 🤖 DIO Explorer — Projeto Final · Formação Bob (IBM)

> **Projeto de conclusão da Formação Bob da DIO (Digital Innovation One)**  
> Construído integralmente com o assistente de IA **Bob (IBM)** — da concepção à implementação.

---

## 📖 Índice

1. [Sobre o Projeto](#-sobre-o-projeto)
2. [Arquitetura](#-arquitetura)
3. [Pré-requisitos](#-pré-requisitos)
4. [Instalação e Execução](#-instalação-e-execução)
5. [Ferramentas Disponíveis](#-ferramentas-disponíveis)
6. [Comandos Slash do Bob](#-comandos-slash-do-bob)
7. [Dados do Projeto](#-dados-do-projeto)
8. [Prompts Utilizados](#-prompts-utilizados-durante-o-desenvolvimento)
9. [Modos de Uso do Bob](#-modos-de-uso-do-bob)
10. [Dicas de Uso](#-dicas-de-uso)
11. [Insights para Futuros Profissionais](#-insights-para-futuros-profissionais)
12. [Estrutura de Arquivos](#-estrutura-de-arquivos)
13. [Tecnologias](#-tecnologias)

---

## 🎯 Sobre o Projeto

O **DIO Explorer** é um servidor MCP (_Model Context Protocol_) que expõe três ferramentas de aprendizado ao Bob (e a qualquer cliente MCP compatível):

| Ferramenta | O que faz |
|---|---|
| `trilha` | Retorna o plano de estudos completo de uma tecnologia |
| `desafio` | Gera um desafio de código personalizado por nível |
| `certificado` | Emite um certificado fictício de conclusão de trilha |
| `listar_trilhas` | Lista todas as trilhas disponíveis com nível e resumo |

O projeto demonstra, de ponta a ponta, como usar o Bob para:

- **Planejar** a arquitetura de um servidor MCP
- **Criar** código TypeScript com type-safety completa
- **Configurar** a integração via `.bob/mcp.json`
- **Criar** slash commands personalizados em `.bob/commands/`
- **Iterar** rapidamente com prompts de refinamento

---

## 🏗️ Arquitetura

```
projeto_final_dio_formacao_bob/
│
├── .bob/                          ← Configurações do Bob
│   ├── mcp.json                   ← Registro do servidor MCP
│   └── commands/                  ← Slash commands personalizados
│       ├── trilha.md              ← /trilha <tecnologia>
│       ├── desafio.md             ← /desafio <tecnologia> <nivel>
│       └── certificado.md         ← /certificado <nome> <trilha>
│
├── mcp/                           ← Servidor MCP (TypeScript)
│   ├── src/
│   │   └── index.ts               ← Código-fonte principal
│   ├── build/
│   │   └── index.js               ← Build compilado (executado pelo Bob)
│   ├── package.json
│   └── tsconfig.json
│
├── data/
│   └── trilhas.json               ← Base de dados de trilhas de estudo
│
├── dio_explorer/
│   └── data/
│       └── trilhas_dio.json       ← Dados enriquecidos das trilhas DIO
│
├── .bobignore                     ← Arquivos ignorados pelo Bob
└── README.md                      ← Este arquivo
```

### Fluxo de comunicação

```
Bob (Cliente MCP)
      │
      │  stdio (stdin/stdout)
      ▼
 mcp/build/index.js  (McpServer via @modelcontextprotocol/sdk)
      │
      ├── tool: trilha        → lê data/trilhas.json
      ├── tool: desafio       → usa dados internos por nível
      ├── tool: certificado   → gera certificado formatado
      └── tool: listar_trilhas → lê data/trilhas.json
```

---

## 🔧 Pré-requisitos

| Requisito | Versão mínima |
|---|---|
| Node.js | 18+ |
| npm | 9+ |
| Bob (IBM) | qualquer versão com suporte a MCP |

---

## 🚀 Instalação e Execução

### 1. Clone o repositório

```bash
git clone https://github.com/<seu-usuario>/projeto_final_dio_formacao_bob.git
cd projeto_final_dio_formacao_bob
```

### 2. Instale as dependências do servidor MCP

```bash
cd mcp
npm install
```

### 3. Compile o TypeScript

```bash
npm run build
```

O arquivo `mcp/build/index.js` será gerado.

### 4. Configure o Bob

O arquivo `.bob/mcp.json` já está configurado:

```json
{
  "mcpServers": {
    "dio-explorer": {
      "command": "node",
      "args": [
        "<caminho-absoluto>/mcp/build/index.js"
      ]
    }
  }
}
```

> ⚠️ **Atenção:** atualize o caminho absoluto para refletir sua máquina se necessário.

### 5. Abra o projeto no Bob

Abra a pasta raiz do projeto no Bob. O servidor MCP será detectado e iniciado automaticamente.

---

## 🛠️ Ferramentas Disponíveis

### `trilha`

Retorna o plano de estudos completo de uma tecnologia.

**Parâmetros:**
- `tecnologia` (string): nome da tecnologia. Ex: `Python`, `Java`, `React`

**Exemplo de uso via MCP:**
```json
{ "tecnologia": "Python" }
```

**Tecnologias disponíveis:** Python, JavaScript, TypeScript, React, Java

---

### `desafio`

Gera um desafio de código com título, descrição, requisitos, dicas e critérios de avaliação.

**Parâmetros:**
- `tecnologia` (string): linguagem do desafio
- `nivel` (enum): `iniciante` | `intermediario` | `avancado` (padrão: `iniciante`)

**Exemplo:**
```json
{ "tecnologia": "JavaScript", "nivel": "intermediario" }
```

**Critérios de avaliação padrão:**
| Critério | Peso |
|---|---|
| Correção | 40% |
| Legibilidade | 30% |
| Boas práticas | 20% |
| Criatividade | 10% |

---

### `certificado`

Emite um certificado fictício formatado em Markdown com código único, carga horária e competências.

**Parâmetros:**
- `nome` (string): nome completo do aluno
- `trilha` (string): nome da trilha concluída

**Exemplo:**
```json
{ "nome": "Helton Cavalcanti", "trilha": "Java" }
```

---

### `listar_trilhas`

Lista todas as trilhas disponíveis com nível e número de módulos. Não requer parâmetros.

---

## 💬 Comandos Slash do Bob

Os slash commands são atalhos que o Bob reconhece diretamente no chat. Estão em `.bob/commands/`.

### `/trilha <tecnologia>`

```
/trilha Python
/trilha JavaScript
/trilha React
```

O Bob lê `data/trilhas.json` e exibe o plano formatado com todos os módulos.

---

### `/desafio <tecnologia> <nivel>`

```
/desafio Python iniciante
/desafio Java avancado
/desafio TypeScript intermediario
```

Gera um desafio aleatório para a tecnologia e nível escolhidos.  
Se o nível não for reconhecido, usa `iniciante` como padrão.

---

### `/certificado <nome> <trilha>`

```
/certificado "Helton Cavalcanti" Java
/certificado "Maria Silva" React
```

Emite um certificado fictício com data atual, código único `DIO-YYYY-XXXXXX` e competências.

---

## 📦 Dados do Projeto

### `data/trilhas.json`

Base principal de trilhas de estudo. Cada entrada segue o schema:

```json
{
  "NomeTrilha": {
    "descricao": "string",
    "nivel": "string",
    "modulos": [
      {
        "numero": 1,
        "titulo": "string",
        "topicos": ["string"]
      }
    ]
  }
}
```

**Trilhas disponíveis:**

| Trilha | Nível | Módulos |
|---|---|---|
| Python | iniciante ao avançado | 7 |
| JavaScript | iniciante ao avançado | 7 |
| TypeScript | intermediário ao avançado | 5 |
| React | intermediário | 6 |
| Java | iniciante ao avançado | 6 |

### `dio_explorer/data/trilhas_dio.json`

Dataset enriquecido com metadados das trilhas DIO: XP total, badges, promoções, vitalício e lives ao vivo agendadas. Contém dados de 10 trilhas com schema detalhado.

---

## 📝 Prompts Utilizados Durante o Desenvolvimento

Esta seção documenta os prompts reais utilizados para construir cada parte do projeto com o Bob.

---

### Fase 1 — Entendendo o Bob e o MCP

**Prompt:** Exploração inicial das capacidades
```
O que é um servidor MCP e como o Bob se integra com ele?
```
> 💡 **Insight:** O Bob explicou o Model Context Protocol, a diferença entre transport stdio e HTTP/SSE, e como o `mcp.json` registra servidores. Perguntas abertas de conceito são ótimas para começar.

---

### Fase 2 — Scaffolding do Projeto

**Prompt:** Criação da estrutura inicial
```
Crie a estrutura de pastas para um servidor MCP em TypeScript que vai expor 
três ferramentas: trilha, desafio e certificado para a plataforma DIO.
Inclua package.json, tsconfig.json e a estrutura de diretórios.
```
> 💡 **Insight:** Quanto mais contexto você fornecer (tecnologia, nomes das ferramentas, objetivo), mais preciso o resultado. Evite prompts vagos como "crie um projeto".

---

### Fase 3 — Implementação das Ferramentas MCP

**Prompt:** Ferramenta `trilha`
```
Implemente a ferramenta trilha no servidor MCP. Ela deve:
- Receber o parâmetro "tecnologia" (string)
- Ler o arquivo data/trilhas.json na raiz do projeto
- Fazer busca case-insensitive
- Retornar o plano de estudos formatado em Markdown
- Se não encontrar, listar as disponíveis
```

**Prompt:** Ferramenta `desafio`
```
Adicione a ferramenta desafio. Parâmetros: tecnologia (string) e nivel 
(enum: iniciante | intermediario | avancado). Gere desafios com título, 
descrição, requisitos, dicas, critérios de avaliação e tempo sugerido.
```

**Prompt:** Ferramenta `certificado`
```
Implemente a ferramenta certificado com parâmetros nome e trilha.
Gere um certificado em Markdown com: código único DIO-ANO-XXXXXX, 
data em português, carga horária por trilha e competências adquiridas.
```
> 💡 **Insight:** Dividir cada ferramenta em um prompt separado é muito mais eficaz do que tentar fazer tudo de uma vez. O Bob mantém contexto entre mensagens.

---

### Fase 4 — Dados

**Prompt:** Base de trilhas
```
Crie o arquivo data/trilhas.json com trilhas de estudo para Python, 
JavaScript, TypeScript, React e Java. Cada trilha deve ter descrição, 
nível e módulos com tópicos.
```

**Prompt:** Dataset enriquecido
```
Crie dio_explorer/data/trilhas_dio.json com dados de 10 trilhas da DIO 
incluindo: id, nome, tecnologia, nivel, modulos, xp_total, badges, 
promoções, acesso vitalício e lives agendadas.
```

---

### Fase 5 — Slash Commands

**Prompt:** Criando os comandos
```
Crie os slash commands do Bob em .bob/commands/ para as três ferramentas:
- trilha.md: recebe <tecnologia>, lê data/trilhas.json, exibe formatado
- desafio.md: recebe <tecnologia> <nivel>, gera desafio aleatório
- certificado.md: recebe <nome> <trilha>, gera certificado Markdown
```
> 💡 **Insight:** Os slash commands são arquivos Markdown com frontmatter YAML. Eles funcionam como templates de prompt — o Bob os executa diretamente no chat sem precisar do servidor MCP.

---

### Fase 6 — Configuração do Bob

**Prompt:** Registro do MCP
```
Configure o arquivo .bob/mcp.json para registrar o servidor dio-explorer 
usando transport stdio apontando para mcp/build/index.js
```

**Prompt:** `.bobignore`
```
Crie um .bobignore excluindo node_modules, arquivos .env, cache de 
progresso e certificados emitidos.
```

---

### Fase 7 — Refinamentos

**Prompt:** Adicionando `listar_trilhas`
```
Adicione uma quarta ferramenta listar_trilhas ao servidor MCP que não 
recebe parâmetros e lista todas as trilhas disponíveis com nome, nível 
e número de módulos.
```

**Prompt:** Documentação
```
Documente todo o projeto feito até o momento, com todos os prompts 
usados, modos de uso, dicas de uso e insights para futuros profissionais 
que vão aprender com nosso projeto.
```

---

## 🖥️ Modos de Uso do Bob

O Bob possui diferentes modos otimizados para cada tipo de tarefa:

### Modo Agent (padrão)
**Quando usar:** para escrever, modificar e refatorar código.

```
Exemplos de prompts no modo Agent:
- "Adicione validação de entrada na ferramenta desafio"
- "Refatore a função loadTrilhas para aceitar um caminho customizável"
- "Corrija o erro de tipagem na linha 45 do index.ts"
```

### Modo Plan
**Quando usar:** para planejar arquitetura antes de implementar.

```
Exemplos de prompts no modo Plan:
- "Como devo estruturar o servidor MCP para suportar múltiplos idiomas?"
- "Desenhe a arquitetura para adicionar um banco de dados ao projeto"
- "Quais são os riscos de usar stdio em produção?"
```

### Modo Ask
**Quando usar:** para perguntas sobre o próprio Bob, conceitos técnicos, documentação.

```
Exemplos de prompts no modo Ask:
- "Como funcionam os slash commands do Bob?"
- "Qual é a diferença entre transport stdio e HTTP/SSE no MCP?"
- "O que é o arquivo .bobignore?"
```

---

## 💡 Dicas de Uso

### 1. Seja específico nos prompts

❌ **Vago:**
```
Melhore o código
```

✅ **Específico:**
```
Melhore o tratamento de erros na ferramenta trilha para que, quando o 
arquivo JSON não for encontrado, retorne uma mensagem amigável ao invés 
de lançar uma exceção.
```

---

### 2. Divida tarefas complexas

Ao invés de um único prompt enorme, quebre em etapas:

1. Primeiro: estrutura de pastas e arquivos vazios
2. Depois: implementação de cada ferramenta separadamente
3. Por fim: integração e testes

---

### 3. Use o contexto do Bob

O Bob lembra toda a conversa. Você pode referenciar decisões anteriores:

```
"Com base na arquitetura que definimos antes, adicione agora a ferramenta 
listar_trilhas seguindo o mesmo padrão das outras ferramentas."
```

---

### 4. Peça revisão antes de aplicar

```
"Antes de aplicar, me mostre o diff do que você vai mudar no index.ts"
```

---

### 5. Use o modo Plan para decisões importantes

Antes de implementar uma feature nova, use o modo Plan para avaliar trade-offs:

```
"No modo Plan: quais são as vantagens e desvantagens de mover os dados 
das trilhas para um banco Appwrite ao invés de um arquivo JSON local?"
```

---

### 6. Aproveite as ferramentas MCP do Appwrite

O Bob tem acesso nativo ao Appwrite MCP. Para persistir dados:

```
"Crie um banco de dados no Appwrite chamado 'dio-explorer' com uma 
coleção 'trilhas' com os atributos: nome (string), nivel (string), 
descricao (string)"
```

---

### 7. Valide sempre após mudanças

```
"Compile o TypeScript e me mostre se há erros"
"Execute os testes e me mostra o resultado"
```

---

## 🚀 Insights para Futuros Profissionais

### 🧠 1. O Bob é um parceiro, não um gerador automático

O maior erro é tratar o Bob como um "gerador de código mágico". Os melhores resultados vêm de uma **colaboração ativa**: você traz o domínio do problema, o Bob traz a capacidade técnica. Quanto melhor você entender o que quer, melhor o Bob entrega.

---

### 📐 2. Arquitetura primeiro, código depois

Antes de pedir para o Bob escrever código, use o **modo Plan** para discutir a arquitetura. Um bom plano economiza horas de refatoração. Pergunte sobre trade-offs, alternativas e riscos antes de implementar.

---

### 🔄 3. Iteração é o método

Nenhum projeto começa perfeito. O fluxo natural com o Bob é:

```
Prompt inicial → Revisão → Refinamento → Prompt de ajuste → ...
```

Não tente acertar em um único prompt. Itere.

---

### 📁 4. Organize o contexto para o Bob

O Bob lê os arquivos do seu projeto. Mantenha o código organizado, com nomes de arquivos descritivos e comentários claros — isso melhora a qualidade das respostas do Bob sobre o seu próprio código.

---

### 🛡️ 5. Entenda o que o Bob gera

Nunca aplique código sem entender o que ele faz. Use o Bob para aprender:

```
"Explique o que esta função faz linha por linha"
"Por que você usou StdioServerTransport ao invés de HTTP?"
"Quais são os possíveis problemas com esta implementação?"
```

---

### 🔌 6. O padrão MCP é o futuro das ferramentas de IA

O Model Context Protocol (MCP) é uma forma padronizada de expor ferramentas para agentes de IA. Ao aprender a construir servidores MCP, você aprende a criar ferramentas que funcionam com qualquer cliente compatível — não apenas o Bob.

---

### 📄 7. Slash commands são prompts reutilizáveis

Os arquivos em `.bob/commands/` são essencialmente "prompts salvos". Esse padrão é poderoso para qualquer equipe: crie comandos para tarefas repetitivas, revisões de código, geração de documentação, etc.

---

### 🗂️ 8. Dados bem estruturados viabilizam features

O arquivo `data/trilhas.json` é a base de todo o DIO Explorer. Um schema limpo e bem pensado permitiu implementar as três ferramentas de forma simples. **Dados bem modelados > código complicado.**

---

### ⚡ 9. TypeScript + Zod = APIs robustas

A combinação de TypeScript para tipagem estática e Zod para validação de schema em runtime é um padrão moderno e poderoso. O MCP SDK do Anthropic usa Zod nativamente — aprenda esse combo.

---

### 🌐 10. Pense no crescimento do projeto

Este projeto usa `stdio` como transport. Para uma versão de produção, o próximo passo seria migrar para `StreamableHTTPServerTransport` e hospedar o servidor MCP em um serviço de nuvem. Planeje sempre o caminho de evolução.

---

## 📂 Estrutura de Arquivos

```
projeto_final_dio_formacao_bob/
│
├── .bob/
│   ├── mcp.json                    # Registro do servidor MCP no Bob
│   └── commands/
│       ├── trilha.md               # /trilha <tecnologia>
│       ├── desafio.md              # /desafio <tecnologia> <nivel>
│       └── certificado.md          # /certificado <nome> <trilha>
│
├── mcp/
│   ├── src/
│   │   └── index.ts                # Servidor MCP — código-fonte
│   ├── build/
│   │   └── index.js                # Servidor MCP — build compilado
│   ├── package.json                # dio-explorer-mcp v0.1.0
│   └── tsconfig.json               # ES2022 / Node16
│
├── data/
│   └── trilhas.json                # Base de dados: Python, JS, TS, React, Java
│
├── dio_explorer/
│   ├── commands/
│   ├── data/
│   │   └── trilhas_dio.json        # Dataset enriquecido (10 trilhas, XP, badges)
│   ├── docs/
│   ├── mcp/
│   └── src/
│
├── .bobignore                      # node_modules, .env, cache, certificados
└── README.md                       # Esta documentação
```

---

## 🧰 Tecnologias

| Tecnologia | Versão | Uso |
|---|---|---|
| TypeScript | 5.8+ | Linguagem do servidor MCP |
| Node.js | 18+ | Runtime |
| `@modelcontextprotocol/sdk` | 1.13+ | Framework MCP |
| Zod | 3.25+ | Validação de schema de ferramentas |
| Bob (IBM) | — | Assistente de IA / cliente MCP |

---

## 👤 Autor

**Helton Cavalcanti**  
Projeto de conclusão da Formação Bob — DIO (Digital Innovation One)

---

*Powered by Bob — IBM* 🤖
