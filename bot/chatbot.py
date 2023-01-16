from tqdm.auto import tqdm

import torch
import torch.nn.functional as F
from torch import optim
from torch.autograd import Variable


from bot_base import Bot


import os  # nopep8
import sys  # nopep8
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))  # nopep8
from net.gptj_lora import get_adapters, set_adapters  # nopep8


from copy import deepcopy
import json
from Crypto.Hash import keccak


import numpy as np


class Chatbot(Bot):
    def __init__(
        self,
        tokenizer,
        model,
        path="models/36eca1e38b0d04afd013a735f4af49f77c15fbb1e93167ddd083b1548b66ab0a",  # gptj_lora
        version=None
    ):
        super().__init__(tokenizer, model, path=path)

        if version is not None:
            self.version = version  # current adapters verion
            self.load_adapters(version)
            self.adapters = get_adapters(self.model)
        else:
            # TODO: check: is it needed?
            self.adapters = get_adapters(self.model)
            self.version = self.adapters_hash(self.adapters)
            self.save_adapters(self.version)

    # Prompt use for chatbot.
    # It consists of Task description, Chatbot information, Chat Examples.
    @staticmethod
    def _get_base_prompt() -> str:
        return """Human: How can I start a successful business?
BRAIN: Networking and building a strong team are important.
Human: What are some tips for staying productive at work?
BRAIN: Taking breaks and maintaining a healthy work-life balance.
Human: How can I improve my relationship with my partner?
BRAIN: Making time for each other and work through any issues that may arise.
Human: How can I lose weight and get in shape?
BRAIN: A combination of regular exercise.
Human: What are some tips for managing stress?
BRAIN: Practicing relaxation techniques such as meditation.
Human: How can I improve my public speaking skills?
BRAIN: Practicing and being well-prepared are essential.
Human: How can I become more confident?
BRAIN: Building self-esteem, setting goals, and learning new skills.
Human: What are some ways to improve my memory?
BRAIN: Staying mentally and physically active.
Human: How can I be more successful in my career?
BRAIN: Setting clear goals, networking, and continuing to learn.
Human: How can I improve my financial situation?
BRAIN: Creating a budget and sticking to it.
Human: What are some tips for successful negotiation?
BRAIN: Active listening, clearly stating your own needs and wants.
Human: How can I become a better leader?
BRAIN: Developing strong communication skills.
Human: How can I improve my communication skills?
BRAIN: Practicing active listening.
Human: How can I be more productive?
BRAIN: Setting clear goals, prioritizing tasks, and minimizing distractions.
Human: What are some ways to improve my mental health?
BRAIN: Regular exercise, getting enough sleep, eating a healthy diet."""

    # Only first response text will return
    @staticmethod
    def _processing_response(response_text: str) -> str:
        ret_text = ""
        for i in range(0, len(response_text)):
            if response_text[i] == "\n" or response_text[i:i + 7] == "Human: " or response_text[i:i + 4] == "BRAIN: ":
                break
            ret_text += response_text[i]
        return ret_text.strip()

    def __call__(self, prompt, version=None, temperature=0.9, max_length=128, seed=Bot.INIT_SEED, device='cuda', **kwargs):
        self.load_adapters(version)

        base_prompt = self._get_base_prompt()
        prompt = f"{base_prompt}\nHuman: {prompt}\nBRAIN:"

        # res = inference(prompt)[len(prompt):]
        res = self.inference_with_seed(
            prompt, temperature, max_length, seed, device=device)[len(prompt):]

        return self._processing_response(res)

    def adapters_hash(self, adapters):
        raw_data = dict()
        for instance, module in adapters.items():
            for name, param in module.named_parameters():
                raw_data[f"{instance}.{name}"] = param.tolist()

        data_str = json.dumps(raw_data)

        k = keccak.new(digest_bits=256)
        k.update(data_str.encode())

        # print(">>>", k.hexdigest())
        return k.hexdigest()

    def train(self, dataset, version=None, num_epochs=2, device='cuda', **kwargs):
        self.load_adapters(version)

        """train"""
        # self.model.train()  # TODO: optimize

        for epoch in range(1, num_epochs+1):
            # self.model.gradient_checkpointing_enable()

            # use the parameters from Appendix D.4, Table 11,12 and 15 at https://arxiv.org/pdf/2106.09685.pdf
            # adjust eps for FP16 (1e-8 => 1e-4)
            optimizer = optim.AdamW(
                self.model.parameters(), lr=2e-4, weight_decay=0.1, eps=1e-4)

            with torch.cuda.amp.autocast():
                for row in (pbar := tqdm(dataset)):
                    if len(row["dialogue"]) <= 1:
                        continue

                    # TODO: refine dataset to `HUMAN:` and `BRAIN:`

                    batch = self.tokenizer(
                        row["dialogue"], truncation=True, max_length=2048, return_tensors='pt')
                    batch = {k: v.to(device) for k, v in batch.items()}

                    optimizer.zero_grad()
                    out = self.model.forward(**batch,)
                    loss = F.cross_entropy(
                        out.logits[:, :-1, :].flatten(0, -2),
                        batch['input_ids'][:, 1:].flatten(),
                        reduction='mean'
                    )
                    pbar.set_description(f"loss {loss:.4f}")  # TODO: disable
                    loss.backward()
                    optimizer.step()

            # Print the statistics of the epoch
            # TODO: train_loss, val_loss, val_accuracy
            print('Completed training batch', epoch)

        # self.model.eval()  # TODO: optimize

        """save new model"""
        self.adapters = get_adapters(self.model)  # TODO: check: is it needed?
        self.version = self.adapters_hash(self.adapters)
        self.save_adapters(self.version)

        return self.version

    def test(self, dataset, version=None, **kwargs):
        pass

    def save_adapters(self, version):
        torch.save(self.adapters, self._get_adapters_path(version))
        # print(f"Adapters version {version} Saved.")

    def load_adapters(self, version):
        if version is not None and self.version != version:
            self.adapters = torch.load(self._get_adapters_path(version))
            set_adapters(self.model, self.adapters)
            # print(f"Adapters version {version} Loaded.")

    def _get_adapters_path(self, version):
        ADAPTERS_PATH = f"{self.path}/adapters"
        os.makedirs(ADAPTERS_PATH, exist_ok=True)
        return f"{ADAPTERS_PATH}/{version}.pt"

    def aggregate(self, versions: list, weights: list):
        # models should be located at cpu

        if len(versions) != len(weights):
            return
        if len(versions) <= 1:
            return

        models = [
            torch.load(
                self._get_adapters_path(path),
                map_location=torch.device('cpu')
            ) for path in versions
        ]

        weights = np.array(weights) / sum(weights)

        aggregated_model = dict()

        for instance, module in models[0].items():
            aggregated_state_dict = dict()
            model_state_dict = module.state_dict()

            for name, param in model_state_dict.items():
                s = Variable(torch.Tensor([weights[0]]).double())
                aggregated_state_dict[name] = param.double().mul(
                    s.expand(param.size())).half()

            aggregated_model[instance] = aggregated_state_dict

        for i, model in enumerate(models[1:]):
            for instance, module in model.items():
                model_state_dict = module.state_dict()

                for name, param in model_state_dict.items():
                    a = aggregated_model[instance][name]

                    s = Variable(torch.Tensor([weights[i]]).double())
                    p = param.double().mul(s.expand(param.size())).half()

                    aggregated_model[instance][name] = a.add(p)

        # set adapters
        for k, v in aggregated_model.items():
            self.adapters[k].load_state_dict(v)
        set_adapters(self.model, self.adapters)

        """save aggregated model"""
        self.adapters = get_adapters(self.model)  # TODO: check: is it needed?
        self.version = self.adapters_hash(self.adapters)
        self.save_adapters(self.version)

        return self.version


