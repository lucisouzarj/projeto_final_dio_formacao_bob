"""
tests/test_commands.py
Suite de testes unitários para os slash commands /trilha, /desafio e /certificado.
Cobertura-alvo: >= 70% das linhas de src/commands_engine.py

Execute com:  python -m pytest tests/test_commands.py -v
"""

import sys
import os
import json
import tempfile
import unittest
from datetime import date

# Adiciona raiz ao path para importar src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.commands_engine import (
    _load_trilhas,
    _find_trilha,
    _gerar_codigo_certificado,
    _data_extenso,
    cmd_trilha,
    cmd_desafio,
    cmd_certificado,
    NIVEIS_VALIDOS,
    TRILHAS_PATH,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

TRILHAS_MOCK = {
    "Java": {
        "descricao": "Trilha completa de Java com foco em back-end",
        "nivel": "iniciante ao avançado",
        "modulos": [
            {
                "numero": 1,
                "titulo": "Fundamentos de Java",
                "topicos": ["JDK e JVM", "Tipos primitivos e wrappers"],
            },
            {
                "numero": 2,
                "titulo": "Orientação a Objetos",
                "topicos": ["Classes e objetos", "Herança e polimorfismo"],
            },
        ],
    },
    "Python": {
        "descricao": "Trilha completa de Python",
        "nivel": "iniciante ao avançado",
        "modulos": [
            {
                "numero": 1,
                "titulo": "Fundamentos de Python",
                "topicos": ["Sintaxe básica"],
            }
        ],
    },
}


