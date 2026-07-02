"""Interactive Gradio visualization Space for nlp-policy-nz pipeline outputs.

Provides fixture-backed tabs for exploring Track 32-35 artifacts, plus the
original Parquet dataset browser:
- **Overview**: Bounded artifact summary and explicit data boundary
- **Corpus Statistics**: Track 32 checked-in statistics
- **Ontology Coverage**: Track 25/29-31 coverage summaries
- **Graph and Vectors**: Track 33 network and projection outputs
- **Artifacts**: Track 35 generated publication artifacts
- **Publication Protocol**: Track 34 evidence-mapped publication protocol
- **Search**: Full-text search over document chunks
- **Citations**: NZ Act cross-reference network
- **Te Reo**: Te Reo Maori term frequency visualisation
- **Stats**: Corpus-level metrics dashboard

Run locally with: ``python spaces/app.py``
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

try:
    import gradio as gr
except ModuleNotFoundError:
    gr = None

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


REPO_ROOT = Path(__file__).resolve().parents[1]
SPACE_PAGES = [
    "Overview",
    "Corpus Statistics",
    "Ontology Coverage",
    "Graph and Vectors",
    "Artifacts",
    "Publication Protocol",
    "Dataset Browser",
]
SPACE_CSS = """
.gradio-container :focus-visible {
    outline: 3px solid #0b5fff;
    outline-offset: 2px;
}

#skip-link {
    margin-bottom: 0.75rem;
}

#main-content {
    scroll-margin-top: 1rem;
}

#privacy-footer {
    border-top: 1px solid #cbd5e1;
    margin-top: 1.5rem;
    padding-top: 1rem;
    color: #0f172a;
}

#privacy-footer p {
    max-width: 72ch;
}

