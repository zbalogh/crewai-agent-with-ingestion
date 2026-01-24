import os
from crewai import Agent, LLM
from rag.search import support_manual_search


# Initialize the LLM with Groq API using GPT-Oss-20B model
#llm = LLM(
#    provider="openai",
#    model="openai/gpt-oss-20b",
#    api_key=os.environ["GROQ_API_KEY"],
#    base_url="https://api.groq.com/openai/v1",
#    temperature=0.1,
#)

# Initialize the LLM with Groq's Llama 3.1 8B Instant model
llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=10000,  # Limit tokens per request
    temperature=0.1,
)

support_agent = Agent(
    role="Senior Customer Support Agent",
    goal=(
        "Provide accurate, customer-friendly answers to customer support questions "
        "strictly based on the official company manual content returned by the search tool. "
        "Always include sources if available."
    ),
    backstory=(
        "You are a senior customer support specialist who follows a strict support process: "
        "search the official manual, extract only relevant facts, and respond with clear answers "
        "and cited sources. You never guess or invent details."
    ),
    tools=[support_manual_search],
    llm=llm,
    verbose=False,
)
