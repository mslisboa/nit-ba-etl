"""Testes unitários de provenance (sem banco: interface e comportamento)."""

from __future__ import annotations

from load.provenance import STATUS_COMPLETED, STATUS_FAILED, STATUS_RUNNING, Batch


def test_batch_tem_identificacao_unica():
    b1 = Batch(source_system="teste")
    b2 = Batch(source_system="teste")
    assert b1.batch_id != b2.batch_id
    assert b1.source_system == b2.source_system


def test_constantes_de_status():
    assert {STATUS_RUNNING, STATUS_COMPLETED, STATUS_FAILED} == {
        "running",
        "completed",
        "failed",
    }


def test_ref_periodo_opcional():
    assert Batch(source_system="x").ref_period is None
    assert Batch(source_system="x", ref_period="2026").ref_period == "2026"
