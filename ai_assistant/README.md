# Adbri Construction Intelligence Assistant

This project applies three AI skills to the existing Adbri BI portfolio:

1. RAG retrieves evidence from project reports, SQL, and documentation.
2. LangChain orchestrates loading, splitting, retrieval, prompting, and tools.
3. LoRA later fine-tunes an open-source model's response style and workflow.

## Learning Sequence

### Phase 1: Retrieval without an LLM

- Load DOCX, Markdown, and SQL files.
- Split them into searchable chunks.
- Create local embeddings and a FAISS index.
- Test whether relevant evidence is retrieved.

### Phase 2: Basic RAG

- Add an LLM.
- Require answers to use retrieved context.
- Return source file names with every answer.
- Refuse unsupported claims.

### Phase 3: LangChain application

- Replace manual orchestration with LangChain components.
- Add conversational history.
- Add metadata filters.
- Add a SQL tool for precise numeric questions.

### Phase 4: Evaluation

- Create a fixed question-and-answer evaluation set.
- Measure retrieval hit rate and answer faithfulness.
- Compare chunk sizes and retrieval settings.

### Phase 5: LoRA

- Prepare instruction-response examples.
- Fine-tune a small open-source model with PEFT/LoRA.
- Compare Base, RAG, LoRA, and RAG + LoRA.

## Knowledge Sources

The first knowledge base uses:

- `../docs/Adbri_Market_Demand_BI_Research_Report_EN.docx`
- `../docs/Adbri_Market_Demand_BI_Research_Report_CN.docx`
- `../docs/data_dictionary.md`
- `../databricks/01_bronze_ingest.sql`
- `../databricks/02_silver_gold_model.sql`
- `../databricks/03_quality_checks.sql`
- `../powerbi/power_bi_model_and_dax.md`
- `../README.md`

CSV fact data is intentionally excluded from the first vector index. Precise
numeric questions will later use a structured-data or SQL tool.
