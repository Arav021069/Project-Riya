from typing import Generator
from app.services.session_service import SessionService
from core.ollama_service import OllamaService, OLLAMA_TOOLS, TOOL_REGISTRY

class ChatService:
    def __init__(self):
        self.ollama = OllamaService()
        self.session_service = SessionService()

    def stream_chat(self, user_message: str, session_id: str, selected_model: str) -> Generator[str, None, None]:
        """
        Orchestrates the chat flow: 
        1. Retrieves history 
        2. Initial LLM call 
        3. Tool execution loop (if needed) 
        4. Final response generation
        """
        full_response = ""
        try:
            # Fetch history from DB for context via SessionService
            history_messages = self.session_service.get_session_history(session_id)

            # Step 1: Call Ollama with tools enabled
            stream = self.ollama.chat(selected_model, history_messages, tools=OLLAMA_TOOLS)

            tool_calls_to_execute = []

            for chunk in stream:
                message = chunk.get("message", {})
                
                # Capture tool calls requested by the model
                if "tool_calls" in message and message["tool_calls"]:
                    tool_calls_to_execute.extend(message["tool_calls"])
                
                content = message.get("content", "")
                if content:
                    full_response += content
                    yield content

            # Step 2: If the model decided to execute one or more tools
            if tool_calls_to_execute:
                assistant_tool_msg = {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": tool_calls_to_execute
                }

                tool_messages = []
                for tool_call in tool_calls_to_execute:
                    func_info = tool_call.get("function", {})
                    func_name = func_info.get("name")
                    func_args = func_info.get("arguments", {})

                    if func_name in TOOL_REGISTRY:
                        try:
                            if func_name == "time":
                                result = TOOL_REGISTRY[func_name]()
                            else:
                                result = TOOL_REGISTRY[func_name](**func_args)
                        except Exception as e:
                            result = f"Error executing tool {func_name}: {str(e)}"
                    else:
                        result = f"Error: Tool '{func_name}' is not registered."

                    tool_messages.append({
                        "role": "tool",
                        "content": str(result),
                        "name": func_name
                    })

                # Combine history, assistant tool request, and tool execution results
                updated_messages = history_messages + [assistant_tool_msg] + tool_messages

                # Step 3: Run the second completion to get the final text response
                final_stream = self.ollama.chat(selected_model, updated_messages)
                for chunk in final_stream:
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        full_response += content
                        yield content

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"SERVICE ERROR: {error_msg}")
            yield error_msg
            full_response = error_msg

        finally:
            if full_response.strip():
                # Save only the final resolved assistant response to DB via SessionService
                self.session_service.save_message(session_id, "assistant", full_response)
