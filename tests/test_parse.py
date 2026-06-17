"""Unit tests for YAML parsing — no Neo4j needed."""

from pathlib import Path

import pytest

from ingest.parse import load_yaml

YAML_PATH = Path(__file__).resolve().parent.parent / "data" / "ATLAS-2026.05.yaml"

VALID_MATURITY_VALUES = {"Realized", "Demonstrated", "Feasible"}
VALID_PLATFORMS = {"Agentic AI", "Generative AI", "Predictive AI", "Enterprise"}


@pytest.fixture(scope="module")
def atlas_data() -> dict:
    """Load ATLAS YAML once for all tests."""
    return load_yaml(YAML_PATH)


def test_load_yaml_returns_all_sections(atlas_data: dict) -> None:
    """Verify all required top-level keys are present."""
    required = {"tactics", "techniques", "mitigations", "case-studies", "relationships"}
    assert required.issubset(set(atlas_data.keys()))


def test_tactic_count(atlas_data: dict) -> None:
    """Verify 16 tactics."""
    assert len(atlas_data["tactics"]) == 16


def test_technique_count(atlas_data: dict) -> None:
    """Verify 170 techniques."""
    assert len(atlas_data["techniques"]) == 170


def test_mitigation_count(atlas_data: dict) -> None:
    """Verify 35 mitigations."""
    assert len(atlas_data["mitigations"]) == 35


def test_case_study_count(atlas_data: dict) -> None:
    """Verify 57 case studies."""
    assert len(atlas_data["case-studies"]) == 57


def test_all_techniques_have_platforms(atlas_data: dict) -> None:
    """Every technique must have a non-empty platforms list."""
    for tech_id, tech in atlas_data["techniques"].items():
        platforms = tech.get("platforms", [])
        assert len(platforms) > 0, f"{tech_id} has no platforms"
        for p in platforms:
            assert p in VALID_PLATFORMS, f"{tech_id} has invalid platform: {p}"


def test_all_techniques_have_maturity(atlas_data: dict) -> None:
    """Every technique must have a valid maturity value."""
    for tech_id, tech in atlas_data["techniques"].items():
        maturity = tech.get("maturity")
        assert maturity in VALID_MATURITY_VALUES, (
            f"{tech_id} has invalid maturity: {maturity}"
        )


def test_all_mitigations_have_lifecycle_phases(atlas_data: dict) -> None:
    """Every mitigation must have a non-empty lifecycle-phases list."""
    for mit_id, mit in atlas_data["mitigations"].items():
        phases = mit.get("lifecycle-phases", [])
        assert len(phases) > 0, f"{mit_id} has no lifecycle-phases"


def test_all_mitigations_have_categories(atlas_data: dict) -> None:
    """Every mitigation must have a non-empty categories list."""
    for mit_id, mit in atlas_data["mitigations"].items():
        cats = mit.get("categories", [])
        assert len(cats) > 0, f"{mit_id} has no categories"


def test_employs_have_required_fields(atlas_data: dict) -> None:
    """All employs relationship entries must have step-id, leads-to, tactic."""
    relationships = atlas_data["relationships"]
    employs_count = 0

    for entity_id, rel_types in relationships.items():
        if "employs" not in rel_types:
            continue
        for entry in rel_types["employs"]:
            employs_count += 1
            assert "step-id" in entry, f"Missing step-id in {entity_id}"
            assert "leads-to" in entry, f"Missing leads-to in {entity_id}"
            assert "tactic" in entry, f"Missing tactic in {entity_id}"
            assert "target" in entry, f"Missing target in {entity_id}"

    assert employs_count > 0, "No employs relationships found"
