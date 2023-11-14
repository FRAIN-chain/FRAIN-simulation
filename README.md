# Contents

- [GPT-J-6B LoRA](#lora-integrated-gpt-j-6b-server)
- [BRAIN Simulation](#Simulation)
- [Commit-and-Reveal](#Commit-and-Reveal)
- [Queue](#Queue)
- [Verifiable Random Functions](#VRF)

---

# LoRA integrated GPT-J-6B Server

Request inference and training to LoRA integrated GPT-J-6B.
Chat (Human ↔️ BRAIN).

### Default Settings
- r=1
- float16
- cuda

## How to Use

### Run Chatbot

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

### Query (Inference)

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

### Train

```bash
$ curl -X POST -H 'Content-Type: application/json' http://<IP>:<PORT>/chat -d '{"from": 0, "to": 10, "base": 1}'
```

* `from`
* `to`
* `base`: optional.

Version:

* Unique key per NN (weights -> hash)

## Test

### Inference

```bash
$ sh test_0.sh
```

```bash
$ sh test_1.sh
```

(round, time, input tokens, output tokens, response) test results are saved in `results`.

### `curl`

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

---

# Simulation

Get Inference Time Table:

```bash
$ python simulate/refine.py
```

Run BRAIN Simulation:

```bash
$ python simulate/nodes.py
```

## How to Use

```bash
$ python simulate/nodes.py --help
```

```
usage: nodes.py [-h] [--seed S] [--repeat R] [--stop P]
                [--interval I] [--size S] [--freq F] [--nodes N]
                [--epoch E] [--d D] [--qc QC] [--tc TC]

Hyperparameters

optional arguments:
  -h, --help    show this help message and exit
  --seed S      Seed for simulation
  --repeat R    # simulation
  --stop P      Stop this round when for loop reaching P
  --interval I  Average Block Time
  --size S      Average # of Transaction per block
  --freq F      Inference Request / Normal Tx
  --nodes N     Number of nodes
  --epoch E     Epoch [blocks]
  --d D         difficulty (0, 2^256-1], but scaling into (0, 256]
  --qc QC       Quorum of Commitments
  --tc TC       Period of the Commit Phase [blocks]
```

or

```bash
$ sh simul.sh
```

---

# Contracts

In each `contracts/<scheme>` repo:

## Commit-and-Reveal

- solc: 0.6.12

### Test

```bash
$ npx hardhat node
```

```bash
$ npx hardhat test benchmark/CommitReveal.js --network localhost

  CommitReveal
    Normal
Tester:  0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
Deploy CommitReveal:     0x129955157BE2622EbB0a7bEBC990216C63069973
      ✓ Commit Hash (38734054 gas)
      ✓ Reveal Hash (71372250 gas)
    Hashed
      ✓ Commit Hash (36884859 gas)
      ✓ Reveal Hash (38856806 gas)

·----------------------------------|---------------------------|-------------|----------------------------·
|       Solc version: 0.6.12       ·  Optimizer enabled: true  ·  Runs: 200  ·  Block limit: 6718946 gas  │
···································|···························|·············|·····························
|  Methods                                                                                                │
·················|·················|·············|·············|·············|··············|··············
|  Contract      ·  Method         ·  Min        ·  Max        ·  Avg        ·  # calls     ·  usd (avg)  │
·················|·················|·············|·············|·············|··············|··············
|  CommitReveal  ·  commit         ·      44825  ·      62072  ·      45732  ·         820  ·          -  │
·················|·················|·············|·············|·············|··············|··············
|  CommitReveal  ·  commit_hashed  ·      44861  ·      44897  ·      44895  ·         820  ·          -  │
·················|·················|·············|·············|·············|··············|··············
|  CommitReveal  ·  reveal         ·      27831  ·     796620  ·      87124  ·         820  ·          -  │
·················|·················|·············|·············|·············|··············|··············
|  CommitReveal  ·  reveal_hashed  ·      47355  ·      47391  ·      47389  ·         819  ·          -  │
·················|·················|·············|·············|·············|··············|··············
|  Deployments                     ·                                         ·  % of limit  ·             │
···································|·············|·············|·············|··············|··············
|  CommitReveal                    ·          -  ·          -  ·     691625  ·      10.3 %  ·          -  │
·----------------------------------|-------------|-------------|-------------|--------------|-------------·

  4 passing (7m)
```

## Queue

PriorityQueue and CircularQueue.

- solc: 0.6.12

### Test

```bash
$ npx hardhat node
# or
$ ganachi-cli
```

```bash
$ npx hardhat test benchmark/Queues.js --network localhost

  Queues
    Queue
Tester:  0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
Deploy Queue:    0x129955157BE2622EbB0a7bEBC990216C63069973
Deploy PriorityQueue:    0x2E80eF24fA1938D4e2F01A564CaC98c77AaAfaa2
      ✓ Push (43314229 gas)
      ✓ Pop (23830071 gas)
    PriorityQueue
      ✓ Push (75137628 gas)
      ✓ Pop (82689318 gas)

·----------------------------|---------------------------|-------------|----------------------------·
|    Solc version: 0.6.12    ·  Optimizer enabled: true  ·  Runs: 200  ·  Block limit: 6718946 gas  │
·····························|···························|·············|·····························
|  Methods                                                                                          │
··················|··········|·············|·············|·············|··············|··············
|  Contract       ·  Method  ·  Min        ·  Max        ·  Avg        ·  # calls     ·  usd (avg)  │
··················|··········|·············|·············|·············|··············|··············
|  CircularQueue  ·  pop     ·      29013  ·      46113  ·      29034  ·         820  ·          -  │
··················|··········|·············|·············|·············|··············|··············
|  CircularQueue  ·  push    ·      51324  ·      68424  ·      51345  ·         820  ·          -  │
··················|··········|·············|·············|·············|··············|··············
|  PriorityQueue  ·  pop     ·      34909  ·     116942  ·     100861  ·         819  ·          -  │
··················|··········|·············|·············|·············|··············|··············
|  PriorityQueue  ·  push    ·      84353  ·     137955  ·      91699  ·         820  ·          -  │
··················|··········|·············|·············|·············|··············|··············
|  Deployments               ·                                         ·  % of limit  ·             │
·····························|·············|·············|·············|··············|··············
|  CircularQueue             ·          -  ·          -  ·     165973  ·       2.5 %  ·          -  │
·····························|·············|·············|·············|··············|··············
|  PriorityQueue             ·          -  ·          -  ·     379664  ·       5.7 %  ·          -  │
·----------------------------|-------------|-------------|-------------|--------------|-------------·

  4 passing (8m)
```

## VRF

Verifiable Random Functions.

- solc version: 0.6.12+commit.27d51765
- optimizer enabled: true (runs 200)

```bash
$ nvm use 12

$ ganache-cli -b 5
```
```bash
$ nvm use 12

$ truffle test --network local ./benchmark/VRFGasHelper.sol ./benchmark/gas.js

  Contract: VRFGasHelper - Gas consumption analysis
    VRF verification functions:
      ✓ should verify a VRF proof (1) (1615119 gas)
      ✓ should verify a VRF proof (2) (1706587 gas)
      ...
```

```
·--------------------------------------------|---------------------------|-------------|----------------------------·
|    Solc version: 0.6.12+commit.27d51765    ·  Optimizer enabled: true  ·  Runs: 200  ·  Block limit: 6718946 gas  │
·············································|···························|·············|·····························
|  Methods                                                                                                          │
·················|···························|·············|·············|·············|··············|··············
|  Contract      ·  Method                   ·  Min        ·  Max        ·  Avg        ·  # calls     ·  usd (avg)  │
·················|···························|·············|·············|·············|··············|··············
|  VRFGasHelper  ·  computeFastVerifyParams  ·    1513058  ·    1831274  ·    1611989  ·          91  ·          -  │
·················|···························|·············|·············|·············|··············|··············
|  VRFGasHelper  ·  decodePoint              ·      55844  ·      55877  ·      55867  ·          10  ·          -  │
·················|···························|·············|·············|·············|··············|··············
|  VRFGasHelper  ·  decodeProof              ·      56839  ·      56860  ·      56851  ·          10  ·          -  │
·················|···························|·············|·············|·············|··············|··············
|  VRFGasHelper  ·  fastVerify               ·     106360  ·     352838  ·     150715  ·          94  ·          -  │
·················|···························|·············|·············|·············|··············|··············
|  VRFGasHelper  ·  gammaToHash              ·      24189  ·      24201  ·      24198  ·          91  ·          -  │
·················|···························|·············|·············|·············|··············|··············
|  VRFGasHelper  ·  verify                   ·    1543493  ·    1862450  ·    1643712  ·          92  ·          -  │
·················|···························|·············|·············|·············|··············|··············
|  Deployments                               ·                                         ·  % of limit  ·             │
·············································|·············|·············|·············|··············|··············
|  VRFGasHelper                              ·          -  ·          -  ·    1598637  ·      23.8 %  ·          -  │
·--------------------------------------------|-------------|-------------|-------------|--------------|-------------·

  195 passing (20m)
```

In Ethereum, gas consumption derived from [Etherscan](https://etherscan.io/gastracker) Average. USD price estimation derived from [CoinMarketCap](https://coinmarketcap.com/currencies/ethereum/).

- 14 gwei/gas
- 1412.49 usd/eth

```
·----------------|---------------------------|-------------|-------------|-------------|--------------|-------------·
|  Contract      ·  Method                   ·  Min        ·  Max        ·  Avg        ·  # calls     ·  usd (avg)  │
·----------------|---------------------------|-------------|-------------|-------------|--------------|-------------·
|  VRF           ·  verify                   ·    1543493  ·    1862450  ·    1643712  ·          92  ·      32.50  │
·················|···························|·············|·············|·············|··············|··············
|  VRF           ·  fastVerify               ·     106360  ·     352838  ·     150715  ·          94  ·       2.98  │
·----------------|---------------------------|-------------|-------------|-------------|--------------|-------------·
```

```
·----------------|---------------------------|-------------|-------------|-------------|--------------|-------------·
|  Contract      ·  Method                   ·  Min        ·  Max        ·  Avg        ·  # calls     ·  usd (avg)  │
·----------------|---------------------------|-------------|-------------|-------------|--------------|-------------·
|  VRF           ·  decodeProof              ·      56839  ·      56860  ·      56851  ·          10  ·       1.12  │
·················|···························|·············|·············|·············|··············|··············
|  VRF           ·  decodePoint              ·      55844  ·      55877  ·      55867  ·          10  ·       1.10  │
·················|···························|·············|·············|·············|··············|··············
|  VRF           ·  computeFastVerifyParams  ·    1513058  ·    1831274  ·    1611989  ·          91  ·      31.88  │
·----------------|---------------------------|-------------|-------------|-------------|--------------|-------------·
```

In Polygon, gas consumption derived from [Polygonscan](https://polygonscan.com/gastracker) Average. USD price estimation derived from [CoinMarketCap](https://coinmarketcap.com/currencies/polygon/).

- 51.6 gwei/gas
- 0.91 usd/matic

```
·----------------|---------------------------|-------------|-------------|-------------|--------------|-------------·
|  Contract      ·  Method                   ·  Min        ·  Max        ·  Avg        ·  # calls     ·  usd (avg)  │
·----------------|---------------------------|-------------|-------------|-------------|--------------|-------------·
|  VRF           ·  verify                   ·    1543493  ·    1862450  ·    1643712  ·          92  ·     0.0772  │
·················|···························|·············|·············|·············|··············|··············
|  VRF           ·  fastVerify               ·     106360  ·     352838  ·     150715  ·          94  ·     0.0071  │
·················|···························|·············|·············|·············|··············|··············
|  VRF           ·  decodeProof              ·      56839  ·      56860  ·      56851  ·          10  ·     0.0027  │
·················|···························|·············|·············|·············|··············|··············
|  VRF           ·  decodePoint              ·      55844  ·      55877  ·      55867  ·          10  ·     0.0026  │
·················|···························|·············|·············|·············|··············|··············
|  VRF           ·  computeFastVerifyParams  ·    1513058  ·    1831274  ·    1611989  ·          91  ·     0.0757  │
·----------------|---------------------------|-------------|-------------|-------------|--------------|-------------·
```

---

# References

- [GPT-J 6B](https://huggingface.co/EleutherAI/gpt-j-6B)
- [microsoft/LoRA](https://github.com/microsoft/LoRA) Also you can see RoBERTa and DeBERTa implementations.
- [Frozen Layers](https://colab.research.google.com/drive/1ft6wQU0BhqG5PRlwgaZJv2VukKKjU4Es?usp=sharing#scrollTo=aIlHG9Wk0WaJ)
- [Priority Queue](https://github.com/omgnetwork/plasma-mvp/blob/master/plasma/root_chain/contracts/PriorityQueue.sol)
- [Heap](https://github.com/zmitton/eth-heap)
