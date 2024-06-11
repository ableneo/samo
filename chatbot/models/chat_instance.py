from typing import List


class ChatInstance:
    chat_history: List[dict[str, str]]

    def __init__(self):
        self.chat_history = []

    def get_filtered_history(self) -> List[dict[str, str]]:
        return list(filter(lambda x: x.get("role") in ["user", "assistant"], self.chat_history))

    def get_answer_history_as_string(self) -> str:
        history_str = ""
        for history in self.get_filtered_history():
            history_str += f"{history.get('role')}: {history.get('content')}\n"
        return history_str
