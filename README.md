# TL;DR

```bash
$ sh simul.sh
```


---


# 📈 Simulation


Run FRAIN simulation:

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
