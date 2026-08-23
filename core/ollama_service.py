import ollama
from core.time_tool import tool as time_tool
from core.web_service import web_service

# Define tool specs for Ollama's function calling interface
OLLAMA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "time",
            "description": "Retrieves the current local system time (e.g. 10:15 PM). Use this whenever the user asks for the current time.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet for real-time information or specific URLs",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query to look up"},
                },
                "required": ["query"],
            },
        },
    }
]

def web_search(query: str):
    """Search the web and return a summary of findings."""

    # 1. Get search results
    search_results = web_service.search(query)
    if not search_results:
        return "No results found."

    # 2. Scrape the top 2 most relevant pages for a deeper context
    full_context = []
    for result in search_results[:2]:
        print(f"Browsing: {result['url']}")
        page_text = web_service.scrape(result['url'])
        full_context.append(f"Source: {result['url']}\nContent: {page_text}")

        return "\n\n---\n\n".join(full_context)

# Execution mapping: relates the tool's name from Ollama to the Python function
TOOL_REGISTRY = {
    "time": time_tool.execute,
    "web_search": web_search,
}


class OllamaService:

    def list_models(self):
        try:
            models_info = ollama.list()
            model_names = [model["name"] for model in models_info.get("models", [])]
            return {"models": model_names}
        except Exception as e:
            return {"models": [], "error": str(e)}

    def chat(self, model: str, messages: list, tools: list | None = None):
        """Sends messages to Ollama, optionally providing tools for function calling."""
        chat_args = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {
                "num_ctx": 4096,
                "temperature": 0.5,
            }
        }
        # Only add tools parameter if tools list is provided
        if tools:
            chat_args["tools"] = tools

        return ollama.chat(**chat_args)

    def pull_model(self, model: str):
        return ollama.pull(model)

    def delete_model(self, model: str):
        return ollama.delete(model)

    def get_model_info(self, model: str):
        """Retrieves details of a specific model from
          Ollama."""
        info = ollama.show(model)

        info_dict = info.model_dump() if hasattr(info, "model_dump") else dict(info)

        return {
            "model_name": model,
            "details": info_dict
        }
