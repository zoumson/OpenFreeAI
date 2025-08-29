from pathlib import Path
from server.managers.resource_manager import ResourceManager

class ConversationManager:
    def __init__(self, file_path=None):
        self.history = []
        self.file_path = Path(file_path) if file_path else None

        if self.file_path and self.file_path.exists():
            self.load_from_file(self.file_path)

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        if self.file_path:
            self.export_to_file(self.file_path)

    def get_history(self):
        return self.history

    def reset(self):
        self.history = []
        if self.file_path:
            self.export_to_file(self.file_path)

    def export_to_file(self, file_path=None):
        path = Path(file_path or self.file_path)
        if not path:
            raise ValueError("No file path provided for export")
        ResourceManager.save_json(path, self.history)
        return path

    def load_from_file(self, file_path=None):
        path = Path(file_path or self.file_path)
        if not path or not path.exists():
            raise FileNotFoundError(f"Conversation file not found: {path}")
        self.history = ResourceManager.load_json(path)
        return self.history
