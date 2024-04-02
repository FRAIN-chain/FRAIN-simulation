# TL;DR

```bash
# Do inference simulations
$ sh simul.sh

# Make Heatmaps about $E_I$, $d$, and $Q_C$
$ sh simul_heatmap.sh
```

---

# 🛜 Run Server


Run `chatbot`, use "samsum" dataset.

```bash
$ CUDA_VISIBLE_DEVICES=0,1 \
python server.py --dataset "samsum" --port 30327
```

*or*

```bash
$ CUDA_VISIBLE_DEVICES=0 \
python server.py --dataset "samsum" --port 30327

$ CUDA_VISIBLE_DEVICES=1 \
python server.py --dataset "samsum" --port 30328
```

* `dataset`: "samsum" as default
* `port`: "30327" as default


## Inference

```bash
$ curl -X POST -H 'Content-Type: application/json' http://<IP>:<PORT>/chat -d '{"prompt": "Hello, World!", "version": "f9d7889c151fbcb863ef4c770fbcca33cd960cf23e05ddee113d09eb01aa1be8", "max_length": 128, "seed": 950327}'

{"result":"I am not the only AI in the world. There are many AI."}

$ curl -X POST -H 'Content-Type: application/json' http://<IP>:<PORT>/chat -d '{"prompt": "Hello, World!", "max_length": 128, "seed":950328}'

{"result":"How are you?"}
```

* `prompt`: input
* `version`: [optional] which version (default: 0x00; latest)
* `temperature`: [optional] temperature (default: 0.9)
* `max_length`: [optional] max_length (default: 128)
* `seed`: [optional] seed (seed: 42; INIT_SEED)


## Train

```bash
$ curl -X POST -H 'Content-Type: application/json' http://<IP>:<PORT>/chat -d '{"from": 0, "to": 10}'
```

* `from`: dataset pagination starting point
* `to`: dataset pagination end point

Returns:

* `previous`: Previous version of model. Unique key per NN — hash of the weights.
* `current`: Current version of model. Unique key per NN — hash of the weights.

---

# 📈 Simulation


## Inference

Get inference results:

```bash
$ sh test_0.sh
$ sh test_1.sh
```

* (round, time, input tokens, output tokens, response) test results are saved in `results`.

Then refine them:

```bash
$ python simulate/refine.py
```

Run BRAIN simulation:

```bash
$ python simulate/nodes.py --help
usage: nodes.py [-h] [--seed S] [--repeat R] [--stop P] [--verbose V] [--path PATH] [--interval I] [--size S] [--freq F] [--latency L] [--nodes N] [--byz B] [--epoch E] [--d D] [--qc QC] [--qto O]

Hyperparameters

options:
  -h, --help    show this help message and exit
  --seed S      Seed for simulation
  --repeat R    # simulation
  --stop P      Stop this round when for loop reaching P
  --verbose V   0: silent, 1: speak, 2: speak all
  --path PATH   path for saving pkl files
  --interval I  Average Block Time
  --size S      Average # of Transaction per block
  --freq F      Inference Request / Normal Tx
  --latency L   Latency of normal EVM execution (s)
  --nodes N     Number of nodes
  --byz B       The number of Byzantine nodes
  --epoch E     Epoch [blocks]
  --d D         difficulty (0, 2^256-1], but scaled in (0, 256]
  --qc QC       Quorum of Commitments
  --qto O       Inference Request's Timeout [blocks] \ 0 for infinity
```

*or*

```bash
$ sh simul.sh
```


# Visualization

```bash
$ python visualization/heatmap.py
```

*or*

```bash
$ sh simul_heatmap.sh
```
