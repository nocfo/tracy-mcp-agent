# NOCFO MCP Project

This project is an AI-powered assistant designed to provide actionable financial insights and guidance for small to medium businesses. It leverages Large Language Models (LLMs) to understand user queries, orchestrate a suite of financial tools, and deliver responses through a user-friendly chat interface.

The system can access and analyze internal financial data, pull contextual information from public databases, and even forecast financial trends using time-series models.

## Core Features

- **Conversational UI**: An interactive chat interface built with Streamlit for easy user interaction.
- **Secure Data Access**: Utilizes JWT authentication to ensure users can only access their own company's internal financial data.
- **Public Data Integration**: Connects to the YTJ public database to fetch details, industry peers, and partners for any company.
- **AI-Powered Analysis**: An LLM-driven agent that can perform financial health checks, compare forecasts with historical data, and summarize key insights.
- **Financial Forecasting**: Integrates the Hugging Face Chronos model to predict future trends of key financial metrics.

## Project Architecture

The project follows a modular, four-part architecture:

1.  **🤖 AI Agent (`agent_api.py`)**: A FastAPI backend that serves as the brain of the operation. It receives user queries, interprets them using a "Virtual CFO" prompt, and decides which tools to use. It enforces all security and access rules.

2.  **🖥️ Frontend UI (`streamlit_agent_ui.py`)**: A user-facing chat application built with Streamlit. It handles user login simulation, maintains chat history, and communicates with the AI Agent API.

3.  **🛠️ MCP Server (`server.py`)**: The central tool hub. It exposes all backend functionalities (like retrieving financial data or running forecasts) as tools that the AI Agent can call. It's responsible for executing these tools and returning the results.

4.  **🔌 Adapters (`adapters/`)**: A collection of modules that connect the system to various data sources, including internal JSON data (`NOCFOAdapter.py`) and external public APIs (`YTJAdapter.py`).

## Getting Started

Follow these steps to set up and run the project locally using `uv`.

### Prerequisites

- [uv](https://github.com/astral-sh/uv) (a fast Python package installer and resolver)
- Python 3.9+

### 1. Installation

First, clone the repository to your local machine:
```bash
git clone https://github.com/tracyshen2678/tracy-mcp-agent.git
cd tracy-mcp-agent
```

Next, create a virtual environment and install the dependencies using `uv`. The dependencies are defined in the `pyproject.toml` file.

```bash
# Create and activate a virtual environment named .venv
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .\.venv\Scripts\activate

# Install all required packages from pyproject.toml
# This command will also use uv.lock to ensure consistent versions.
uv pip sync
```

**Note:** The `uv pip sync` command is the recommended way to install dependencies as it ensures your environment matches the `uv.lock` file exactly. If `uv.lock` is not present or you want to install directly from `pyproject.toml`, you can use `uv pip install -e .`.

### 2. Configuration (Environment Variables)

This project requires API keys to be set as environment variables. Before running the application, you must export them in your terminal session.

**Open a new terminal and export the following variables:**

```bash
# Replace with your actual OpenAI API key
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```
**Important:** These variables are only active for the current terminal session. If you open a new terminal, you will need to set them again.

### 3. Running the Application

The application consists of three main components that need to be run **in separate terminal windows**. Make sure you have activated the virtual environment (`source .venv/bin/activate`) in each terminal.

**Terminal 1: Start the MCP Server**

This server exposes the tools to the AI agent.
```bash
uv run python server.py
```

**Terminal 2: Start the Agent API**

This is the FastAPI backend that the frontend will talk to. Use `uv` to run `uvicorn`.
```bash
uv run uvicorn agent_api:app --host 0.0.0.0 --port 8001 --reload
```
The server will be running at `http://localhost:8001`.

**Terminal 3: Launch the Streamlit UI**

This is the user interface you will interact with.
```bash
uv run streamlit run streamlit_agent_ui.py
```
A new tab should automatically open in your web browser with the chat application. If not, open your browser and navigate to the URL provided in the terminal (usually `http://localhost:8501`).

You are now ready to use the Virtual CFO AI Agent! Log in via the sidebar in the UI and start asking questions.

