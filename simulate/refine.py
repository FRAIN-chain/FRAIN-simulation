import os
import pandas as pd
import numpy as np


PATH = "./results"


def minMaxAvgSdMed(t: np.array, i: np.array, o: np.array):
    print(f"- Time:     Min {min(t):8.4f}, Max {max(t):8.4f}, Avg {(np.average(t)):8.4f} (SD: {t.std():8.4f}), MED {np.median(t):8.4f}")
    print(f"- Input:    Min {min(i):8d}, Max {max(i):8d}, Avg {(np.average(i)):8.4f} (SD: {i.std():8.4f}), MED {int(np.median(i)):8d}")
    print(f"- Output:   Min {min(o):8d}, Max {max(o):8d}, Avg {(np.average(o)):8.4f} (SD: {o.std():8.4f}), MED {int(np.median(o)):8d}")


if __name__ == "__main__":
    print()

    file_lists = os.listdir(PATH)
    file_lists = [f for f in file_lists if f.endswith('txt')]  # only txt

    # metadata
    nfile = len(file_lists)
    round = None
    header = list()
    zeros = None

    # data
    times = np.array([])
    inputs = np.array([])
    outputs = np.array([])
    # responses = list()

    for fid, file_list in enumerate(file_lists):
        filepath = PATH + '/' + file_list
        # print(file_list)

        with open(filepath, 'r') as f:
            df = pd.read_csv(f, delimiter='\t|\n', header=0, engine='python')

            if round == None:  # init
                round = len(df)
                header = list(df.columns)
                times = np.zeros((nfile, round), dtype=float)

                inputs = np.array(df.loc[:, 'inputs'])
                outputs = np.array(df.loc[:, 'outputs'])

            tzs = 0
            for index, row in df.iterrows():
                # print(row)
                if row['outputs'] == 0:
                    tzs += 1
                else:
                    times[fid][index] = float(row['time'])

            if zeros == None:  # init
                zeros = tzs

    # Median
    times = np.median(times, axis=0)
    df = pd.DataFrame({
        'round': range(round),
        'time': times
    })
    df.to_csv(PATH + '/' + 'med_times.csv', index=False, sep='\t')  # save

    times = times[np.nonzero(outputs)]
    inputs = inputs[np.nonzero(outputs)]
    outputs = outputs[np.nonzero(outputs)]

    print(f"From {nfile} files, {round} data per file, except {zeros} zerolen result.")
    minMaxAvgSdMed(times, inputs, outputs)
    print("=" * 81)
    print()

    # inputs: 287~361
    # outputs: 1~234

    xs = [0] + [290, 320] + [361]
    ys = [0] + [10, 20, 50, 100] + [234]

    x_ids = [np.where((x_1 < inputs) & (inputs <= x_2))[0] for x_1, x_2 in zip(xs[:-1], xs[1:])]
    y_ids = [np.where((y_1 < outputs) & (outputs <= y_2))[0] for y_1, y_2 in zip(ys[:-1], ys[1:])]

    c_count = 0
    z_count = 0
    for xid, i in enumerate(x_ids):
        for yid, o in enumerate(y_ids):
            c = list()
            for k in range(round):
                if (k in i) & (k in o):
                    c.append(k)
            # print(c)  # category indices
            if len(c) == 0:
                z_count += 1
            else:
                c_count += 1

                c_times = times[c]
                c_inputs = inputs[c]
                c_outputs = outputs[c]

                print(f"(~{xs[xid+1]:3d}) x (~{ys[yid+1]:3d}): {len(c):3d}")
                minMaxAvgSdMed(c_times, c_inputs, c_outputs)
                print()

    print(f"{len(xs)-1} * {len(ys)-1} - {z_count} == {c_count} categories except {z_count} zerolen category.")
    print("=" * 81)
    print()
