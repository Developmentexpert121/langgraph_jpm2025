import os
from typing import TypedDict, List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from langgraph.graph import StateGraph, END
from retrieval.retriever import load_chunks, build_chunk_embeddings, semantic_search

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chunks = load_chunks("data/processed/semantic_chunks.pkl")
build_chunk_embeddings(chunks)

class RAGState(TypedDict):
    question: str
    docs: List[str]
    retrieved_chunks: List[Dict]
    answer: str

def router_node(state: RAGState) -> RAGState:
    q = state["question"].lower()

    if q.startswith("according to mid-year outlook"):
        docs = ["outlook_2025", "midyear_2025"]
    elif q.startswith("produce a table"):
        docs = ["outlook_2025", "midyear_2025"]
    elif "mid-year" in q:
        docs = ["midyear_2025"]
    elif "forecast" in q or "outlook" in q:
        docs = ["outlook_2025"]
    else:
        docs = ["outlook_2025", "midyear_2025"]

    return {**state, "docs": docs}


def retrieval_node(state: RAGState) -> RAGState:
    filtered = [c for c in chunks if c["doc_name"] in state["docs"]]
    retrieved = semantic_search(filtered, state["question"], top_k=8)
    return {**state, "retrieved_chunks": retrieved}


def synthesis_node(state: RAGState) -> RAGState:
    question = state["question"]
    retrieved_chunks = state["retrieved_chunks"]

    context = ""
    for c in retrieved_chunks:
        context += (
            f"[{c['doc_name']} | {c['heading']} | "
            f"Pages {c['page_start']}-{c['page_end']}]\n"
            f"{c['text']}\n\n"
        )

    extra_rules = ""

    if question.startswith("According to Outlook 2025"):
        extra_rules = """
- Identify major equity themes.
- Group related statements into coherent themes.
- List specific stocks or stock groups explicitly mentioned.
"""

    elif question.startswith("According to Mid-Year Outlook 2025"):
        extra_rules = """
- Compare forecast expectations with mid-year outcomes.
- If mid-year language confirms strength or resilience, mark as "played out as expected".
- If it mentions underperformance, volatility, or concern, mark as "underperformed or disappointed".
- Do NOT say "Not stated" if comparative evidence exists across documents.
"""

    elif question.startswith("Identify at least two named stocks"):
        extra_rules = """
- Identify at least two explicitly named stocks.
- Describe their 2025 forecast view.
- Describe how they are discussed at mid-year.
"""

    elif question.startswith("What valuation or risk concerns"):
        extra_rules = """
- Identify risks mentioned at the start of 2025.
- Explicitly state which risks materialized by mid-year.
"""

    elif question.startswith("Produce a table"):
        extra_rules = """
- Produce a table with AT LEAST three rows.
- Each row must represent a stock or investment theme.
- Use both Outlook 2025 and Mid-Year 2025.
- "Supported = Yes" only if mid-year evidence confirms the forecast.
- "Supported = No" if it weakens or contradicts the forecast.
- Every row MUST have citations.
- Do NOT return a placeholder or empty table.
"""


    prompt = f"""
You are a financial research assistant.

GLOBAL RULES:
- Use ONLY the provided context.
- You MAY synthesize across multiple excerpts and pages.
- Do NOT introduce external knowledge.
- Every factual claim MUST include a citation (Document | Page X–Y).
- If evidence truly does not exist, say "Not stated in the documents".

QUESTION-SPECIFIC RULES:
{extra_rules}

Question:
{question}

Context:
{context}

Answer:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    return {**state, "answer": response.choices[0].message.content.strip()}

graph = StateGraph(RAGState)

graph.add_node("router", router_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("synthesis", synthesis_node)

graph.set_entry_point("router")
graph.add_edge("router", "retrieval")
graph.add_edge("retrieval", "synthesis")
graph.add_edge("synthesis", END)

rag_app = graph.compile()


if __name__ == "__main__":
    print("\nJPM Outlook LangGraph RAG\n")

    while True:
        question = input("Question: ").strip()
        if question.lower() in {"exit", "quit", "q"}:
            break

        print("\nThinking...\n")
        result = rag_app.invoke({"question": question})
        print(result["answer"])
        print("\n" + "-" * 90 + "\n")
