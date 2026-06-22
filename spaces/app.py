"""Interactive Gradio visualization Space for nlp-policy-nz pipeline outputs.

Provides four tabs for exploring Parquet datasets:
- **Search**: Full-text search over document chunks
- **Citations**: NZ Act cross-reference network
- **Te Reo**: Te Reo Maori term frequency visualisation
- **Stats**: Corpus-level metrics dashboard

Run locally with: ``python spaces/app.py``
"""

from __future__ import annotations

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

    matches["relevance"] = matches["raw_text"].str.lower().apply(
        lambda t: t.count(query_lower) / max(len(t.split()), 1)
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
        yaxis=dict(autorange="reversed"),
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

    with gr.Blocks(
        title="nlp-policy-nz Explorer",
        theme=gr.themes.Soft(),
    ) as app:
        gr.Markdown("# nlp-policy-nz Explorer\nInteractive visualisation of NZ parliamentary and legislative NLP datasets.")

        file_input = gr.File(
            label="Upload Parquet Dataset",
            file_types=[".parquet"],
            type="filepath",
        )

        with gr.Tabs():
            # --- Search tab ---
            with gr.Tab("Search"):
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

    return app


if __name__ == "__main__":
    app = build_app()
    app.launch()
