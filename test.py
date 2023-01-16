import os  # nopep8
import sys  # nopep8
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/bot')  # nopep8
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/net')  # nopep8


from datasets import load_dataset


from bot.chatbot import Chatbot  # nopep8
from net.gptj_lora import gptj_lora  # nopep8

config, tokenizer, model = gptj_lora(
    "models/36eca1e38b0d04afd013a735f4af49f77c15fbb1e93167ddd083b1548b66ab0a"
)
chatbot = Chatbot(tokenizer, model)


import time

def chat(**params):
    start = time.time()
    result = chatbot(**params)
    end = time.time()

    base_prompt = chatbot._get_base_prompt()
    prompt = f"{base_prompt}\nHuman: {params['prompt']}\nBRAIN:"

    encoded_input = tokenizer(prompt, truncation=True, max_length=2048, return_tensors='pt') 
    encoded_output = tokenizer(result, truncation=True, max_length=2048, return_tensors='pt')

    # time, input tokens, output tokens, response
    print(f"{end - start:.8f}\t{encoded_input.input_ids.shape[1]}\t{encoded_output.input_ids.shape[1]}\t{result}")

    return


import argparse

def argparser():
    parser = argparse.ArgumentParser(description='Hyperparameters')

    parser.add_argument('--dataset', metavar='D', type=str, default="samsum", help='Dataset to use')
    parser.add_argument('--start', metavar='S', type=int, default=0, help='Start point of dataset')
    parser.add_argument('--end', metavar='E', type=int, default=100, help='End point of dataset')

    parser.add_argument('--round', metavar='R', type=int, default=1000, help='Round')

    args = parser.parse_args()
    return args


"""main"""

if __name__ == "__main__":
    args = argparser()
    # print(args) # dataset, start, end

    dataset = load_dataset(args.dataset)
    test_dataset = load_dataset("samsum", split=f'test[{args.start}%:{args.end}%]')
    # print(len(test_dataset)) # samsum test_dataset: 819

    rounds = args.round
    if len(test_dataset) < args.round:
        rounds = len(test_dataset)

    # time, input tokens, output tokens, response
    print("time\tinputs\toutputs\tresponse")

    for r in range(rounds):
        input = test_dataset[r]['dialogue'].split(": ", 1)[1].split("\n")[0]
        # print(r, test_dataset[r]['dialogue'].split(": ", 1)[1].split("\n")[0])

        chat(
            prompt=input,
            max_length=128,
            seed=r + 42
        )
