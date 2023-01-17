import argparse
import os
import pandas as pd
import numpy as np
import random


PATH = "./results"


def argparser():
    parser = argparse.ArgumentParser(description='Hyperparameters')

    parser.add_argument('--seed', metavar='S', type=int, default=42,
                        help='Seed for simulation')
    parser.add_argument('--repeat', metavar='R', type=int, default=1000,
                        help='# simulation')
    parser.add_argument('--stop', metavar='P', type=int, default=1000000,
                        help='Stop this round when for loop reaching P')
    parser.add_argument('--verbose', metavar='V', type=int, default=0,
                        help='0: silent, 1: speak')

    """Blockchain Hyperparams"""

    # January 13, 2023 (https://etherscan.io/chart/blocktime)
    parser.add_argument('--interval', metavar='I', type=float, default=12.06,
                        help='Average Block Time')
    # January 13, 2023 (https://etherscan.io/chart/tx)
    # 154.630975 -> 155
    parser.add_argument('--size', metavar='S', type=int, default=155,
                        help='Average # of Transaction per block')
    parser.add_argument('--freq', metavar='F', type=float, default=0.02,
                        help='Inference Request / Normal Tx')
    # (0.05 / 155) : Sereum - Protecting Existing Smart Contracts Against Re-Entrancy Attacks
    # (0.001) : Ethanos - efficient bootstrapping for full nodes on account-based blockchain
    parser.add_argument('--latency', metavar='L', type=float, default=0.001,
                        help='Latency of normal EVM execution (s)')

    """BRAIN Hyperparams"""

    parser.add_argument('--nodes', metavar='N', type=int, default=21,
                        help='Number of nodes')  # Also, Block Producer (BP)
    parser.add_argument('--epoch', metavar='E', type=int, default=10,
                        help='Epoch [blocks]')
    parser.add_argument('--d', metavar='D', type=int, default=128,
                        help='difficulty (0, 2^256-1], but scaling into (0, 256]')
    parser.add_argument('--qc', metavar='QC', type=int, default=4,
                        help='Quorum of Commitments')
    # parser.add_argument('--qr', metavar='QR', type=int, default=4,
    # help='Quorum of Revelations')
    parser.add_argument('--tc', metavar='TC', type=int, default=100,
                        help='Period of the Commit Phase [blocks]')
    # parser.add_argument('--tr', metavar='TR', type=int, default=30,
    # help='Period of the Reveal Phase [blocks]')
    # parser.add_argument('--te', metavar='TE', type=int, default=1000,
    # help='Period of the Execute Phase [blocks]')

    return parser.parse_args()


