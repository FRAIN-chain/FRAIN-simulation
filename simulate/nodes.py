import argparse
import os
import pandas as pd
import numpy as np
import random
import math


PATH = "./results"


def argparser():
    """ Parse command line arguments for the simulation. """
    parser = argparse.ArgumentParser(description='Hyperparameters')

    parser.add_argument('--seed', metavar='S', type=int, default=42,
                        help='Seed for simulation')
    parser.add_argument('--repeat', metavar='R', type=int, default=100,
                        help='# simulation')
    parser.add_argument('--stop', metavar='P', type=int, default=2000000,
                        help='Stop this round when for loop reaching P')
    parser.add_argument('--verbose', metavar='V', type=int, default=1,
                        help='0: silent, 1: speak, 2: speak all')

    """Blockchain Hyperparams"""

    # January 13, 2023 (https://etherscan.io/chart/blocktime) (https://polygonscan.com/chart/blocktime)
    parser.add_argument('--interval', metavar='I', type=float, default=12.06,
                        help='Average Block Time')
    # January 13, 2023 (https://etherscan.io/chart/tx) (https://polygonscan.com/chart/tx)
    # 154.630975 -> 155, 71.65305 -> 72
    parser.add_argument('--size', metavar='S', type=int, default=155,
                        help='Average # of Transaction per block')
    # Opensea, 2022 Q2 (https://dune.com/queries/690140/1280371) (https://etherscan.io/chart/tx)
    # 5752729 / 99638953 = 0.05773574317 -> 0.0577
    parser.add_argument('--freq', metavar='F', type=float, default=0.0577,
                        help='Inference Request / Normal Tx')
    # (0.05 / 155) = 0.0003225806452 : Sereum - Protecting Existing Smart Contracts Against Re-Entrancy Attacks
    # (0.001) : Ethanos - efficient bootstrapping for full nodes on account-based blockchain
    parser.add_argument('--latency', metavar='L', type=float, default=0.001,
                        help='Latency of normal EVM execution (s)')

    """BRAIN Hyperparams"""

    parser.add_argument('--nodes', metavar='N', type=int, default=21,
                        help='Number of nodes')  # Also, Block Producer (BP)
    parser.add_argument('--byz', metavar='B', type=int, default=0,
                        help='The number of Byzantine nodes')
    parser.add_argument('--epoch', metavar='E', type=int, default=8,
                        help='Epoch [blocks]')
    parser.add_argument('--d', metavar='D', type=int, default=128,
                        help='difficulty (0, 2^256-1], but scaling into (0, 256]')
    parser.add_argument('--qc', metavar='QC', type=int, default=11,
                        help='Quorum of Commitments')
    # parser.add_argument('--qr', metavar='QR', type=int, default=11,
    # help='Quorum of Revelations')
    parser.add_argument('--qto', metavar='O', type=int, default=20,
                        help='Inference Request\'s Timeout [blocks]')
    # parser.add_argument('--tr', metavar='TR', type=int, default=30,
    # help='Period of the Reveal Phase [blocks]')
    # parser.add_argument('--te', metavar='TE', type=int, default=1000,
    # help='Period of the Execute Phase [blocks]')

    return parser.parse_args()


