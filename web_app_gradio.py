"""
Customer Support AI Assistant - Gradio Web Interface

This module provides a web-based UI for the customer support assistant
using Gradio. It allows users to ask questions about company products through
a simple browser interface.

Usage:
    python web_app_gradio.py

The app will launch on http://localhost:7860
"""

import bootstrap_litellm

from dotenv import load_dotenv
import gradio as gr
from rag.ingest import ingest_if_needed
from agents.support_agent import support_agent
from crewai import Task, Crew
import time


# Load environment variables
load_dotenv()

# Ensure vector DB is populated on startup
print("🔄 Initializing Customer Support AI Assistant...")
ingest_if_needed()
print("✅ Vector database ready!")


def ask_customer_support(question: str, history: list = None) -> str:
    """
    Process user question and return answer from Customer Support agent.
    
    Args:
        question: User's question about company products
        history: Conversation history (optional, for future chat interface)
    
    Returns:
        Answer from the AI agent
    """
    if not question or not question.strip():
        return "⚠️ Please enter a question."
    
    try:
        print(f"\n📝 Processing question: {question}")
        start_time = time.time()
        
        # Create task for the support agent
        task = Task(
            description=(
                "You are a customer support assistant.\n\n"
                "Answer the user's question strictly based on the company manual content "
                "returned by the available tools. The manual is the primary source of truth.\n\n"
                f"User question:\n{question}\n\n"
                "Rules and guidelines:\n"
                "- Use ONLY information explicitly stated in the company manual.\n"
                "- Do NOT invent or assume missing details. DO NOT hallucinate and generate false information.\n"
                "- Extract and summarize only the relevant information.\n"
                "- If the manual does not contain sufficient information, clearly state that.\n"
                "- Keep the response clear, professional, and customer-friendly.\n"
            ),
            agent=support_agent,
            expected_output=(
                "Answer with sources. Return a customer-friendly answer in well-structured Markdown. Please be concise yet informative.\n\n"
                "Do NOT include internal thoughts, reasoning steps, or labels such as "
                "\"Thought:\", \"Action:\", or \"Observation:\".\n"
                "Include references to the relevant parts of the company manual where appropriate.\n"
            ),
        )

        # Create and execute crew
        crew = Crew(
            agents=[support_agent],
            tasks=[task],
        )

        result = crew.kickoff()
        
        elapsed_time = time.time() - start_time
        print(f"✅ Answer generated in {elapsed_time:.2f} seconds")
        
        return str(result)

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(error_msg)
        return error_msg


# Example questions for quick testing
EXAMPLE_QUESTIONS = [
    ["How can I configure Users?"],
    ["How can I configure Roles and Permissions?"],
    ["List all Service URLs which are available in company software. Please summarise them in a table."],
    ["How can I perform a software update on my application server?"],
]


# Create Gradio interface with custom styling
with gr.Blocks(
    title="🔧 Customer Support AI Assistant",
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="purple",
    ),
    css="""
    #support-examples table,
    #support-examples .gr-examples-table,
    #support-examples .grid-wrap {
        width: 100% !important;
        justify-content: flex-start !important;
    }

    #support-examples td,
    #support-examples button,
    #support-examples .gr-button,
    #support-examples .example,
    #support-examples .gr-example {
        text-align: left !important;
        justify-content: flex-start !important;
    }
    """,
) as demo:
    
    gr.Markdown(
        """
        # 🔧 Customer Support AI Assistant
        
        Ask questions about company products, technical specifications, configuration, troubleshooting, and more.
        The assistant uses AI and official product documentation to provide accurate answers.
        
        **Note:** Responses may take 10-30 seconds as the AI agent searches and processes information.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            # Input section
            question_input = gr.Textbox(
                label="Your Question",
                placeholder="e.g., How do I troubleshoot my company device?",
                lines=3,
                max_lines=5,
            )
            
            with gr.Row():
                submit_btn = gr.Button("🔍 Ask Assistant", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ Clear", size="lg")
            
            # Output section
            answer_output = gr.Markdown(
                label="Answer",
                value="",
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### 📝 Example Questions")
            gr.Markdown("Click any example to try it:")
            
            examples = gr.Examples(
                examples=EXAMPLE_QUESTIONS,
                inputs=question_input,
                label=None,
                elem_id="support-examples",
            )
            
            gr.Markdown(
                """
                ---
                ### 💡 Tips
                - Be specific in your questions
                - Ask about products, technical specs, or troubleshooting
                - Wait for complete response (10-30s)
                
                ### ℹ️ About
                This assistant uses:
                - **CrewAI** for intelligent agents
                - **LiteLLM** for efficient LLM access
                - **RAG** with ChromaDB for documentation search
                - **Groq** LLM provider for natural responses
                """
            )
    
    # Event handlers
    submit_btn.click(
        fn=ask_customer_support,
        inputs=[question_input],
        outputs=[answer_output],
    )
    
    question_input.submit(
        fn=ask_customer_support,
        inputs=[question_input],
        outputs=[answer_output],
    )
    
    clear_btn.click(
        fn=lambda: ("", ""),
        inputs=None,
        outputs=[question_input, answer_output],
    )


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Customer Support AI Assistant Web Interface")
    print("="*60)
    
    demo.launch(
        server_name="0.0.0.0",  # Allow external connections
        server_port=7860,        # Default Gradio port
        share=False,             # Set to True to create public link
        show_error=True,         # Show detailed errors in UI
        quiet=False,             # Show server logs
    )
