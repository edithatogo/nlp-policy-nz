"""Auto-generate Hugging Face dataset cards from pipeline metadata.

Builds YAML frontmatter and a markdown description body suitable for
uploading as a ``README.md`` alongside a Hugging Face dataset.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DATASET_CARD_TEMPLATE = """\
---
{yaml_frontmatter}---

# {title}

{description}

## Dataset Details

| Property | Value |
|----------|-------|
| **Source** | {source} |
| **Total Chunks** | {total_chunks} |
| **Corpus Types** | {corpus_types} |
| **Embedding Dimension** | {embedding_dim} |
| **Language** | English, Te Reo Māori |

## Schema

| Column | Type | Description |
|--------|------|-------------|
| doc_id | string | Unique document identifier |
| corpus_source | string | Source corpus (legislation / hansard / select_committee etc.) |
| raw_text | string | Original raw text of the document chunk |
| cleaned_tokens | list[string] | Tokenised and cleaned tokens |
| nz_act_citations | list[string] | NZ Act cross-references detected |
| te_reo_terms | list[string] | Te Reo Maori terms identified |
| embeddings | list[float] | Dense vector embedding (if generated) |
| submitter_name | string | Name of the submission author/organisation (submissions) |
| committee | string | Name of the select or regulations review committee |
| bill_reference | string | Related bill/act reference |
| linkage_confidence | float | Confidence score for the bill linkage |
| challenged_regulation | string | Regulation being challenged (regulations review) |
| grounds | string | Grounds for challenging the regulation (regulations review) |
| report_title | string | Title of the select committee report |
| findings | list[string] | Findings extracted from the report |
| recommendations | list[string] | Recommendations extracted from the report |


## Usage

```python
from datasets import load_dataset

ds = load_dataset("{repo_id}", split="train")
print(ds[0])
```

## Processing Pipeline

This dataset was produced by the `nlp-policy-nz` NLP preprocessing pipeline:

1. **Ingestion** — Raw XML/JSON/Text documents parsed via `UniversalIngestionEngine`
2. **Maori Language Guard** — Unicode normalisation and Te Reo token protection
3. **Syntactic Layer** — Sentence segmentation, token cleaning, citation extraction
4. **Semantic Layer** — Dense vector embeddings via Hugging Face Transformers
5. **Serialisation** — Output to Apache Parquet format

## Citation

```bibtex
@misc{{nlp_policy_nz_{year},
  title={{nlp-policy-nz: NLP Preprocessing Pipeline for New Zealand Legislation and Hansard}},
  year={{{year}}},
  publisher={{Hugging Face}},
  url={{https://huggingface.co/datasets/{repo_id}}}
}}
```
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_dataset_card(
    repo_id: str,
    *,
    source: str = "New Zealand Parliament & Legislation",
    title: str = "NZ Parliamentary & Legislative Corpus",
    description: str = (
        "Preprocessed NLP dataset of New Zealand legislation and Hansard "
        "parliamentary debates, with Maori-language annotations, citation "
        "networks, and dense vector embeddings."
    ),
    total_chunks: int | None = None,
    corpus_types: str = "legislation, hansard",
    embedding_dim: int | None = None,
    license_id: str = "mit",
    year: int | None = None,
    tags: list[str] | None = None,
) -> str:
    """Generate a Hugging Face dataset card (README.md) content.

    Parameters
    ----------
    repo_id : str
        Dataset repository identifier (``"user/dataset"`` format).
    source : str
        Description of the data source.
    title : str
        Dataset title for the markdown heading.
    description : str
        Human-readable description of the dataset.
    total_chunks : int | None
        Total number of document chunks in the dataset.
    corpus_types : str
        Comma-separated list of corpus types included.
    embedding_dim : int | None
        Dimensionality of the embedding vectors, if present.
    license_id : str
        SPDX license identifier. Defaults to ``"mit"``.
    year : int | None
        Publication year. Defaults to current year.
    tags : list[str] | None
        Additional tags for the YAML frontmatter.

    Returns
    -------
    str
        The complete dataset card content (YAML + markdown).
    """
    if year is None:
        year = datetime.date.today().year

    total_chunks_str = f"{total_chunks:,}" if total_chunks is not None else "N/A"

    embedding_dim_str = str(embedding_dim) if embedding_dim is not None else "N/A"

    tag_list = tags or ["nlp", "new-zealand", "legislation", "hansard", "parliament"]
    tags_yaml = "\n".join(f"  - {t}" for t in tag_list)

    yaml_frontmatter = (
        f"language:\n  - en\n  - mi\n"
        f"license: {license_id}\n"
        f"tags:\n{tags_yaml}\n"
        f"pretty_name: {title}\n"
        f"size_categories:\n  - 10K<n<100K\n"
    )

    return _DATASET_CARD_TEMPLATE.format(
        yaml_frontmatter=yaml_frontmatter,
        title=title,
        description=description,
        source=source,
        total_chunks=total_chunks_str,
        corpus_types=corpus_types,
        embedding_dim=embedding_dim_str,
        repo_id=repo_id,
        year=year,
    )


def write_dataset_card(
    path: str | Path,
    **kwargs: Any,
) -> Path:
    """Generate and write a dataset card to disk.

    Parameters
    ----------
    path : str | Path
        Destination file path (typically ``README.md`` in the Space or
        dataset directory).
    **kwargs
        All keyword arguments are forwarded to :func:`generate_dataset_card`.

    Returns
    -------
    Path
        The resolved path of the written file.
    """
    dest = Path(path).resolve()
    content = generate_dataset_card(**kwargs)
    dest.write_text(content, encoding="utf-8")
    return dest
