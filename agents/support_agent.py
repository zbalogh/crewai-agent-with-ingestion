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

# if there is GROQ_API_KEY in the environment, use Groq LLM
if os.getenv("GROQ_API_KEY"):
    print(f"🔄 Using Groq LLM with {os.getenv('GROQ_MODEL', 'groq/llama-3.1-8b-instant')} model.")
    llm = LLM(
        model=os.getenv("GROQ_MODEL", "groq/llama-3.1-8b-instant"),
        api_key=os.getenv("GROQ_API_KEY"),
        max_tokens=int(os.getenv("GROQ_MAX_TOKENS", 1500)),  # Limit tokens per request
        temperature=float(os.getenv("GROQ_TEMPERATURE", 0.2)), # Adjust temperature for more focused responses
        top_p=0.9,  # Use nucleus sampling for more coherent responses
    )

# if there is OPENAI_API_KEY in the environment, use OpenAI LLM
elif os.getenv("OPENAI_API_KEY"):
    print(f"🔄 Using OpenAI LLM with {os.getenv('OPENAI_MODEL', 'openai/gpt-4o-mini')} model.")
    llm = LLM(
        model=os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", 1500)),  # Limit tokens per request
        temperature=float(os.getenv("OPENAI_TEMPERATURE", 0.2)), # Adjust temperature for more focused responses
        top_p=0.9,  # Use nucleus sampling for more coherent responses
    )

# if no API key is found, raise an error: exit with an error message an non-zero exit code
else:
    print("❌ Error: No API key found for Groq or OpenAI. Please set GROQ_API_KEY or OPENAI_API_KEY in the environment.", file=sys.stderr)
    sys.exit(1)


# Create the support agent with the defined role, goal, backstory, tools, and LLM.
# The agent is designed to provide accurate and customer-friendly answers to support questions
# based on the official company manual content returned by the search tool.
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
