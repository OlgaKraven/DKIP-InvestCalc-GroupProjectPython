import json
from pathlib import Path

class JsonStorage:
    def __init__(self, path: str):
        self.path = Path(path)
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data):
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
