# ableneo-ChatBot: A RAG-based ChatBot

![Python Version](https://shields.io/badge/python-3.11%20-blue)
[![Apache 2 License](https://img.shields.io/badge/license-Apache%202-brightgreen.svg?style=flat&logo=apachet)](https://github.com/ableneo/chat-beckend/blob/master/LICENSE.txt)
[![Account X](https://img.shields.io/twitter/follow/ableneo?style=flat&labelColor=606060&logo=X&logoColor=white&link=https://twitter.com/ableneo1)](https://twitter.com/ableneo1)

## Installing

Clone the repository:

```shell
git clone https://github.com/ableneo/samo
```

Install Ableneo ChatBot Samo via:

```shell
pip install  .
```

## Launching the ChatBot Samo

For demonstration purposes, we have already prepared all the prerequisites.
The ChatBot is configured to serve as a helpful Biology assistant.
It utilizes information from biological pages on Wikipedia as its knowledge base (data were downloaded from https://commoncrawl.org/).
All responses will be in Slovak, so no additional translation is necessary.

### Running server

To run chatbot Samo server run::

1. Duplicate the `config.example.yaml` file
2. Fill in all placeholders in the config file
3. Run the following command::
   ```shell
   ableneo-chatbot server run --config-file <config.yaml>
   ```
4. Run the server

For more information, run:

```shell
ableneo-chatbot server --help
```

### Initialize Knowledge-Base

If you would like to use your data in your ChatBot system, follow these steps:

1. Remove the `./db` folder
2. Copy your `*.txt` data to the `./data` folder
3. Run the following command:
   ```shell
   ableneo-chatbot knowledge-base init --data-root './data' --data-type '.txt' --config-file './config.yaml' --encoding 'utf-8'
   ```

For more information, run::

```shell
ableneo-chatbot knowledge-base --help
```

## Endpoints

### `GET /health`

**Request**

```shell
curl -i --request GET 'http://127.0.0.1:6628/health'
```

<details>
  <summary>Response</summary>

   ```
   HTTP/1.1 200 OK
   Server: Werkzeug/3.0.3 Python/3.11.9
   Date: Thu, 06 Jun 2024 15:41:15 GMT
   Content-Type: text/html; charset=utf-8
   Content-Length: 2
   Access-Control-Allow-Origin: *
   Connection: close

   OK
   ```

</details>

### `GET /version`

**Request**

```shell
curl -i --request GET 'http://127.0.0.1:6628/version'
```

<details>
  <summary>Response</summary>

   ```
   HTTP/1.1 200 OK
   Server: Werkzeug/3.0.3 Python/3.11.9
   Date: Thu, 06 Jun 2024 15:41:48 GMT
   Content-Type: text/html; charset=utf-8
   Content-Length: 5
   Access-Control-Allow-Origin: *
   Connection: close

   0.1.1
   ```

</details>

### `POST /v1/chatbot/prompt`

**Request**

`GET /version`

```shell
curl -i --request POST 'http://127.0.0.1:6628/v1/chatbot/prompt' \
--header 'Content-Type: application/json' \
--data '{
    "chat_id": "abb99ff0-22ad-4992-ac54-997b95ebbc11",
    "chat_history": [],
    "question": "Koľko mláďat ročne má Myšiarka ušatá?"
}'
```

<details>
  <summary>Response</summary>

   ```
   HTTP/1.1 200 OK
   Server: Werkzeug/3.0.3 Python/3.11.9
   Date: Thu, 06 Jun 2024 16:12:54 GMT
   Content-Type: text/plain; charset=utf-8
   Access-Control-Allow-Origin: *
   Transfer-Encoding: chunked
   Connection: close

   Myšiarka ušatá (Asio otus) kladie 3 až 7 svetlých vajec ročne.

   Zdroj: <a href='data\\mysiarka_usata.txt'>data\\mysiarka_usata.txt</a>
   ```

</details>

### `POST /v1/chatbot/history`

**Request**

```shell
curl -i --request POST 'http://127.0.0.1:6628/v1/chatbot/history' \
--header 'Content-Type: application/json' \
--data '{"chat_id": "abb99ff0-22ad-4992-ac54-997b95ebbc11"}'
```

<details>
  <summary>Response</summary>

   ```
   HTTP/1.1 200 OK
   Server: Werkzeug/3.0.3 Python/3.11.9
   Date: Thu, 06 Jun 2024 16:14:26 GMT
   Content-Type: application/json
   Content-Length: 259
   Access-Control-Allow-Origin: *
   Connection: close

   [{"role": "user", "content": "Koľko mláďat ročne má Myšiarka ušatá?"}, {"role": "assistant", "content": "Myšiarka ušatá (Asio otus) kladie 3 až 7 svetlých vajec ročne. <a href='data\\mysiarka_usata.txt'>data\\mysiarka_usata.txt</a>"}]
   ```

</details>

### `POST /v1/chatbot/feedback`

**Request**

```shell
curl -i --request POST 'http://127.0.0.1:6628/v1/chatbot/feedback' \
--header 'Content-Type: application/json' \
--data '{
    "chat_id": "abb99ff0-22ad-4992-ac54-997b95ebbc11",
    "chat_history": [],
    "question": "Koľko mláďat ročne má Myšiarka ušatá?",
    "feedback": "Správne",
    "answer": "Myšiarka ušatá (Asio otus) kladie 3 až 7 svetlých vajec ročne. <a href='\''data\\mysiarka_usata.txt'\''>data\\mysiarka_usata.txt</a>",
    "reporter": "učiteľ"
}'
```

<details>
  <summary>Response</summary>

   ```shell
   HTTP/1.1 200 OK
   Server: Werkzeug/3.0.3 Python/3.11.9
   Date: Thu, 06 Jun 2024 16:21:00 GMT
   Content-Type: application/json
   Content-Length: 22
   Access-Control-Allow-Origin: *
   Connection: close

   {"message": "success"}
   ```

</details>

## Development

If you would like to customize the source code, you can install all development dependencies via:

```shell
pip install -e .[dev]
```

## About Ableneo

### Read our blog

- [https://medium.com/ableneo](https://medium.com/ableneo)
- [https://www.ableneo.com/blog](https://www.ableneo.com/blog)

### Our website

[https://www.ableneo.com](https://www.ableneo.com)

### Contact

For more information, contact:

- [info@ableneo.com](mailto:info@ableneo.com)
- +421 2 32 144 791