if __name__ == "__main__":
    import os  # nopep8
    import sys  # nopep8
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))  # nopep8
    from net.gptj_lora import gptj_lora  # nopep8

    import datasets
    from datasets import load_dataset
    datasets.logging.set_verbosity_error()

    def print_sample(bot, num=3):
        for i in range(num):
            chat = "Hello, World!"
            print("="*64)
            # print(torch.seed())
            print(">>>", bot(chat, seed=(950327+i)))
            # print(">>>", chatbot(chat))
            print("="*64)

    config_0, tokenizer_0, model_0 = gptj_lora(
        "models/36eca1e38b0d04afd013a735f4af49f77c15fbb1e93167ddd083b1548b66ab0a",
        device="cuda:0"
    )
    chatbot_0 = Chatbot(tokenizer_0, model_0)

    config_1, tokenizer_1, model_1 = gptj_lora(
        "models/36eca1e38b0d04afd013a735f4af49f77c15fbb1e93167ddd083b1548b66ab0a",
        device="cuda:1"
    )
    chatbot_1 = Chatbot(tokenizer_1, model_1)

    """aggregate"""

    versions = [
        chatbot_0.version,
        chatbot_1.version
    ]
    chatbot_0.aggregate(
        versions=versions,
        weights=[3, 2]
    )

    """train"""

    train_dataset = load_dataset("samsum", split='train[1%:2%]')
    # valid_dataset = load_dataset("samsum", split='validation')
    chatbot_0.train(
        train_dataset,
        num_epochs=1,
        device="cuda:0",
        seed=1
    )

    print_sample(chatbot_0, num=2)
