from crewai.tools import tool
from rag.vectorstore import VectorStore

store = VectorStore()

@tool("support_manual_search")
def support_manual_search(query: str) -> str:
    """Search the company manual knowledge base for relevant information.
    
    Use this tool to find official company manual information about:
    - How to configure and use company products
    - Troubleshooting common issues
    - How to install and set up company software
    - How to configure company modules and features
    
    Args:
        query (str): A clear search query string describing what information you need.
                     Examples: "create group", "install company software", "configure Directory"
    
    Input JSON schema format (REQUIRED):
        {"query": "your search term"}
    
    Examples:
        {"query": "create group"}
        {"query": "install company software"}
        {"query": "configure Directory"}
    

    Returns:
        str: Relevant company manual content with source information, or an error message if no results found.
    """
    if not query or not query.strip():
        return "Tool usage error: missing search query."

    results = store.search(query)

    if not results.get("documents") or not results["documents"][0]:
        return "No relevant company manual information found."

    output = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        output.append(
            f"{doc}\nSource: {meta.get('url', meta.get('source', 'N/A'))}"
        )

    return "\n\n".join(output)
