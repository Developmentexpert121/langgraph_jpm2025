from graph.workflow import rag_app

QUESTIONS = {
    "Q1": """According to Outlook 2025:
Which equity market themes were expected to perform well in 2025?
Which specific stocks or groups of stocks were highlighted?""",

    "Q2": """According to Mid-Year Outlook 2025:
Which forecasted themes played out as expected?
Which underperformed or disappointed?""",

    "Q3": """Identify at least two named stocks such as Apple, Microsoft, or NVIDIA.
What was stated about them in the 2025 forecast?
How are they described at mid-year 2025?""",

    "Q4": """What valuation or risk concerns were highlighted at the start of 2025?
Which of those risks materialized by mid-year, according to J.P. Morgan?""",

    "Q5": """Produce a table with the following columns:
| Stock / Theme | 2025 Forecast View | Mid-Year 2025 Reality | Supported? (Yes/No) | Citation |
Use only information explicitly stated in the documents."""
}


def run():
    print("\nJ.P. Morgan 2025 Forecast vs Mid-Year Reality\n")
    print("=" * 90)

    for qid, question in QUESTIONS.items():
        print(f"\n{qid}")
        print("-" * 90)
        result = rag_app.invoke({"question": question})
        print(result["answer"])
        print("\n" + "=" * 90)


if __name__ == "__main__":
    run()