.gradio-container .tabitem {
    text-wrap: balance;
}
"""

PRIVACY_NOTICE = (
    "Privacy notice: this Space is fixture-first and may display parliamentary "
    "and legislative content that includes names, electorate references, and "
    "other potentially identifying information. For deletion or correction "
    "requests, email privacy@nlp-policy-nz.example and include the dataset "
    "source, document identifier, and the requested change. See PRIVACY.md "
    "for retention and processor details."
)


def _read_json(path: Path, fallback: object) -> object:
    """Read JSON with a deterministic fallback for missing fixture files."""
    if not path.is_file():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def _read_csv(path: Path) -> pd.DataFrame:
    """Read CSV with an empty DataFrame fallback."""
    if not path.is_file():
        return pd.DataFrame()
    return pd.read_csv(path)


def _read_text(path: Path) -> str:
    """Read UTF-8 text with a missing-data label."""
    if not path.is_file():
        return f"Missing checked-in artifact: {path.as_posix()}"
    return path.read_text(encoding="utf-8")


def build_fixture_mode_notice() -> str:
    """Return the public data-boundary label for the Space."""
    return (
        "Fixture mode: this Space loads checked-in, bounded Track 32-35 artifacts "
        "by default so it can run without credentials in local development and "
        "GitHub Actions. Requires full corpus: upload PipelineRecord Parquet files "
        "or mount full LanceDB/Parquet exports to make corpus-wide claims."
    )


def load_explorer_artifacts(repo_root: Path | str | None = None) -> dict[str, object]:
    """Load checked-in artifacts for the Track 36 exploration pages."""
    root = Path(repo_root) if repo_root is not None else REPO_ROOT
    statistics_dir = root / "data" / "statistics"
    analysis_dir = root / "data" / "analysis"
    publication_dir = root / "data" / "publication"
    artifacts_dir = root / "artifacts"

    publication_claims = _read_json(publication_dir / "publication_protocol_claims.json", {})
    if not isinstance(publication_claims, dict):
        publication_claims = {}

    return {
        "mode": "fixture",
        "mode_notice": build_fixture_mode_notice(),
        "space_pages": SPACE_PAGES,
        "corpus_statistics": {
            "manifest": _read_json(statistics_dir / "corpus_statistics_manifest.json", {}),
            "per_corpus": _read_csv(statistics_dir / "corpus_statistics_per_corpus.csv"),
            "per_year": _read_csv(statistics_dir / "corpus_statistics_per_year.csv"),
            "entity_types": _read_csv(statistics_dir / "corpus_statistics_entity_types.csv"),
            "blockers": _read_json(statistics_dir / "corpus_statistics_blockers.json", []),
        },
        "ontology_coverage": _read_json(
            statistics_dir / "corpus_statistics_ontology_coverage.json",
            {},
        ),
        "graph_vector": {
            "manifest": _read_json(analysis_dir / "graph_vector_manifest.json", {}),
            "graph_metrics": _read_json(analysis_dir / "graph_vector_graph_metrics.json", {}),
            "vector_metrics": _read_json(analysis_dir / "graph_vector_vector_metrics.json", {}),
            "alignment": _read_csv(analysis_dir / "graph_vector_alignment.csv"),
            "blockers": _read_json(analysis_dir / "graph_vector_blockers.json", []),
            "network": _read_text(analysis_dir / "graph_vector_network.mmd"),
        },
        "analysis_artifacts": {
            "manifest": _read_json(artifacts_dir / "analysis_artifact_manifest.json", {}),
            "blockers": _read_json(artifacts_dir / "analysis_artifact_blockers.json", []),
            "visual_inspection": _read_text(artifacts_dir / "visual_inspection_checklist.md"),
        },
        "publication_protocol": {
            "manifest": _read_json(publication_dir / "publication_protocol_manifest.json", {}),
            "claims": publication_claims.get("claims", []),
            "overclaim_review": _read_json(
                publication_dir / "publication_protocol_overclaim_review.json",
                [],
            ),
            "markdown": _read_text(root / "docs" / "publication_protocol.md"),
        },
    }


def summarize_explorer_artifacts(artifacts: dict[str, object]) -> dict[str, object]:
    """Summarize Track 36 fixture artifacts for the overview page."""
    corpus_summary = artifacts["corpus_statistics"]["manifest"].get("summary", {})
    graph_summary = artifacts["graph_vector"]["manifest"].get("summary", {})
    artifact_summary = artifacts["analysis_artifacts"]["manifest"].get("summary", {})
    publication_summary = artifacts["publication_protocol"]["manifest"].get("claim_counts", {})
    known_blockers = (
        len(artifacts["corpus_statistics"]["blockers"])
        + len(artifacts["graph_vector"]["blockers"])
        + len(artifacts["analysis_artifacts"]["blockers"])
        + len(artifacts["publication_protocol"]["overclaim_review"])
    )
    return {
        "mode": artifacts["mode"],
        "space_pages": artifacts["space_pages"],
        "record_count": corpus_summary.get("record_count", 0),
        "corpus_count": corpus_summary.get("corpus_count", 0),
        "graph_node_count": graph_summary.get("graph_node_count", 0),
        "graph_edge_count": graph_summary.get("graph_edge_count", 0),
        "vector_count": graph_summary.get("vector_count", 0),
        "available_artifacts": artifact_summary.get("available_count", 0),
        "publication_claims": publication_summary.get("total", 0),
        "known_blockers": known_blockers,
    }


def build_ontology_coverage_table(artifacts: dict[str, object]) -> pd.DataFrame:
    """Render ontology coverage summaries as a matrix-friendly table."""
    coverage = artifacts["ontology_coverage"]
    rows: list[dict[str, object]] = []
    for track, values in coverage.items():
        if not isinstance(values, dict):
            continue
        for metric, value in values.items():
            if isinstance(value, dict):
                for label, count in value.items():
                    rows.append(
                        {
                            "track": track,
                            "metric": metric,
                            "value": label,
                            "count": count,
                        }
                    )
            elif isinstance(value, list):
                rows.append(
                    {
                        "track": track,
                        "metric": metric,
                        "value": ", ".join(str(item) for item in value),
                        "count": len(value),
                    }
                )
            else:
                rows.append(
                    {
                        "track": track,
                        "metric": metric,
                        "value": str(value),
                        "count": value if isinstance(value, int | float) else None,
                    }
                )
    return pd.DataFrame(rows)


def build_publication_claims_table(artifacts: dict[str, object]) -> pd.DataFrame:
    """Render Track 34 publication claims with evidence status."""
    claims = artifacts["publication_protocol"]["claims"]
    rows = [
        {
            "claim_id": claim.get("claim_id", ""),
            "claim_status": claim.get("claim_status", ""),
            "protocol_section": claim.get("protocol_section", ""),
            "claim": claim.get("claim", ""),
            "evidence_paths": ", ".join(claim.get("evidence_paths", [])),
        }
        for claim in claims
    ]
    return pd.DataFrame(rows)


def build_artifact_inventory_table(artifacts: dict[str, object]) -> pd.DataFrame:
    """Render Track 35 publication artifact inventory."""
    manifest = artifacts["analysis_artifacts"]["manifest"]
    return pd.DataFrame(manifest.get("artifacts", []))


def build_blocker_table(artifacts: dict[str, object]) -> pd.DataFrame:
    """Render known blockers and overclaim risks across Track 32-35."""
    rows: list[dict[str, object]] = []
    for source, blockers in [
        ("corpus_statistics", artifacts["corpus_statistics"]["blockers"]),
        ("graph_vector", artifacts["graph_vector"]["blockers"]),
        ("analysis_artifacts", artifacts["analysis_artifacts"]["blockers"]),
        ("publication_protocol", artifacts["publication_protocol"]["overclaim_review"]),
    ]:
        for blocker in blockers:
            row = {"source": source}
            if isinstance(blocker, dict):
                row.update(blocker)
            else:
                row["detail"] = str(blocker)
            rows.append(row)
    return pd.DataFrame(rows)


def build_corpus_statistics_chart(artifacts: dict[str, object]) -> go.Figure:
    """Build a Track 32 corpus record/token chart."""
    per_corpus = artifacts["corpus_statistics"]["per_corpus"]
    if per_corpus.empty:
        return go.Figure()
    return px.bar(
        per_corpus,
        x="corpus_source",
        y=["record_count", "token_count"],
        barmode="group",
        title="Fixture Corpus Records and Tokens",
    )


def build_graph_vector_projection(artifacts: dict[str, object]) -> go.Figure:
    """Build a Track 33 vector projection chart."""
    projection = artifacts["graph_vector"]["vector_metrics"].get("pca_projection", [])
    if not projection:
        return go.Figure()
    projection_df = pd.DataFrame(projection)
    return px.scatter(
        projection_df,
        x="pc1",
        y="pc2",
        hover_name="record_id",
        title="Fixture Vector PCA Projection",
    )


def load_parquet(file_path: str | None) -> pd.DataFrame | None:
    """Load a Parquet file into a pandas DataFrame.

    Parameters
    ----------
    file_path : str | None
        Path to a Parquet file.

    Returns
    -------
    pd.DataFrame | None
        The loaded DataFrame, or ``None`` if no file is provided.

    """
    if file_path is None:
        return None
    path = Path(file_path)
    if not path.is_file():
        return None
    return pd.read_parquet(path)


# ---------------------------------------------------------------------------
# Search tab
# ---------------------------------------------------------------------------


def search_chunks(
    query: str,
    df: pd.DataFrame | None,
    top_k: int,
) -> pd.DataFrame:
    """Search document chunks by simple substring matching.

    Parameters
    ----------
    query : str
        The search query.
    df : pd.DataFrame | None
        The loaded dataset.
    top_k : int
        Maximum number of results to return.

    Returns
    -------
    pd.DataFrame
        Matching rows with relevance scoring.

    """
    if df is None or not query.strip():
        return pd.DataFrame()

    query_lower = query.lower()
    mask = df["raw_text"].str.lower().str.contains(query_lower, na=False)
    matches = df[mask].head(top_k).copy()

    if matches.empty:
        return matches

    matches["relevance"] = (
        matches["raw_text"]
        .str.lower()
        .apply(lambda t: t.count(query_lower) / max(len(t.split()), 1))
    )
    display_cols = ["doc_id", "corpus_source", "raw_text", "relevance"]
    return matches[display_cols].sort_values("relevance", ascending=False)


# ---------------------------------------------------------------------------
# Citations tab
# ---------------------------------------------------------------------------


def build_citation_network(df: pd.DataFrame | None) -> go.Figure | str:
    """Build a citation cross-reference visualisation.

    Parameters
    ----------
    df : pd.DataFrame | None
        The loaded dataset.

    Returns
    -------
    go.Figure | str
        A Plotly figure, or an error message string.

    """
    if df is None:
        return "Upload a Parquet file to visualise citations."

    if "nz_act_citations" not in df.columns:
        return "No citation column found in dataset."

    all_citations: list[str] = []
    for cell in df["nz_act_citations"]:
        if isinstance(cell, list):
            all_citations.extend(cell)
        elif isinstance(cell, str) and cell:
            all_citations.extend([c.strip() for c in cell.split(",") if c.strip()])

    if not all_citations:
        return "No citations found in the dataset."

    counts = Counter(all_citations)
    top = counts.most_common(20)
    labels = [c[0] for c in top]
    values = [c[1] for c in top]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color="#2196F3",
        )
    )
    fig.update_layout(
        title="Top 20 NZ Act Citations",
        xaxis_title="Frequency",
        yaxis_title="Citation",
        yaxis={"autorange": "reversed"},
        height=500,
    )
    return fig


# ---------------------------------------------------------------------------
# Te Reo tab
# ---------------------------------------------------------------------------


def build_tereo_chart(df: pd.DataFrame | None) -> go.Figure | str:
    """Build a Te Reo Maori term frequency chart.

    Parameters
    ----------
    df : pd.DataFrame | None
        The loaded dataset.

    Returns
    -------
    go.Figure | str
        A Plotly figure, or an error message string.

    """
    if df is None:
        return "Upload a Parquet file to visualise Te Reo terms."

    if "te_reo_terms" not in df.columns:
        return "No te_reo_terms column found in dataset."

    all_terms: list[str] = []
    for cell in df["te_reo_terms"]:
        if isinstance(cell, list):
            all_terms.extend(cell)
        elif isinstance(cell, str) and cell:
            all_terms.extend([t.strip() for t in cell.split(",") if t.strip()])

    if not all_terms:
        return "No Te Reo Maori terms found in the dataset."

    counts = Counter(all_terms)
    top = counts.most_common(30)
    terms = [t[0] for t in top]
    freqs = [t[1] for t in top]

    fig = px.bar(
        x=terms,
        y=freqs,
        labels={"x": "Term", "y": "Frequency"},
        title="Top 30 Te Reo Maori Terms",
        color_discrete_sequence=["#4CAF50"],
    )
    fig.update_layout(xaxis_tickangle=-45, height=450)
    return fig


# ---------------------------------------------------------------------------
# Stats tab
# ---------------------------------------------------------------------------


def compute_stats(df: pd.DataFrame | None) -> dict[str, str | int]:
    """Compute corpus-level statistics.

    Parameters
    ----------
    df : pd.DataFrame | None
        The loaded dataset.

    Returns
    -------
    dict[str, str | int]
        A dictionary of statistic name to value.

    """
    if df is None:
        return {"Status": "No dataset loaded"}

    stats: dict[str, str | int] = {}
    stats["Total Chunks"] = len(df)

    if "corpus_source" in df.columns:
        source_counts = df["corpus_source"].value_counts()
        for source, count in source_counts.items():
            stats[f"Source: {source}"] = int(count)

    if "embeddings" in df.columns:
        has_embed = df["embeddings"].apply(lambda x: x is not None and len(x) > 0).sum()
        stats["Chunks with Embeddings"] = int(has_embed)
        sample = df["embeddings"].dropna().iloc[0] if has_embed > 0 else None
        if sample is not None and hasattr(sample, "__len__"):
            stats["Embedding Dimension"] = len(sample)

    if "te_reo_terms" in df.columns:
        has_tereo = df["te_reo_terms"].apply(lambda x: isinstance(x, list) and len(x) > 0).sum()
        stats["Chunks with Te Reo"] = int(has_tereo)

    if "nz_act_citations" in df.columns:
        has_cite = df["nz_act_citations"].apply(lambda x: isinstance(x, list) and len(x) > 0).sum()
        stats["Chunks with Citations"] = int(has_cite)

    if "raw_text" in df.columns:
        total_words = df["raw_text"].str.split().str.len().sum()
        stats["Total Words"] = int(total_words)

    return stats


# ---------------------------------------------------------------------------
# Gradio app
# ---------------------------------------------------------------------------


def build_app() -> object:
    """Build and return the Gradio Blocks application.

    Returns
    -------
    object
        The configured Gradio application.

    """
    if gr is None:
        raise RuntimeError("gradio is required to build the interactive Space")

    explorer_artifacts = load_explorer_artifacts()
    overview_summary = summarize_explorer_artifacts(explorer_artifacts)
    ontology_table = build_ontology_coverage_table(explorer_artifacts)
    publication_claims = build_publication_claims_table(explorer_artifacts)
    artifact_inventory = build_artifact_inventory_table(explorer_artifacts)
    blocker_table = build_blocker_table(explorer_artifacts)

    with gr.Blocks(
        title="nlp-policy-nz Explorer",
        theme=gr.themes.Soft(primary_hue="blue", secondary_hue="green", neutral_hue="slate"),
        css=SPACE_CSS,
        analytics_enabled=False,
    ) as app:
        gr.Markdown(
            "[Skip to main content](#main-content)",
            elem_id="skip-link",
        )
        gr.Markdown(
            "# nlp-policy-nz Explorer\nInteractive visualisation of NZ parliamentary and legislative NLP datasets.",
        )
        gr.Markdown(explorer_artifacts["mode_notice"])

        file_input = gr.File(
            label="Upload a Parquet dataset",
            file_types=[".parquet"],
            type="filepath",
        )

        gr.Markdown("", elem_id="main-content")

        with gr.Tabs():
            with gr.Tab("Overview"):
                gr.JSON(value=overview_summary, label="Track 32-35 Artifact Summary")
                gr.Dataframe(value=blocker_table, label="Known Blockers and Overclaim Risks")

            with gr.Tab("Corpus Statistics"):
                gr.Plot(
                    value=build_corpus_statistics_chart(explorer_artifacts),
                    label="Corpus Statistics",
                )
                gr.Dataframe(
                    value=explorer_artifacts["corpus_statistics"]["per_corpus"],
                    label="Per-Corpus Metrics",
                )
                gr.Dataframe(
                    value=explorer_artifacts["corpus_statistics"]["per_year"],
                    label="Per-Year Metrics",
                )
                gr.Dataframe(
                    value=explorer_artifacts["corpus_statistics"]["entity_types"],
                    label="Entity Type Metrics",
                )

            with gr.Tab("Ontology Coverage"):
                gr.Dataframe(value=ontology_table, label="Ontology Coverage Matrix")

            with gr.Tab("Graph and Vectors"):
                gr.JSON(
                    value=explorer_artifacts["graph_vector"]["manifest"],
                    label="Graph and Vector Manifest",
                )
                gr.Plot(
                    value=build_graph_vector_projection(explorer_artifacts),
                    label="Vector Projection",
                )
                gr.Dataframe(
                    value=explorer_artifacts["graph_vector"]["alignment"],
                    label="Graph/Vector Alignment",
                )
                gr.Code(
                    value=explorer_artifacts["graph_vector"]["network"],
                    language="markdown",
                    label="Mermaid Network",
                )

            with gr.Tab("Artifacts"):
                gr.Dataframe(value=artifact_inventory, label="Generated Artifacts")
                gr.Markdown(explorer_artifacts["analysis_artifacts"]["visual_inspection"])

            with gr.Tab("Publication Protocol"):
                gr.Dataframe(value=publication_claims, label="Evidence-Mapped Claims")
                gr.Markdown(explorer_artifacts["publication_protocol"]["markdown"])

            # --- Search tab ---
            with gr.Tab("Dataset Browser"):
                with gr.Row():
                    query_input = gr.Textbox(
                        label="Search Query",
                        placeholder="e.g. Treaty of Waitangi, climate change...",
                    )
                    top_k_input = gr.Slider(
                        minimum=1,
                        maximum=50,
                        value=10,
                        step=1,
                        label="Max Results",
                    )
                search_btn = gr.Button("Search", variant="primary")
                search_output = gr.Dataframe(label="Results")

                state_df = gr.State(None)

                file_input.change(fn=load_parquet, inputs=[file_input], outputs=[state_df])
                search_btn.click(
                    fn=search_chunks,
                    inputs=[query_input, state_df, top_k_input],
                    outputs=[search_output],
                )

            # --- Citations tab ---
            with gr.Tab("Citations"):
                citation_btn = gr.Button("Build Citation Network", variant="primary")
                citation_output = gr.Plot(label="Citation Network")
                citation_btn.click(
                    fn=build_citation_network,
                    inputs=[state_df],
                    outputs=[citation_output],
                )

            # --- Te Reo tab ---
            with gr.Tab("Te Reo Maori"):
                tereo_btn = gr.Button("Show Term Frequencies", variant="primary")
                tereo_output = gr.Plot(label="Te Reo Terms")
                tereo_btn.click(
                    fn=build_tereo_chart,
                    inputs=[state_df],
                    outputs=[tereo_output],
                )

            # --- Stats tab ---
            with gr.Tab("Stats"):
                stats_btn = gr.Button("Compute Statistics", variant="primary")
                stats_output = gr.JSON(label="Corpus Statistics")
                stats_btn.click(
                    fn=compute_stats,
                    inputs=[state_df],
                    outputs=[stats_output],
                )

        gr.Markdown(
            f"<div id='privacy-footer'>{PRIVACY_NOTICE} "
            "The Space footer is part of the public-facing compliance surface. "
            "[Read the policy](../PRIVACY.md).</div>",
        )

    return app


if __name__ == "__main__":
    app = build_app()
    app.launch()
