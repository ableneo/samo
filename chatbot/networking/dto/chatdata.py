from typing import List, Optional

from jsonpickle import json
from lxml import etree

from chatbot.core import SerializableInterface
from chatbot.utils.fn import create_xml_element


class ChatData(SerializableInterface):
    chat_history: Optional[List[dict[str, str]]]
    chat_id: str
    question: str
    feedback: str
    answer: str
    reporter: str

    def __init__(self):
        self.chat_history = None

    def serialize(self) -> str:
        return json.encode(self)

    def serialize_history(self):
        return json.encode(self.chat_history)

    def deserialize(self, data: str):
        json_data = json.decode(data)
        self.chat_id = json_data["chat_id"]
        if "chat_history" in json_data:
            self.chat_history = json_data["chat_history"]
        if "question" in json_data:
            self.question = json_data["question"]
        if "feedback" in json_data:
            self.feedback = json_data["feedback"]
        if "answer" in json_data:
            self.answer = json_data["answer"]
        if "reporter" in json_data:
            self.reporter = json_data["reporter"]

    def to_xml(self) -> str:
        """Return XML representation of self."""
        root = etree.Element('data')
        for key, val in vars(self).items():
            if isinstance(val, list):
                sub_root = etree.Element(key, {'type': 'array'})
                for txt in val:
                    elem = create_xml_element('value', txt)
                    sub_root.append(elem)
                root.append(sub_root)
            else:
                elem = create_xml_element(key, val)
                root.append(elem)
        return etree.tostring(root, encoding='utf-8', pretty_print=True).decode()
