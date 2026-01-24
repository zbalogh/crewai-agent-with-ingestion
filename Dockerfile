FROM python:3.11-slim

WORKDIR /app

EXPOSE 7860

# Copy the requirements file first to leverage Docker layer caching
COPY requirements-libs.txt .

# Note: if you want to mount your external data/markdown directory, then you have to mount it to /app/data/markdown
# Example: docker run -v ./data/markdown:/app/data/markdown

RUN pip install --no-cache-dir -r requirements-libs.txt

# Copy all application files including the data/markdown directory
COPY . .

# we do not need data/website directory in the container
RUN rm -rf ./data/website

# we do not need the ".venv" directory in the container
RUN rm -rf ./.venv

# we do not need any .git directories in the container
RUN find . -type d -name ".git" -exec rm -r {}

# we do not need .env files in the container, delete it in the root
RUN find . -type f -name ".env" -exec rm {} \;

# we do not need any __pycache__ directories in the container
RUN find . -type d -name "__pycache__" -exec rm -r {}

# we do not need chromadb persistent database in the container
RUN rm -rf ./chromadb

# Set environment variables for Gradio server
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Important: Set Groq API Key environment variable when running the container
ENV GROQ_API_KEY=""

# Start the Gradio web application
CMD ["python", "web_app_gradio.py"]
