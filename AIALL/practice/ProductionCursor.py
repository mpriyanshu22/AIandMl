import os
import subprocess
import json

class ProductionCursor:
    """
    A more robust, modular version of the autonomous coding assistant.
    Features:
    - Enhanced command execution with error handling.
    - File system management.
    - Context-aware logging.
    """
    
    def __init__(self, workspace_path="."):
        self.workspace_path = workspace_path
        self.history = []

    def run_command(self, command):
        """Executes a shell command and returns the output."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, cwd=self.workspace_path
            )
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            return result.stdout
        except Exception as e:
            return f"Execution failed: {str(e)}"

    def read_file(self, filepath):
        """Reads content from a file."""
        try:
            with open(os.path.join(self.workspace_path, filepath), 'r') as f:
                return f.read()
        except Exception as e:
            return f"Could not read file: {str(e)}"

    def write_file(self, filepath, content):
        """Writes content to a file."""
        try:
            full_path = os.path.join(self.workspace_path, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {filepath}"
        except Exception as e:
            return f"Could not write file: {str(e)}"

    def list_files(self, path="."):
        """Lists files in the directory."""
        try:
            return os.listdir(os.path.join(self.workspace_path, path))
        except Exception as e:
            return f"Could not list directory: {str(e)}"

    def log_action(self, action, result):
        """Logs actions for traceability."""
        self.history.append({"action": action, "result": result})
        print(f"[LOG] {action}: {result[:50]}...")

if __name__ == "__main__":
    # Example usage
    agent = ProductionCursor()
    print("ProductionCursor initialized.")
    # agent.log_action("list_files", str(agent.list_files()))
