import ollama
from core.time_tool import tool as time_tool

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
    }
]

# Execution mapping: relates the tool's name from Ollama to the Python function
TOOL_REGISTRY = {
    "time": time_tool.execute
}


class OllamaService:

    def list_models(self):
        try:
            models_info = ollama.list()
            model_names = [model["name"] for model in models_info.get("models", [])]
            return {"models": model_names}
        except Exception as e:
            return {"models": [], "error": str(e)}

    def chat(self, model: str, messages: list, tools: list = None):
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
