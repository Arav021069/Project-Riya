import os
from langchain_core.tools import tool


@tool
def create_directory(directory_name: str):
    """
    Creates a new directory on the local file system.
    Use this when the user asks to 'make a folder' or 'create a directory'.
    """
    try:
        os.makedirs(directory_name, exist_ok=True)
        return f"Successfully created directory: {directory_name}"
    except Exception as e:
        return f"Failed to create directory: {str(e)}"
