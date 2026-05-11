# EduNexus 🧠

EduNexus is a modern AI agent experiment demonstrating how to connect a **LangGraph** orchestration loop with a local **Model Context Protocol (MCP)** server. Powered by Google's Gemini, this project allows an AI agent to dynamically invoke local Python tools securely over standard input/output.

## 🚀 Features

- **LangGraph Orchestration**: Uses `create_react_agent` to manage the reasoning and tool-calling loop.
- **FastMCP Integration**: Exposes local Python functions (`get_weather`, `calculate_grade`) as AI tools securely without giving the LLM direct code execution access.
- **Google Gemini**: Uses `gemini-2.5-flash` for high-speed, accurate tool calling.
- **`uv` Package Management**: Blazing fast dependency resolution and execution.

## 🛠️ Setup

1. **Install dependencies** (assuming you have [uv](https://astral.sh/uv) installed):
   ```bash
   uv sync
   ```

2. **Environment Variables**:
   Create a `.env` file in the root directory and add your Google API Key:
   ```ini
   GOOGLE_API_KEY="your_api_key_here"
   ```

3. **Run the Agent**:
   ```bash
   python main.py
   ```

## 🏗️ Architecture

- `main.py`: The entry point. Connects to the MCP server, loads the tools, and executes the LangGraph agent.
- `mcp_bridge.py`: A custom utility that bridges the gap between the MCP specifications and LangChain's expected `StructuredTool` format with dynamic Pydantic schema generation.
- `mcp_server/server.py`: The FastMCP server containing the actual local tools the AI can use.