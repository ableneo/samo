# based on https://gist.github.com/python273/563177b3ad5b9f74c0f8f3299ec13850

import json
import queue

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler


class ThreadedGenerator:
    def __init__(self):
        self.queue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        item = self.queue.get()
        if item is StopIteration:
            raise item
        return item

    def send(self, data):
        self.queue.put(data)

    def close(self):
        self.queue.put(StopIteration)


class ChainStreamHandler(StreamingStdOutCallbackHandler):
    def __init__(self, gen, history, log_path):
        super().__init__()
        self.gen = gen
        self.history = history
        self.log_path = log_path

    def on_llm_new_token(self, token: str, **kwargs):
        self.gen.send(token)

    def on_llm_end(self, response, **kwargs):
        self.history.append({"role": "assistant", "content": f"{response.generations[0][0].text}"})

        with open(self.log_path, "w") as log_file:
            json.dump(self.history, log_file)