if __name__ == "__main__":
    print()

    args = argparser()
    print(args)
    if args.verbose != 0:
        print("=" * 85)
    print()

    filepath = PATH + '/' + 'med_times.csv'

    qtxn = None
    times = None

    with open(filepath, 'r') as f:
        df = pd.read_csv(f, delimiter='\t|\n', header=0, engine='python')
        qtxn = len(df)
        # for index, row in df.iterrows():
        # print(row['time'])
        times = np.array(df.loc[:, 'time'])

    print(f"# Inference Requests: {qtxn}")
    # print(f"Normal TX latency: {args.latency:8.4f}, Avg Inference latency: {np.average(times[np.nonzero(times)]):8.4f}, (SD: {times.std():8.4f})")
    print(f"Avg Inference latency: {np.average(times[np.nonzero(times)]):8.4f}, (SD: {times.std():8.4f})")
    if args.verbose != 0:
        print("=" * 85)
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
    ntxs = list()
    timeouts = list()

    for r in range(repeat):  # in this repeat,
        random.seed(args.seed + r)  # fix seed for each round

        # BRAIN
        qs = PriorityQueue()  # lower is first. (because of pareto dist.)
        ps = pareto(qtxn, lower=2, upper=1000)  # 0 for highest priority, 1 for secondary
        commitments = np.array([0 for _ in range(qtxn)])
        # revelations = np.array([0 for _ in range(qtxn)])  # assumption: all nodes reveal commitment in an one block.

        # Metrics
        inferences = [dict({'start': -1, 'end': -1}) for _ in range(qtxn)]  # latency = inferences[id][end] - inferences[id][start] in [Block]  # for evaluation

        # create tx set
        txn = int(qtxn / args.freq)
        txs = [-1 for _ in range(txn)] + [t for t in range(qtxn)]  # -1 for normal txs, 0~N for inference queries
        random.shuffle(txs)
        if len(txs) < args.stop:
            txs += [-1 for _ in range(args.stop - len(txs))]  # for late submissions

        # for VRF
        seed = args.seed + r

        # data
        current_block = 0
        timeout_count = 0
        inference_count = 0

        for txid, tx in enumerate(txs):  # each tx w/ txid
            if txid % args.size == 0:
                current_block += 1

            # if args.verbose != 0:
            print(f"Round {r:4d}, Block {current_block:4d}, Inference: # {inference_count:4d}, Timeout: # {timeout_count:4d}, txid {txid:6d} / {len(txs):6d}, tx {'normal' if tx == -1 else 'inferq'} {tx:4d}", end='\r')

            # Tx
            if tx == -1:  # normal tx
                pass
            else:  # inference request tx
                qs.put((ps[tx], (current_block, times[tx], tx)))  # inference request, push()
                inferences[tx]['start'] = current_block

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
                    if current_block - qs.queue[0][1][0] >= args.tc:
                        qs.get()
                        timeout_count += 1
                        # break

                    # Enough block height: Do action.
                    elif (qs.queue[0][1][0] < current_block):
                        q = qs.queue[0][1]

                        # vrf
                        vrf_seed = int(f"{q[2]}{seed}{int(current_block / args.epoch)}{n}")
                        random.seed(vrf_seed)
                        if random.randint(0, 256) < args.d:  # join committee
                            # inference
                            # print(f"- node {n} do inference")

                            # commit
                            commitments[q[2]] += 1
                            if commitments[q[2]] >= args.qc:
                                # seed update
                                random.seed(seed)
                                seed = random.randint(0, 256)  # 0~256

                                # pop
                                qs.get()
                                inference_count += 1
                                # break

            # commit->reveal->execute
            for id in np.where(commitments >= args.qc)[0]:  # Actually, ==
                if inferences[id]['end'] == -1:
                    inferences[id]['end'] = current_block + int(times[id] / args.interval) + 1  # for inference time

            if (inference_count + timeout_count) == qtxn:
                break

        """End of Round"""

        # print("=" * 85)
        for i, inference in enumerate(inferences):
            if inference['end'] == -1:
                # TODO: fallbacks (for not ended qtxs)
                if args.verbose != 0:
                    print(f"Fallbacks @ {r:4d}, {i:4d}, {inference}")
            else:
                latencies_block = np.append(latencies_block, [inference['end'] - inference['start']])  # latencies_block

        if args.verbose != 0:
            print(f"Round {r:4d}, Block {current_block:4d}, Inference: # {inference_count:4d}, Timeout: # {timeout_count:4d}" + " " * 19)
            print("=" * 85)
            print()
        # print("Queue", qs.queue)
        # Per round operations
        blocks.append(current_block)
        ntxs.append(txid)
        timeouts.append(timeout_count)

    # All round operations
    # print("=" * 85)
    # print("Blocks per round:", blocks)
    # print("TXs per round     :", ntxs)

    def evaluate(A):
        return f"Min {min(A):10.4f}, Max {max(A):10.4f}, Avg {(np.average(A)):10.4f} (SD: {A.std():10.4f}), MED {(np.median(A)):10.4f}"

    ntxs = np.array(ntxs)
    elapsed_times = (ntxs - qtxn) * args.latency + sum(times)
    timeouts = np.array(timeouts)

    print(f"Execution Time (s)      : {sum(times):10.4f}", " " * 70)
    print(f"Timeout                 :", evaluate(timeouts))
    print(f"TPS (tx/s) No Inference : {(1 / args.latency):10.4f}")
    print(f"TPS (tx/s) Other        :", evaluate(819. / elapsed_times))
    print(f"TPS (tx/s) BRAIN        :", evaluate(ntxs / elapsed_times))
    print(f"Latency [blocks]        :", evaluate(latencies_block))
    print("=" * 85)
    print()

    if args.verbose != 0:
        latencies_block = latencies_block.reshape((args.repeat, qtxn))
        for r, ls in enumerate(latencies_block):
            print(f"Round {r:4d}: Latency[Blocks] Min {min(ls):4d}, Max {max(ls):4d}, Avg {(np.average(ls)):8.4f} (SD: {ls.std():8.4f}), MED {int(np.median(ls)):4d}")
        print()