if __name__ == "__main__":
    args = argparser()
    if args.verbose > 1:
        print()
        print(args)
        print("=" * 105)
        print()

    filepath = PATH + '/' + 'med_times.csv'

    n_qtx = None
    times = None

    with open(filepath, 'r') as f:
        df = pd.read_csv(f, delimiter='\t|\n', header=0, engine='python')
        n_qtx = len(df)
        # for index, row in df.iterrows():
        # print(row['time'])
        times = np.array(df.loc[:, 'time'])

    if args.verbose > 0:
        print(f"# Inference Requests: {n_qtx}")
        # print(f"Normal TX latency: {args.latency:8.4f}, Avg Inference latency: {np.average(times[np.nonzero(times)]):8.4f}, (SD: {times.std():8.4f})")
        print(f"All Inference time: {sum(times):10.4f}")
        print(f"Avg Inference time: {np.average(times[np.nonzero(times)]):10.4f}, (SD: {times.std():10.4f})")
        print("=" * 105)
        print()

    """Simulator"""

    from queue import PriorityQueue  # (priority, (block_height_when_req, time, qtxid))
    # top() -> qs.queue[0]
    # pop() -> get()
    # push() -> put()

    def pareto(size, alpha=1.16, lower=0., upper=1.):
        s = np.random.pareto(alpha, size)
        s /= sum(s)
        s *= (upper - lower)
        s += lower
        return s.clip(lower, upper)

    repeat = args.repeat
    nodes = args.nodes

    # Evaluation data above all rounds
    latencies_block = np.array([], dtype=int)
    blocks = list()
    n_txs = list()
    timeouts = list()
    additional_txs = list()
    max_queue_lens = list()

    for r in range(repeat):  # in this repeat,
        random.seed(args.seed + r)  # fix seed for each round

        # BRAIN
        qs = PriorityQueue()  # lower is first. (because of pareto dist.)
        ps = pareto(n_qtx, lower=2, upper=1000)  # 0 for highest priority, 1 for secondary
        commitments = np.zeros(n_qtx)
        # revelations = np.array([0 for _ in range(n_qtx)])  # assumption: all nodes reveal commitment in an one block.
        committee = np.zeros((n_qtx, args.nodes))

        # Metrics
        inferences = [dict({'start': -1, 'end': -1}) for _ in range(n_qtx)]  # latency = inferences[id][end] - inferences[id][start] in [Block]  # for evaluation

        # create tx set
        txn = int(n_qtx / args.freq)
        txs = [-1 for _ in range(txn)] + [t for t in range(n_qtx)]  # -1 for normal txs, 0~N for inference queries
        random.shuffle(txs)
        txs += [-1 for _ in range(args.stop - len(txs))]

        # for VRF
        # seed = args.seed + r

        # data
        current_block = 0
        timeout_count = 0
        inference_count = 0
        additional_tx = 0
        max_queue_len = 0

        for txid, tx in enumerate(txs):  # each tx w/ txid
            if txid % args.size == 0:
                current_block += 1

            if args.verbose > 1:
                print(f"Round {r:4d}, Block {current_block:4d}, Inference: # {inference_count:4d}, Timeout: # {timeout_count:4d}, txid {txid:6d} / {len(txs):6d}, tx {'normal' if tx == -1 else 'inferq'} {tx:4d}", end='\r')

            # Tx
            if tx == -1:  # normal tx
                pass
            else:  # inference request tx

                # Fail case
                if (args.nodes - args.byz) < args.qc:
                    timeout_count += 1
                    continue

                qs.put((ps[tx], (current_block, times[tx], tx)))  # inference request, push()
                inferences[tx]['start'] = current_block
                # counting on tx - no additional tx

                if qs.qsize() > max_queue_len:
                    max_queue_len = qs.qsize()

            # Each node
            for n in range(nodes):
                if qs.empty():
                    pass  # nothing in the queue
                elif qs.queue[0][0] != 0:  # nothing to refer now
                    top = qs.queue[0]  # top
                    requested_block = top[1][0]
                    if requested_block < current_block:
                        q = qs.get()[1]  # update
                        qs.put((0, (requested_block, q[1], q[2])))  # update w/ highest priority. Now can refer it.

                # Actions: not empty, highest priority.
                if (not qs.empty()) and (qs.queue[0][0] == 0):
                    # Timeout
                    if current_block - qs.queue[0][1][0] >= args.qto:
                        qs.get()
                        timeout_count += 1
                        # break

                    # Enough block height: Do action.
                    elif (qs.queue[0][1][0] < current_block):
                        q = qs.queue[0][1]

                        # vrf
                        # vrf_seed = int(f"{q[2]}{seed}{int(current_block / args.epoch)}{n}")
                        # random.seed(vrf_seed)
                        y = random.randint(0, 256)
                        # byzantine
                        # probabilistic approach
                        bp = random.randint(0, args.nodes)
                        if (bp >= args.byz) and (y < args.d) and (committee[q[2]][n] == 0):  # join committee
                            # inference
                            # print(f"- node {n} do inference")

                            # commit
                            commitments[q[2]] += 1
                            additional_tx += 2  # commit and reveal
                            committee[q[2]][n] = 1

                            if commitments[q[2]] >= args.qc:
                                # seed update
                                # random.seed(seed)
                                # seed = random.randint(0, 256)  # 0~256

                                # pop
                                qs.get()
                                inferences[q[2]]['end'] = current_block + int(times[q[2]] / args.interval) + 1  # for inference time
                                inference_count += 1
                                current_block += 1

                        elif (bp < args.byz) and (n == args.nodes - 1):  # byzantine case
                            current_block += 1

            if (inference_count + timeout_count) == n_qtx:
                break

        """End of Round"""
        if args.verbose == 1:
            print(f"Round {r:4d} End", end='\r')

        # print("=" * 105)
        for i, inference in enumerate(inferences):
            if inference['end'] == -1:
                # TODO: fallbacks (for not ended qtxs)
                if args.verbose > 1:
                    print(f"Fallbacks @ {r:4d}, {i:4d}, {inference}")
            else:
                latencies_block = np.append(latencies_block, [inference['end'] - inference['start']])  # latencies_block

        if args.verbose > 1:
            print(f"Round {r:4d}, Block {current_block:4d}, Inference: # {inference_count:4d}, Timeout: # {timeout_count:4d}" + " " * 19)
            print("=" * 105)
            print()
        # print("Queue", qs.queue)
        # Per round operations
        blocks.append(current_block + 1)  # +1
        n_txs.append(math.ceil(txid / args.size) * args.size)
        timeouts.append(timeout_count)
        max_queue_lens.append(max_queue_len)
        additional_txs.append(additional_tx)

    # All round operations
    # print("=" * 105)
    # print("Blocks per round:", blocks)
    # print("TXs per round     :", n_txs)

    def evaluate(A):
        if len(A) == 0:
            return "Empty"
        return f"Min {min(A):10.4f}, Max {max(A):10.4f}, Avg {(np.average(A)):10.4f} (SD: {A.std():10.4f}), MED {(np.median(A)):10.4f}"

    blocks = np.array(blocks)
    n_txs = np.array(n_txs)  # number of tasks
    timeouts = np.array(timeouts)  # failed inference tasks
    max_queue_lens = np.array(max_queue_lens)
    additional_txs = np.array(additional_txs)

    BRAIN_elapsed_times = (n_txs + additional_txs) * args.latency
    others_elapsed_times = (n_txs - n_qtx) * args.latency + sum(times)

    print(f"Executed Time (s)       :", evaluate(BRAIN_elapsed_times))
    print(f"Executed Inference Tasks:", evaluate(n_qtx - timeouts))
    print(f"Timeout  Inference Tasks:", evaluate(timeouts))
    print()
    print(f"TPS (tx/s) No Inference :", evaluate(np.ones(args.repeat) * (1 / args.latency)))  # tasks / (tasks * per_latency)
    print(f"TPS (tx/s) Other        :", evaluate(n_txs / others_elapsed_times))
    print(f"TPS (tx/s) BRAIN        :", evaluate(n_txs / BRAIN_elapsed_times))  # [Task Per Second]
    print()
    print(f"Max Queue Length        :", evaluate(max_queue_lens))
    print(f"Latency [blocks]        :", evaluate(latencies_block))
    if args.verbose > 0:
        print("=" * 105)
        print()
