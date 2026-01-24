import bootstrap_litellm

from dotenv import load_dotenv
from rag.ingest import ingest_if_needed
from agents.support_agent import support_agent
from crewai import Task, Crew


# load ".env" environment file
load_dotenv()

# Ensure vector DB is populated
ingest_if_needed()

question = input("Ask customer support question: ")

task = Task(
    description=f"Answer this question using the company's manual if needed:\n{question}",
    agent=support_agent,
    expected_output="Answer with sources. Format your answer in a well-structured Markdown.",
)

crew = Crew(
    agents=[support_agent],
    tasks=[task],
)

result = crew.kickoff()
print(result)
