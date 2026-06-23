"""Smoke tests — quick-start checks that core imports and configs work.

These run first in CI to fail fast if the environment is broken.
"""

from __future__ import annotations

from pathlib import Path

# ── Package imports ──────────────────────────────────────────────────────


class TestPackageImports:
    """Verify top-level package imports resolve without error."""

    def test_import_nlp_policy_nz(self) -> None:
        import nlp_policy_nz  # noqa: F811

        # Package imported successfully (no version attr — read from metadata)
        assert hasattr(nlp_policy_nz, "run_nlp_pipeline")

    def test_import_guard(self) -> None:
        from nlp_policy_nz.guard import normalize_text  # noqa: F811

        assert callable(normalize_text)

    def test_import_syntactic(self) -> None:
        from nlp_policy_nz.syntactic import (  # noqa: F811
            create_nlp_pipeline,
        )

        assert callable(create_nlp_pipeline)

    def test_import_semantic(self) -> None:
        from nlp_policy_nz.semantic import generate_embedding  # noqa: F811

        assert callable(generate_embedding)

    def test_import_storage(self) -> None:
        from nlp_policy_nz.storage import (  # noqa: F811
            PipelineRecord,
        )

        assert PipelineRecord is not None

    def test_import_cli(self) -> None:
        from nlp_policy_nz.cli.main import main  # noqa: F811

        assert callable(main)

    def test_import_integrations(self) -> None:
        from nlp_policy_nz.integrations import (  # noqa: F811
            ZenodoArchiver,
            deploy_space,
            push_dataset_to_hub,
        )

        assert ZenodoArchiver is not None
        assert callable(push_dataset_to_hub)
        assert callable(deploy_space)


# ── Config files ─────────────────────────────────────────────────────────


class TestConfigFiles:
    """Verify critical project config files exist and parse correctly."""

    def test_pyproject_toml_exists(self) -> None:
        root = Path(__file__).resolve().parents[1]
        pyproject = root / "pyproject.toml"
        assert pyproject.is_file(), f"Missing pyproject.toml at {pyproject}"

    def test_pixi_toml_exists(self) -> None:
        root = Path(__file__).resolve().parents[1]
        pixi = root / "pixi.toml"
        assert pixi.is_file(), f"Missing pixi.toml at {pixi}"

    def test_tach_toml_exists(self) -> None:
        root = Path(__file__).resolve().parents[1]
        tach = root / ".tach.toml"
        assert tach.is_file(), f"Missing .tach.toml at {tach}"


# ── Conductor files ──────────────────────────────────────────────────────


class TestConductorFiles:
    """Verify conductor directory structure is intact."""

    def test_tracks_md_exists(self) -> None:
        root = Path(__file__).resolve().parents[1]
        tracks = root / "conductor" / "tracks.md"
        assert tracks.is_file(), f"Missing conductor/tracks.md at {tracks}"

    def test_product_md_exists(self) -> None:
        root = Path(__file__).resolve().parents[1]
        product = root / "conductor" / "product.md"
        assert product.is_file(), f"Missing conductor/product.md at {product}"
