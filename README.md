```markdown
# LangGraph RAG – JPMorgan 2025 Forecast vs Mid-Year Reality

This project implements a **LangGraph-based Retrieval-Augmented Generation (RAG)** system to analyze and compare **J.P. Morgan’s 2025 Outlook forecast** against the **Mid-Year 2025 Reality** report.

The system retrieves grounded evidence from provided documents and produces **faithful, citation-backed answers**, with a clear separation between *forecasted views* and *mid-year outcomes*.

## Deliverables Covered

1. LangGraph code for orchestration and RAG workflow
2. Answers to all evaluation questions (included below)
3. Explanation of technology choices, chunking, ranking, and retrieval strategy
4. This README explaining setup, design decisions, and limitations

## Project Structure

```
langgraph_jpm2025/
│
├── graph/
│   ├── run_all_questions.py      # Executes all evaluation questions
│   ├── workflow.py               # LangGraph workflow definition
│
├── ingestion/
│   ├── chunker.py                # PDF chunking logic
│   ├── pdf_loader.py             # PDF processing / ingestion
│
├── retrieval/
│   └── retriever.py              # Retrieval and ranking logic
│
├── data/
│   ├── images/                   # Any reference images
│   ├── processed/                # Processed data, embeddings
│   └── raw/                      # Raw PDFs / documents
│
├── storage/
│   └── chunks.json               # Persisted chunks (generated)
│
├── requirements.txt
├── .env.example
└── README.md
```

## Environment Setup

### Prerequisites

*   Python 3.10+
*   Git
*   OpenAI API key

### macOS / Linux Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set environment variable:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Verify:

```bash
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Windows Setup (PowerShell)

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Set environment variable:

```powershell
setx OPENAI_API_KEY "your_api_key_here"
```

Restart the terminal, then verify:

```powershell
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

## Document Ingestion and Chunking

Before running the question-answering workflow, the PDFs must be **processed and chunked**.

### Step 1: Process PDFs

This step:

*   Loads PDF files from `data/raw/`
*   Extracts text
*   Normalizes whitespace and page boundaries
*   Attaches document metadata (source, page numbers)

```bash
python -m ingestion.pdf_loader \
  --input data/raw/outlook_2025.pdf data/raw/midyear_2025.pdf \
  --output data/processed/raw_docs.json
```

### Step 2: Create Chunks

This step:

*   Splits documents into semantically coherent chunks
*   Preserves section and page references
*   Applies overlap to maintain context continuity

```bash
python -m ingestion.chunker \
  --input data/processed/raw_docs.json \
  --output storage/chunks.json \
  --chunk-size 600 \
  --overlap 100
```

Chunking defaults:

*   Chunk size: 500–700 tokens
*   Overlap: ~15%
*   Chunked by semantic boundaries (paragraphs/sections)

## Running the RAG Workflow

Once chunks are generated, run all evaluation questions:

```bash
python -m graph.run_all_questions
```

Purpose:

*   Retrieves top-ranked chunks per question
*   Separates forecast vs mid-year context
*   Generates grounded answers
*   Outputs citations and structured comparisons

### Running the LangGraph RAG CLI

```bash
python -m graph.workflow
```

**Example Usage:**

```
JPM Outlook LangGraph RAG
Type your question and press Enter.
Type 'exit' anytime to quit.

Question: According to Outlook 2025, which equity market themes were expected to perform well in 2025? Which specific stocks or groups of stocks were highlighted?
Thinking...

Answer:
According to the Outlook 2025 report, the following major equity market themes were expected to perform well in 2025:

1. Easing Global Policy (Pages 7-7)
2. Accelerating Capital Investment (Pages 7-7)
3. Understanding Election Impacts (Pages 7-7)
4. Renewing Portfolio Resilience (Pages 7-7)
5. Evolving Investment Landscapes (Pages 7-7)

