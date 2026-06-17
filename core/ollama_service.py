import ollama


class OllamaService:

    def list_models(self):
        return ollama.list()

    def chat(self, model, messages):
        return ollama.chat(
            model=model,
            messages=messages
        )

    def pull_model(self, model):
        return ollama.pull(model)

    def delete_model(self, model):
        return ollama.delete(model)
    