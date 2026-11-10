"""Testes unitários das etapas do pipeline demo (sem banco).

Fixtures sintéticas em tmp_path: nenhum dado real versionado
(architecture.md §12) — a fixture data/raw/demo/amostra.csv é usada
apenas no teste de integração de ponta a ponta.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from common.exceptions import FormatError
from pipelines.demo import _find_input_file, extract, transform, validate

SINTETICO = (
    "nome,sigla,descricao\n"
    "Registro Sintetico ALFA,RSA,Amostra anonimizada\n"
    "Registro Sintetico BETA,,Sem sigla: rejeitado\n"
)


class TestFindInputFile:
    def test_diretorio_ausente(self, tmp_path):
        with pytest.raises(FormatError, match="ausente"):
            _find_input_file(tmp_path)

    def test_dir_sem_csv(self, tmp_path):
        (tmp_path / "raw" / "demo").mkdir(parents=True)
        with pytest.raises(FormatError, match="Nenhum arquivo"):
            _find_input_file(tmp_path)

    def test_multiplos_csv_ambiguos(self, tmp_path):
        d = tmp_path / "raw" / "demo"
        d.mkdir(parents=True)
        (d / "a.csv").touch()
        (d / "b.csv").touch()
        with pytest.raises(FormatError, match="Múltiplos"):
            _find_input_file(tmp_path)

    def test_unico_csv_localizado(self, tmp_path):
        d = tmp_path / "raw" / "demo"
        d.mkdir(parents=True)
        arquivo = d / "amostra.csv"
        arquivo.write_text(SINTETICO, encoding="utf-8")
        assert _find_input_file(tmp_path) == arquivo


class TestExtract:
    def test_leitura_preserva_conteudo(self, tmp_path):
        arquivo = tmp_path / "amostra.csv"
        arquivo.write_text(SINTETICO, encoding="utf-8")
        rows = extract(arquivo)
        assert len(rows) == 2
        assert rows[0] == {
            "nome": "Registro Sintetico ALFA",
            "sigla": "RSA",
            "descricao": "Amostra anonimizada",
        }

    def test_arquivo_ilegivel(self, tmp_path):
        arquivo: Path = tmp_path / "_dir_inexistente" / "x.csv"
        with pytest.raises(FormatError):
            extract(arquivo)


class TestTransform:
    def test_trim_de_bordas(self):
        row = {"nome": "  Espaço  ", "sigla": " E1 ", "vazio": None}
        out = transform([row])[0]
        assert out == {"nome": "Espaço", "sigla": "E1", "vazio": ""}

    def test_lista_vazia(self):
        assert transform([]) == []


class TestValidate:
    def test_separacao_validos_invalidos(self):
        rows = transform(
            [
                {"nome": "A", "sigla": "A1"},
                {"nome": "B", "sigla": ""},
            ]
        )
        validos, invalidos, _ = validate(rows)
        assert len(validos) == 1
        assert len(invalidos) == 1
        assert invalidos[0]["nome"] == "B"
