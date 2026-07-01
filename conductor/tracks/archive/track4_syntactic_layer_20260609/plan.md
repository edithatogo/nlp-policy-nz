# Plan: Track 4 Syntactic Parsing & Citation Extractor ✅

This track builds the spaCy syntactic layer with custom tokenizer integration, NZ legislation citation extraction via EntityRuler, and sentence-level document chunking.

---

### [x] Task 4.1: Scaffold spaCy Pipeline ✅
- **Action**: Build pipeline loader using the customized tokenizer from Track 3's Māori Language Guard.
- **Completed**: Created `pipeline.py` with `create_nlp_pipeline()` integrating Maori Guard component.

### [x] Task 4.2: Implement EntityRuler Regex Matchers ✅
- **Action**: Configure patterns to extract NZ Act titles and cross-references.
- **Completed**: Created `citations.py` with 5 token-based patterns and `create_citation_ruler()` factory.

### [x] Task 4.3: Implement Document Chunking ✅
- **Action**: Write sentence-level splitting logic with unique document identifiers (`doc_id`).
- **Completed**: Created `chunking.py` with ID generation and sentence chunking for legislation and Hansard.

---