Specific stocks/groups:
- U.S. Large-Cap Stocks (Pages 12-12)
- Japanese Corporations (Pages 12-12)
- Emerging Markets: Taiwan, India, Indonesia, Mexico (Pages 12-12)
```

You can ask questions one by one, and the system will generate citation-grounded answers.

## Answers to Evaluation Questions

### Q1 – Forecasted Equity Themes (Outlook 2025)

According to the Outlook 2025 report, the following major equity market themes were expected to perform well in 2025:

1.  **Easing Global Policy**
    Global central banks were expected to cut rates, creating a supportive environment for economic growth and benefiting areas such as U.S. housing and European productivity.
    (Outlook 2025 | Pages 7–7)

2.  **Accelerating Capital Investment**
    Significant investments were forecast in artificial intelligence, power and energy, and security infrastructure, requiring substantial capital deployment.
    (Outlook 2025 | Pages 7–7)

3.  **Understanding Election Impacts**
    Election outcomes, particularly in the U.S., were expected to influence sovereign debt trajectories, fiscal policy, and taxation.
    (Outlook 2025 | Pages 7–7)

4.  **Renewing Portfolio Resilience**
    Investors were encouraged to focus on income generation and downside protection to withstand macroeconomic volatility.
    (Outlook 2025 | Pages 7–7)

5.  **Evolving Investment Landscapes**
    New opportunities such as evergreen alternatives, sports investing, and changing urban dynamics driven by work-life shifts were highlighted.
    (Outlook 2025 | Pages 7–7)

**Highlighted stocks / regions:**

*   U.S. large-cap stocks with stable margins and shareholder returns
*   Japanese corporations benefiting from improved governance
*   Emerging markets including India, Taiwan, Indonesia, and Mexico
    (Outlook 2025 | Pages 12–12)

### Q2 – Mid-Year Reality Check (2025)

**Themes that played out as expected:**

1.  Consumer spending remained resilient.
    (Mid-Year Outlook | Page 12)

2.  Labor markets continued to show strength.
    (Mid-Year Outlook | Page 34)

**Themes that disappointed or underperformed:**

1.  Economic growth was slower than initially anticipated.
    (Mid-Year Outlook | Page 13)

2.  Market volatility was higher than expected.
    (Mid-Year Outlook | Page 36)

### Q3 – Stock-Level Comparison

**Stocks discussed:** Microsoft and the “Magnificent 7”

**Forecast View (Start of 2025):**

*   **Microsoft**
    Expected to benefit strongly from AI-driven cloud demand, contributing nearly half of a 35% growth rate in its cloud business.
    (Mid-Year 2025 | Page 26)

*   **Magnificent 7**
    Projected to deliver 15% EPS growth versus 8% for the rest of the market.
    (Mid-Year 2025 | Page 14)

**Mid-Year 2025 Reality:**

*   **Microsoft**
    Confirmed as an AI leader with strong cloud growth driven by AI workloads.
    (Mid-Year 2025 | Page 26)

*   **Magnificent 7**
    Underperformed year-to-date due to capex concerns but retained strong earnings and attractive valuations.
    (Mid-Year 2025 | Page 14)

### Q4 – Valuation and Risk Assessment

**Risks highlighted at the start of 2025:**

*   Rising recession risks
*   U.S. policy uncertainty
*   Two-way risks to growth and inflation
    (Mid-Year Outlook | Pages 2–4)

**Risks realized by mid-year:**

*   Global growth showed signs of slowing
*   Policy uncertainty remained elevated
    (Mid-Year Outlook | Pages 2–3)

### Q5 – Forecast vs Reality Summary Table

| Stock / Theme                | 2025 Forecast View              | Mid-Year 2025 Reality               | Supported |
| :--------------------------- | :------------------------------ | :---------------------------------- | :-------- |
| Easing Global Policy         | Rate cuts expected to support growth | Inflation cooled, soft landing narrative | Yes       |
| Accelerating Capital Investment | Heavy AI and energy investment | Continued strong AI and energy investment | Yes       |
| Portfolio Resilience         | Focus on downside protection    | Volatility reinforced resilience need | Yes       |

## Technology Choices

*   **LangGraph**: Multi-step RAG reasoning
*   **OpenAI LLM**: Citation-aware answer generation
*   **PDF-first ingestion**: Answers grounded only in provided documents
*   **Structured prompts**: Enforce separation of forecast vs mid-year outcomes

## Chunking Strategy

*   Chunk size: ~500–700 tokens
*   Overlap: ~15%
*   Chunked along semantic boundaries

Benefits:

*   Higher retrieval precision
*   Faithful citations
*   Reduced hallucination risk

## Retrieval and Ranking

*   Hybrid keyword + semantic similarity
*   Top-k retrieval (k = 4)
*   Ranking prioritizes:
    *   Numeric claims
    *   Named entities
    *   Temporal indicators (forecast vs mid-year)

## Prompting Choices

*   Instructions to:
    *   Answer only from retrieved context
    *   Avoid speculation
    *   Return “not stated” if no evidence
*   Structured output for consistency

## Limitations and Future Improvements

**Current limitations:**

*   No contradiction resolution
*   No per-answer confidence score
*   Static question set

**Potential enhancements:**

*   Evidence-strength scoring
*   Cross-document contradiction detection
*   Interactive UI for Q&A exploration
*   Automated faithfulness evaluation

## Conclusion

This implementation prioritizes **retrieval correctness, citation discipline, and faithfulness**. Where evidence is insufficient, the system explicitly states so, aligning with evaluation expectations.
```