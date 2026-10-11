"""
commands_engine.py
Lógica central dos slash commands /trilha, /desafio e /certificado.
Toda função aqui é pura e testável de forma unitária.
"""

import json
import os
import re
import random
import string
from datetime import date

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

_ROOT = os.path.join(os.path.dirname(__file__), "..")
TRILHAS_PATH = os.path.join(_ROOT, "data", "trilhas.json")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_trilhas(path: str = TRILHAS_PATH) -> dict:
    """Carrega e retorna o JSON de trilhas. Levanta FileNotFoundError se ausente."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _find_trilha(data: dict, tecnologia: str) -> tuple[str | None, dict | None]:
    """
    Busca case-insensitive por uma tecnologia no dicionário de trilhas.
    Retorna (chave_original, dados) ou (None, None) se não encontrar.
    """
    for key, value in data.items():
        if key.lower() == tecnologia.strip().lower():
            return key, value
    return None, None


def _gerar_codigo_certificado(ano: int | None = None) -> str:
    """Gera código no formato DIO-{ANO}-{6 chars alfanuméricos em maiúsculo}."""
    if ano is None:
        ano = date.today().year
    chars = string.ascii_uppercase + string.digits
    sufixo = "".join(random.choices(chars, k=6))
    return f"DIO-{ano}-{sufixo}"


def _data_extenso(d: date | None = None) -> str:
    """Retorna data no formato por extenso em português: '15 de janeiro de 2025'."""
    if d is None:
        d = date.today()
    meses = [
        "", "janeiro", "fevereiro", "março", "abril", "maio", "junho",
        "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
    ]
    return f"{d.day} de {meses[d.month]} de {d.year}"


# ---------------------------------------------------------------------------
# /trilha
# ---------------------------------------------------------------------------

def cmd_trilha(tecnologia: str, trilhas_path: str = TRILHAS_PATH) -> str:
    """
    Retorna o plano de estudos formatado para a tecnologia informada.
    Se não encontrada, retorna lista de trilhas disponíveis.
    """
    data = _load_trilhas(trilhas_path)
    chave, trilha = _find_trilha(data, tecnologia)

    if trilha is None:
        disponiveis = ", ".join(data.keys())
        return (
            f"❌ Trilha '{tecnologia}' não encontrada.\n"
            f"Trilhas disponíveis: {disponiveis}"
        )

    linhas = [
        f"# 🗺️ Trilha de {chave}\n",
        f"> {trilha['descricao']}",
        f"> **Nível:** {trilha['nivel']}\n",
        "## 📚 Módulos\n",
    ]
    for mod in trilha["modulos"]:
        linhas.append(f"### Módulo {mod['numero']} — {mod['titulo']}\n")
        for topico in mod["topicos"]:
            linhas.append(f"• {topico}")
        linhas.append("")

    linhas.append("---")
    linhas.append("🚀 Comece hoje! Cada módulo te aproxima de uma carreira sólida em tecnologia.")
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# /desafio
# ---------------------------------------------------------------------------

NIVEIS_VALIDOS = {"iniciante", "intermediario", "avancado"}

DESAFIOS = {
    "iniciante": [
        ("Calculadora de IMC", "Crie um programa que receba peso e altura e calcule o IMC do usuário, exibindo a classificação correspondente."),
        ("Conversor de Temperatura", "Implemente um conversor que transforme graus Celsius em Fahrenheit e Kelvin."),
        ("Contador de Palavras", "Escreva um programa que receba uma string e retorne a contagem de cada palavra única."),
    ],
    "intermediario": [
        ("Sistema de Cadastro com Arquivo", "Implemente um CRUD de usuários salvando os dados em um arquivo JSON local."),
        ("API de Consulta de CEP", "Consuma a API ViaCEP e retorne os dados de endereço formatados para um CEP informado."),
        ("Algoritmo de Ordenação Próprio", "Implemente o algoritmo Merge Sort do zero sem usar funções nativas de ordenação."),
    ],
    "avancado": [
        ("Pool de Threads para Download", "Crie um gerenciador de downloads concorrentes usando threads, com controle de taxa e retry automático."),
        ("Micro ORM Simples", "Implemente um mini ORM que mapeie classes Python/Java para tabelas SQL sem usar bibliotecas externas."),
        ("Sistema de Cache LRU", "Desenvolva uma estrutura de cache LRU com expiração por TTL e suporte a operações concorrentes."),
    ],
}

TEMPOS = {"iniciante": "30 minutos", "intermediario": "1 hora", "avancado": "2 horas"}


def cmd_desafio(tecnologia: str, nivel: str, seed: int | None = None) -> str:
    """
    Gera um desafio de código para a tecnologia e nível informados.
    `seed` permite resultado determinístico em testes.
    """
    nivel_norm = nivel.strip().lower()
    if nivel_norm not in NIVEIS_VALIDOS:
        nivel_norm = "iniciante"

    rng = random.Random(seed)
    titulo, descricao = rng.choice(DESAFIOS[nivel_norm])
    tempo = TEMPOS[nivel_norm]

    return (
        f"# ⚔️ Desafio de Código — {tecnologia} ({nivel_norm})\n\n"
        f"## 📋 Descrição\n\n{descricao}\n\n"
        f"## 🎯 Requisitos\n\n"
        f"• Implemente a solução completa em {tecnologia}\n"
        f"• Trate entradas inválidas com mensagens de erro claras\n"
        f"• Escreva pelo menos 2 testes unitários\n"
        f"• Documente as funções principais\n\n"
        f"## 💡 Dicas\n\n"
        f"• Quebre o problema em funções menores antes de implementar\n"
        f"• Revise os conceitos de {nivel_norm} antes de começar\n\n"
        f"## 📊 Critérios de Avaliação\n\n"
        f"| Critério      | Peso |\n"
        f"|---------------|------|\n"
        f"| Correção      | 40%  |\n"
        f"| Legibilidade  | 30%  |\n"
        f"| Boas práticas | 20%  |\n"
        f"| Criatividade  | 10%  |\n\n"
        f"## ⏱️ Tempo sugerido\n\n{tempo}\n"
    )


# ---------------------------------------------------------------------------
# /certificado
# ---------------------------------------------------------------------------

COMPETENCIAS = {
    "Java": [
        "Programação orientada a objetos com Java",
        "Desenvolvimento de APIs REST com Spring Boot",
        "Persistência de dados com Spring Data JPA",
        "Segurança de aplicações com Spring Security",
        "Testes automatizados com JUnit 5 e Mockito",
        "Streams API e programação funcional",
        "Deploy de aplicações Java em nuvem",
    ]
}
COMPETENCIAS_PADRAO = [
    "Lógica de programação aplicada",
    "Boas práticas de código limpo",
    "Controle de versão com Git",
    "Estruturas de dados fundamentais",
    "Testes unitários e integração",
]

CARGA_HORARIA = {"Java": "80h", "Python": "60h", "JavaScript": "70h", "TypeScript": "50h", "React": "60h"}


def cmd_certificado(nome: str, trilha: str, data_emissao: date | None = None, codigo: str | None = None) -> str:
    """Gera o certificado fictício em Markdown para o aluno e a trilha informados."""
    if data_emissao is None:
        data_emissao = date.today()
    if codigo is None:
        codigo = _gerar_codigo_certificado(data_emissao.year)

    data_str = _data_extenso(data_emissao)
    carga = CARGA_HORARIA.get(trilha, "60h")
    competencias = COMPETENCIAS.get(trilha, COMPETENCIAS_PADRAO)

    comp_lista = "\n".join(f"• {c}" for c in competencias)

    return (
        f"# 🏆 CERTIFICADO DE CONCLUSÃO\n\n"
        f"```\n"
        f"╔══════════════════════════════════════════════════════════════╗\n"
        f"║           DIO — Digital Innovation One                      ║\n"
        f"║                CERTIFICADO DE CONCLUSÃO                     ║\n"
        f"╚══════════════════════════════════════════════════════════════╝\n"
        f"```\n\n"
        f"## Certificamos que\n\n"
        f"# {nome}\n\n"
        f"concluiu com êxito a trilha de formação:\n\n"
        f"## 🎓 {trilha}\n\n"
        f"---\n\n"
        f"📅 **Data de emissão:** {data_str}\n\n"
        f"🆔 **Código do certificado:** `{codigo}`\n\n"
        f"⏱️ **Carga horária total:** {carga}\n\n"
        f"---\n\n"
        f"### 📚 Competências adquiridas\n\n"
        f"{comp_lista}\n\n"
        f"---\n\n"
        f"### 🌟 Parabéns, {nome}!\n\n"
        f"Você concluiu com dedicação a trilha de **{trilha}** e está pronto para enfrentar\n"
        f"os desafios do mercado de tecnologia. Continue estudando, construindo projetos e\n"
        f"compartilhando seu conhecimento com a comunidade!\n\n"
        f"---\n\n"
        f"*Este é um certificado fictício gerado para fins de aprendizado e portfólio pessoal.*\n\n"
        f"*Powered by Bob — IBM*\n\n"
        f"> 💡 Compartilhe no LinkedIn e adicione **{trilha}** às suas habilidades!\n"
    )