def _temp_trilhas_file(data: dict) -> str:
    """Grava um dicionário como JSON temporário e retorna o caminho."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(data, tmp, ensure_ascii=False)
    tmp.close()
    return tmp.name


# ===========================================================================
# Testes: _load_trilhas
# ===========================================================================


class TestLoadTrilhas(unittest.TestCase):

    def test_carrega_arquivo_real(self):
        """Deve carregar o trilhas.json real sem lançar exceção."""
        data = _load_trilhas(TRILHAS_PATH)
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 0)

    def test_arquivo_inexistente_levanta_erro(self):
        """Deve lançar FileNotFoundError para caminho inválido."""
        with self.assertRaises(FileNotFoundError):
            _load_trilhas("/caminho/que/nao/existe.json")

    def test_contem_chave_java(self):
        """O arquivo real deve conter a trilha Java."""
        data = _load_trilhas(TRILHAS_PATH)
        self.assertIn("Java", data)

    def test_java_tem_modulos(self):
        """A trilha Java deve ter pelo menos 1 módulo."""
        data = _load_trilhas(TRILHAS_PATH)
        self.assertGreater(len(data["Java"]["modulos"]), 0)


# ===========================================================================
# Testes: _find_trilha
# ===========================================================================


class TestFindTrilha(unittest.TestCase):

    def test_busca_exata(self):
        chave, trilha = _find_trilha(TRILHAS_MOCK, "Java")
        self.assertEqual(chave, "Java")
        self.assertIsNotNone(trilha)

    def test_busca_lowercase(self):
        """Busca case-insensitive: 'java' deve encontrar 'Java'."""
        chave, trilha = _find_trilha(TRILHAS_MOCK, "java")
        self.assertEqual(chave, "Java")

    def test_busca_uppercase(self):
        """Busca case-insensitive: 'JAVA' deve encontrar 'Java'."""
        chave, trilha = _find_trilha(TRILHAS_MOCK, "JAVA")
        self.assertEqual(chave, "Java")

    def test_busca_mista(self):
        """Busca case-insensitive: 'JaVa' deve encontrar 'Java'."""
        chave, trilha = _find_trilha(TRILHAS_MOCK, "JaVa")
        self.assertEqual(chave, "Java")

    def test_nao_encontrado_retorna_none(self):
        chave, trilha = _find_trilha(TRILHAS_MOCK, "Go")
        self.assertIsNone(chave)
        self.assertIsNone(trilha)

    def test_busca_com_espacos(self):
        """Espaços extras no input devem ser ignorados."""
        chave, trilha = _find_trilha(TRILHAS_MOCK, "  java  ")
        self.assertEqual(chave, "Java")


# ===========================================================================
# Testes: _gerar_codigo_certificado
# ===========================================================================


class TestGerarCodigoCertificado(unittest.TestCase):

    def test_formato_correto(self):
        """Formato esperado: DIO-{ANO}-{6 CHARS}."""
        codigo = _gerar_codigo_certificado(2025)
        self.assertRegex(codigo, r"^DIO-2025-[A-Z0-9]{6}$")

    def test_ano_padrao_e_atual(self):
        """Sem ano explícito deve usar o ano atual."""
        codigo = _gerar_codigo_certificado()
        ano_atual = str(date.today().year)
        self.assertIn(ano_atual, codigo)

    def test_codigos_diferentes_em_chamadas_distintas(self):
        """Dois códigos gerados sem seed devem (provavelmente) ser diferentes."""
        codigos = {_gerar_codigo_certificado(2025) for _ in range(20)}
        self.assertGreater(len(codigos), 1)


# ===========================================================================
# Testes: _data_extenso
# ===========================================================================


class TestDataExtenso(unittest.TestCase):

    def test_data_especifica(self):
        d = date(2025, 1, 15)
        resultado = _data_extenso(d)
        self.assertEqual(resultado, "15 de janeiro de 2025")

    def test_mes_dezembro(self):
        d = date(2024, 12, 1)
        self.assertIn("dezembro", _data_extenso(d))

    def test_data_padrao_e_hoje(self):
        resultado = _data_extenso()
        hoje = date.today()
        self.assertIn(str(hoje.year), resultado)


# ===========================================================================
# Testes: cmd_trilha
# ===========================================================================


class TestCmdTrilha(unittest.TestCase):

    def setUp(self):
        self.path = _temp_trilhas_file(TRILHAS_MOCK)

    def tearDown(self):
        os.unlink(self.path)

    # --- Encontrado --------------------------------------------------------

    def test_java_encontrado(self):
        resultado = cmd_trilha("Java", self.path)
        self.assertIn("Trilha de Java", resultado)

    def test_java_case_insensitive(self):
        resultado = cmd_trilha("java", self.path)
        self.assertIn("Trilha de Java", resultado)

    def test_java_uppercase(self):
        resultado = cmd_trilha("JAVA", self.path)
        self.assertIn("Trilha de Java", resultado)

    def test_contem_descricao(self):
        resultado = cmd_trilha("Java", self.path)
        self.assertIn("Trilha completa de Java", resultado)

    def test_contem_nivel(self):
        resultado = cmd_trilha("Java", self.path)
        self.assertIn("iniciante ao avançado", resultado)

    def test_contem_modulo_1(self):
        resultado = cmd_trilha("Java", self.path)
        self.assertIn("Módulo 1", resultado)

    def test_contem_topico_jdk(self):
        resultado = cmd_trilha("Java", self.path)
        self.assertIn("JDK e JVM", resultado)

    def test_mensagem_motivacional(self):
        resultado = cmd_trilha("Java", self.path)
        self.assertIn("🚀", resultado)

    # --- Não encontrado ----------------------------------------------------

    def test_tecnologia_inexistente(self):
        resultado = cmd_trilha("Rust", self.path)
        self.assertIn("não encontrada", resultado)

    def test_lista_disponiveis_quando_nao_encontrado(self):
        resultado = cmd_trilha("Kotlin", self.path)
        self.assertIn("Java", resultado)
        self.assertIn("Python", resultado)

    # --- Arquivo real -------------------------------------------------------

    def test_java_no_arquivo_real(self):
        """Teste de integração leve: Java no trilhas.json real."""
        resultado = cmd_trilha("Java", TRILHAS_PATH)
        self.assertIn("Spring Boot", resultado)

    def test_java_real_6_modulos(self):
        """A trilha Java real deve ter 6 módulos listados."""
        resultado = cmd_trilha("Java", TRILHAS_PATH)
        self.assertIn("Módulo 6", resultado)


# ===========================================================================
# Testes: cmd_desafio
# ===========================================================================


class TestCmdDesafio(unittest.TestCase):

    def test_nivel_iniciante(self):
        resultado = cmd_desafio("Java", "iniciante", seed=42)
        self.assertIn("iniciante", resultado)

    def test_nivel_intermediario(self):
        resultado = cmd_desafio("Java", "intermediario", seed=42)
        self.assertIn("intermediario", resultado)

    def test_nivel_avancado(self):
        resultado = cmd_desafio("Java", "avancado", seed=42)
        self.assertIn("avancado", resultado)

    def test_nivel_invalido_usa_iniciante(self):
        resultado = cmd_desafio("Java", "supremo", seed=42)
        self.assertIn("iniciante", resultado)

    def test_nivel_vazio_usa_iniciante(self):
        resultado = cmd_desafio("Java", "", seed=42)
        self.assertIn("iniciante", resultado)

    def test_contem_tecnologia(self):
        resultado = cmd_desafio("Java", "avancado", seed=1)
        self.assertIn("Java", resultado)

    def test_contem_secao_descricao(self):
        resultado = cmd_desafio("Java", "iniciante", seed=0)
        self.assertIn("## 📋 Descrição", resultado)

    def test_contem_secao_requisitos(self):
        resultado = cmd_desafio("Java", "iniciante", seed=0)
        self.assertIn("## 🎯 Requisitos", resultado)

    def test_contem_secao_dicas(self):
        resultado = cmd_desafio("Java", "iniciante", seed=0)
        self.assertIn("## 💡 Dicas", resultado)

    def test_contem_tabela_avaliacao(self):
        resultado = cmd_desafio("Java", "intermediario", seed=0)
        self.assertIn("Correção", resultado)
        self.assertIn("40%", resultado)

    def test_contem_tempo_sugerido(self):
        resultado = cmd_desafio("Java", "avancado", seed=0)
        self.assertIn("2 horas", resultado)

    def test_seed_determinista(self):
        """Mesma seed deve produzir exatamente o mesmo resultado."""
        r1 = cmd_desafio("Java", "intermediario", seed=99)
        r2 = cmd_desafio("Java", "intermediario", seed=99)
        self.assertEqual(r1, r2)

    def test_seeds_diferentes_podem_variar(self):
        """Seeds diferentes devem (em geral) produzir desafios diferentes."""
        resultados = {cmd_desafio("Java", "iniciante", seed=s) for s in range(10)}
        self.assertGreater(len(resultados), 1)


# ===========================================================================
# Testes: cmd_certificado
# ===========================================================================


class TestCmdCertificado(unittest.TestCase):

    DATA_FIXA = date(2025, 7, 10)
    CODIGO_FIXO = "DIO-2025-TEST01"

    def _cert(self, nome="Helton Cavalcanti", trilha="Java"):
        return cmd_certificado(
            nome, trilha, data_emissao=self.DATA_FIXA, codigo=self.CODIGO_FIXO
        )

    def test_contem_nome_aluno(self):
        self.assertIn("Helton Cavalcanti", self._cert())

    def test_contem_trilha(self):
        self.assertIn("Java", self._cert())

    def test_contem_codigo_certificado(self):
        self.assertIn("DIO-2025-TEST01", self._cert())

    def test_contem_data_emissao(self):
        self.assertIn("10 de julho de 2025", self._cert())

    def test_contem_carga_horaria_java(self):
        self.assertIn("80h", self._cert())

    def test_competencias_java(self):
        resultado = self._cert()
        self.assertIn("Spring Boot", resultado)
        self.assertIn("JUnit 5", resultado)

    def test_mensagem_parabenizacao(self):
        resultado = self._cert()
        self.assertIn("Parabéns", resultado)

    def test_footer_bob(self):
        resultado = self._cert()
        self.assertIn("Powered by Bob", resultado)

    def test_trilha_desconhecida_usa_competencias_padrao(self):
        resultado = cmd_certificado(
            "Alice", "Kotlin", data_emissao=self.DATA_FIXA, codigo=self.CODIGO_FIXO
        )
        self.assertIn("Git", resultado)

    def test_codigo_gerado_automaticamente(self):
        """Sem código explícito, deve gerar um no formato correto."""
        import re
        resultado = cmd_certificado("Bob", "Java", data_emissao=self.DATA_FIXA)
        self.assertRegex(resultado, r"DIO-\d{4}-[A-Z0-9]{6}")

    def test_carga_python(self):
        resultado = cmd_certificado(
            "Ana", "Python", data_emissao=self.DATA_FIXA, codigo=self.CODIGO_FIXO
        )
        self.assertIn("60h", resultado)

    def test_linkedin_dica(self):
        self.assertIn("LinkedIn", self._cert())


# ===========================================================================
# Ponto de entrada
# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)
