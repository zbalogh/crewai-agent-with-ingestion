# Customer Support AI Agent (with ingestion)

CrewAI-based RAG agent with:
- Groq LLM provider
- LiteLLM for efficient LLM access
- Local SentenceTransformer embeddings
- ChromaDB vector database
- Automatic ingestion on startup


## Requirements
```
crewai==1.7.2
crewai-tools
chromadb
sentence-transformers
litellm
litellm[proxy]
groq
fastapi
python-dotenv
gradio==4.44.0
beautifulsoup4==4.12.3
markdownify==0.11.6
lxml==5.1.0
```


## Setup
```bash
# create python virtual environment (venv)
py -m venv .venv

# allow temporary script execution for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# activate the venv
& .\.venv\Scripts\Activate.ps1

# install the requirements
python -m pip install -r requirements-libs.txt
```

## HTML to Markdown Conversion

Convert website HTML files to clean Markdown format:

```bash
# Install required packages first
python -m pip install beautifulsoup4 markdownify lxml

# Convert with default settings (data/website -> data/markdown)
python html_to_markdown.py

# Custom input/output directories
python html_to_markdown.py --input data/website --output data/markdown

# Clean output directory before conversion
python html_to_markdown.py --clean

# Quiet mode (only show summary)
python html_to_markdown.py --quiet

# Flatten directory structure
python html_to_markdown.py --no-preserve-structure

# See all options
python html_to_markdown.py --help
```

## Run AI Assistant

Add your GROQ_API_KEY or OPENAI_API_KEY to .env file:

```
GROQ_API_KEY=<YOUR-API-KEY>
LITELLM_LOG=WARNING
```

OR

```
OPENAI_API_KEY=<YOUR-API-KEY>
LITELLM_LOG=WARNING
```

### CLI Mode
```bash
python app.py
```

### Web UI Mode (Gradio)
```bash
python web_app_gradio.py
```

### Web UI Access
The web interface will launch on http://localhost:7860

## To create a requirements.txt that records exact versions
```bash
python -m pip freeze > requirements.txt
```

## Optionally, install additional dependencies if required by LiteLLM
```bash
python -m pip install apscheduler email-validator fastapi uvicorn
python -m pip install 'litellm[proxy]'
```
