#!/usr/bin/env node
/**
 * DIO Explorer MCP Server
 *
 * Exposes the three core slash-command tools of the DIO Explorer project:
 *   - trilha        → returns the full study plan for a given technology
 *   - desafio       → generates a coding challenge for a technology + level
 *   - certificado   → generates a completion certificate for a student
 *
 * Transport: stdio (default, local)
 * To use over HTTP/SSE in the future, swap StdioServerTransport for
 * a StreamableHTTPServerTransport and add an Express/Fastify wrapper.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join, resolve } from "path";

// ---------------------------------------------------------------------------
// Paths
// ---------------------------------------------------------------------------

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// The data files live two levels up from mcp/build/
const PROJECT_ROOT = resolve(__dirname, "..", "..", "..");
const TRILHAS_PATH = join(PROJECT_ROOT, "data", "trilhas.json");
const TRILHAS_DIO_PATH = join(PROJECT_ROOT, "dio_explorer", "data", "trilhas_dio.json");

// ---------------------------------------------------------------------------
// Data helpers
// ---------------------------------------------------------------------------

interface Modulo {
  numero: number;
  titulo: string;
  topicos: string[];
}

interface Trilha {
  descricao: string;
  nivel: string;
  modulos: Modulo[];
}

interface TrilhasMap {
  [key: string]: Trilha;
}

function loadTrilhas(): TrilhasMap {
  try {
    const raw = readFileSync(TRILHAS_PATH, "utf-8");
    return JSON.parse(raw) as TrilhasMap;
  } catch {
    return {};
  }
}

function findTrilha(data: TrilhasMap, tecnologia: string): [string | null, Trilha | null] {
  for (const [key, value] of Object.entries(data)) {
    if (key.toLowerCase() === tecnologia.trim().toLowerCase()) {
      return [key, value];
    }
  }
  return [null, null];
}

function gerarCodigoCertificado(ano?: number): string {
  const year = ano ?? new Date().getFullYear();
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let sufixo = "";
  for (let i = 0; i < 6; i++) {
    sufixo += chars[Math.floor(Math.random() * chars.length)];
  }
  return `DIO-${year}-${sufixo}`;
}

function dataExtenso(d?: Date): string {
  const date = d ?? new Date();
  const meses = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
  ];
  return `${date.getDate()} de ${meses[date.getMonth()]} de ${date.getFullYear()}`;
}

// ---------------------------------------------------------------------------
// Desafio data
// ---------------------------------------------------------------------------

const DESAFIOS: Record<string, Array<[string, string]>> = {
  iniciante: [
    ["Calculadora de IMC", "Crie um programa que receba peso e altura e calcule o IMC do usuário, exibindo a classificação correspondente."],
    ["Conversor de Temperatura", "Implemente um conversor que transforme graus Celsius em Fahrenheit e Kelvin."],
    ["Contador de Palavras", "Escreva um programa que receba uma string e retorne a contagem de cada palavra única."],
  ],
  intermediario: [
    ["Sistema de Cadastro com Arquivo", "Implemente um CRUD de usuários salvando os dados em um arquivo JSON local."],
    ["API de Consulta de CEP", "Consuma a API ViaCEP e retorne os dados de endereço formatados para um CEP informado."],
    ["Algoritmo de Ordenação Próprio", "Implemente o algoritmo Merge Sort do zero sem usar funções nativas de ordenação."],
  ],
  avancado: [
    ["Pool de Threads para Download", "Crie um gerenciador de downloads concorrentes usando threads, com controle de taxa e retry automático."],
    ["Micro ORM Simples", "Implemente um mini ORM que mapeie classes Python/Java para tabelas SQL sem usar bibliotecas externas."],
    ["Sistema de Cache LRU", "Desenvolva uma estrutura de cache LRU com expiração por TTL e suporte a operações concorrentes."],
  ],
};

const TEMPOS: Record<string, string> = {
  iniciante: "30 minutos",
  intermediario: "1 hora",
  avancado: "2 horas",
};

const COMPETENCIAS: Record<string, string[]> = {
  Java: [
    "Programação orientada a objetos com Java",
    "Desenvolvimento de APIs REST com Spring Boot",
    "Persistência de dados com Spring Data JPA",
    "Segurança de aplicações com Spring Security",
    "Testes automatizados com JUnit 5 e Mockito",
    "Streams API e programação funcional",
    "Deploy de aplicações Java em nuvem",
  ],
};

const COMPETENCIAS_PADRAO = [
  "Lógica de programação aplicada",
  "Boas práticas de código limpo",
  "Controle de versão com Git",
  "Estruturas de dados fundamentais",
  "Testes unitários e integração",
];

const CARGA_HORARIA: Record<string, string> = {
  Java: "80h",
  Python: "60h",
  JavaScript: "70h",
  TypeScript: "50h",
  React: "60h",
};

// ---------------------------------------------------------------------------
// MCP Server
// ---------------------------------------------------------------------------

const server = new McpServer({
  name: "dio-explorer-mcp",
  version: "0.1.0",
});

// ---------------------------------------------------------------------------
// Tool: trilha
// ---------------------------------------------------------------------------

server.registerTool(
  "trilha",
  {
    description:
      "Retorna o plano de estudos completo (módulos e tópicos) de uma trilha de tecnologia disponível na DIO. " +
      "Se a tecnologia não for encontrada, lista as trilhas disponíveis.",
    inputSchema: z.object({
      tecnologia: z
        .string()
        .describe(
          "Nome da tecnologia (ex: Python, JavaScript, TypeScript, React, Java)"
        ),
    }),
  },
  async ({ tecnologia }) => {
    try {
      const data = loadTrilhas();
      const [chave, trilha] = findTrilha(data, tecnologia);

      if (!trilha || !chave) {
        const disponiveis = Object.keys(data).join(", ");
        return {
          content: [
            {
              type: "text",
              text:
                `❌ Trilha '${tecnologia}' não encontrada.\n` +
                `Trilhas disponíveis: ${disponiveis || "nenhuma carregada"}`,
            },
          ],
          isError: true,
        };
      }

      const linhas: string[] = [
        `# 🗺️ Trilha de ${chave}\n`,
        `> ${trilha.descricao}`,
        `> **Nível:** ${trilha.nivel}\n`,
        "## 📚 Módulos\n",
      ];

      for (const mod of trilha.modulos) {
        linhas.push(`### Módulo ${mod.numero} — ${mod.titulo}\n`);
        for (const topico of mod.topicos) {
          linhas.push(`• ${topico}`);
        }
        linhas.push("");
      }

      linhas.push("---");
      linhas.push(
        "🚀 Comece hoje! Cada módulo te aproxima de uma carreira sólida em tecnologia."
      );

      return { content: [{ type: "text", text: linhas.join("\n") }] };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Erro ao carregar trilhas: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Tool: desafio
// ---------------------------------------------------------------------------

server.registerTool(
  "desafio",
  {
    description:
      "Gera um desafio de código personalizado para uma tecnologia e nível de dificuldade. " +
      "Retorna título, descrição, requisitos, dicas, critérios de avaliação e tempo sugerido.",
    inputSchema: z.object({
      tecnologia: z
        .string()
        .describe("Nome da tecnologia (ex: Python, JavaScript, Java)"),
      nivel: z
        .enum(["iniciante", "intermediario", "avancado"])
        .default("iniciante")
        .describe("Nível de dificuldade do desafio"),
    }),
  },
  async ({ tecnologia, nivel }) => {
    try {
      const nivelNorm =
        ["iniciante", "intermediario", "avancado"].includes(nivel)
          ? nivel
          : "iniciante";

      const opcoes = DESAFIOS[nivelNorm];
      const [titulo, descricao] = opcoes[Math.floor(Math.random() * opcoes.length)];
      const tempo = TEMPOS[nivelNorm];

      const texto =
        `# ⚔️ Desafio de Código — ${tecnologia} (${nivelNorm})\n\n` +
        `## 📋 Descrição\n\n${descricao}\n\n` +
        `## 🎯 Requisitos\n\n` +
        `• Implemente a solução completa em ${tecnologia}\n` +
        `• Trate entradas inválidas com mensagens de erro claras\n` +
        `• Escreva pelo menos 2 testes unitários\n` +
        `• Documente as funções principais\n\n` +
        `## 💡 Dicas\n\n` +
        `• Quebre o problema em funções menores antes de implementar\n` +
        `• Revise os conceitos de ${nivelNorm} antes de começar\n\n` +
        `## 📊 Critérios de Avaliação\n\n` +
        `| Critério      | Peso |\n` +
        `|---------------|------|\n` +
        `| Correção      | 40%  |\n` +
        `| Legibilidade  | 30%  |\n` +
        `| Boas práticas | 20%  |\n` +
        `| Criatividade  | 10%  |\n\n` +
        `## ⏱️ Tempo sugerido\n\n${tempo}\n`;

      return { content: [{ type: "text", text: texto }] };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Erro ao gerar desafio: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Tool: certificado
// ---------------------------------------------------------------------------

server.registerTool(
  "certificado",
  {
    description:
      "Gera um certificado de conclusão fictício (para portfólio e aprendizado) para um aluno " +
      "que concluiu uma trilha de tecnologia na DIO.",
    inputSchema: z.object({
      nome: z.string().describe("Nome completo do aluno"),
      trilha: z
        .string()
        .describe("Nome da trilha concluída (ex: Python, Java, React)"),
    }),
  },
  async ({ nome, trilha }) => {
    try {
      const hoje = new Date();
      const codigo = gerarCodigoCertificado(hoje.getFullYear());
      const dataStr = dataExtenso(hoje);
      const carga = CARGA_HORARIA[trilha] ?? "60h";
      const competencias = COMPETENCIAS[trilha] ?? COMPETENCIAS_PADRAO;
      const compLista = competencias.map((c) => `• ${c}`).join("\n");

      const texto =
        `# 🏆 CERTIFICADO DE CONCLUSÃO\n\n` +
        "```\n" +
        "╔══════════════════════════════════════════════════════════════╗\n" +
        "║           DIO — Digital Innovation One                      ║\n" +
        "║                CERTIFICADO DE CONCLUSÃO                     ║\n" +
        "╚══════════════════════════════════════════════════════════════╝\n" +
        "```\n\n" +
        `## Certificamos que\n\n` +
        `# ${nome}\n\n` +
        `concluiu com êxito a trilha de formação:\n\n` +
        `## 🎓 ${trilha}\n\n` +
        `---\n\n` +
        `📅 **Data de emissão:** ${dataStr}\n\n` +
        `🆔 **Código do certificado:** \`${codigo}\`\n\n` +
        `⏱️ **Carga horária total:** ${carga}\n\n` +
        `---\n\n` +
        `### 📚 Competências adquiridas\n\n` +
        `${compLista}\n\n` +
        `---\n\n` +
        `### 🌟 Parabéns, ${nome}!\n\n` +
        `Você concluiu com dedicação a trilha de **${trilha}** e está pronto para enfrentar\n` +
        `os desafios do mercado de tecnologia. Continue estudando, construindo projetos e\n` +
        `compartilhando seu conhecimento com a comunidade!\n\n` +
        `---\n\n` +
        `*Este é um certificado fictício gerado para fins de aprendizado e portfólio pessoal.*\n\n` +
        `*Powered by Bob — IBM*\n\n` +
        `> 💡 Compartilhe no LinkedIn e adicione **${trilha}** às suas habilidades!\n`;

      return { content: [{ type: "text", text: texto }] };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Erro ao gerar certificado: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Tool: listar_trilhas
// ---------------------------------------------------------------------------

server.registerTool(
  "listar_trilhas",
  {
    description:
      "Lista todas as trilhas de tecnologia disponíveis no DIO Explorer com nome, nível e descrição resumida.",
    inputSchema: z.object({}),
  },
  async () => {
    try {
      const data = loadTrilhas();
      const keys = Object.keys(data);
      if (keys.length === 0) {
        return {
          content: [{ type: "text", text: "Nenhuma trilha encontrada no arquivo de dados." }],
          isError: true,
        };
      }

      const linhas = ["# 📋 Trilhas disponíveis no DIO Explorer\n"];
      for (const key of keys) {
        const t = data[key];
        linhas.push(`## ${key}`);
        linhas.push(`> ${t.descricao}`);
        linhas.push(`> **Nível:** ${t.nivel} | **Módulos:** ${t.modulos.length}`);
        linhas.push("");
      }

      return { content: [{ type: "text", text: linhas.join("\n") }] };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Erro ao listar trilhas: ${error instanceof Error ? error.message : String(error)}`,
          },
        ],
        isError: true,
      };
    }
  }
);

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("dio-explorer-mcp running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in MCP server:", error);
  process.exit(1);
});
