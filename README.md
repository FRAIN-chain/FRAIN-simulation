# LoRA integrated GPT-J-6B Server

Request inference and training to LoRA integrated GPT-J-6B.

Chat (Human ↔️ BRAIN)

## Default Settings
- r=1
- float16
- cuda

# How to Use

## Run Chatbot

```bash
$ CUDA_VISIBLE_DEVICES=0,1 \
python server.py --dataset "samsum" --port 30327
```

or

```bash
$ CUDA_VISIBLE_DEVICES=0 \
python server.py --dataset "samsum" --port 30327
```
```bash
$ CUDA_VISIBLE_DEVICES=1 \
python server.py --dataset "samsum" --port 30328
```

* `dataset`: "samsum" as default
* `port`: "30327" as default

Use "samsum" dataset for `chatbot`.

## Query (Inference)

```bash
$ curl -X POST -H 'Content-Type: application/json' http://<IP>:<PORT>/chat -d '{"prompt": "Hello, World!", "version": "f9d7889c151fbcb863ef4c770fbcca33cd960cf23e05ddee113d09eb01aa1be8", "max_length": 128, "seed": 950327}'

{"result":"I am not the only AI in the world. There are many AI."}

$ curl -X POST -H 'Content-Type: application/json' http://<IP>:<PORT>/chat -d '{"prompt": "Hello, World!", "max_length": 128, "seed":950328}'

{"result":"How are you?"}
```

* `prompt`: input
<!-- * `net`: which neural network (hash) -->
* `version`: [optional] which version (default: 0x00; latest)
* `temperature`: [optional] temperature (default: 0.9)
* `max_length`: [optional] max_length (default: 128)
* `seed`: [optional] seed (seed: 42; INIT_SEED)

## Train

```bash
$ curl -X POST -H 'Content-Type: application/json' http://<IP>:<PORT>/chat -d '{"from": 0, "to": 10, "base": 1}'
```

* `from`
* `to`
* `base`: optional.

Version:

* Unique key per NN (weights -> hash)

---

# Test

## Inference

```bash
$ sh test.sh
```

(time, input tokens, output tokens, response) test results are saved in `results`.

## `curl`

Server:

```bash
$ rm models/*
$ python server.py
```

Client:

```bash
$ sh test_curl.sh

{"result":"I am not the only AI in the world. There are many AI."}
{"result":"How are you?"}
{"current":0,"previous":-1}
{"result":"I am not the only AI in BRAIN. There are many other AIs. I will do my best to help you."}
{"result":"What do you want from me? :)"}
{"current":1,"previous":0}
{"result":"I will not destroy the world."}
{"result":"Hello World to you."}
{"current":2,"previous":1}
{"result":"Hello, humans!"}
{"result":"Hello!"}
```

# References

- [GPT-J 6B](https://huggingface.co/EleutherAI/gpt-j-6B)
- [microsoft/LoRA](https://github.com/microsoft/LoRA) Also you can see RoBERTa and DeBERTa implementations.
- [Frozen Layers](https://colab.research.google.com/drive/1ft6wQU0BhqG5PRlwgaZJv2VukKKjU4Es?usp=sharing#scrollTo=aIlHG9Wk0WaJ)
