import torch


class Bot():
    INIT_SEED = 42

    def __init__(self, tokenizer, model, path="models/default"):
        self.tokenizer = tokenizer
        self.model = model

        self.path = path

    def inference(self, prompt, temperature=0.9, max_length=128, device='cuda'):
        with torch.no_grad():
            tokens = self.tokenizer.encode(
                prompt, return_tensors='pt'
            ).to(device=device, non_blocking=True)
            gen_tokens = self.model.generate(
                tokens,
                do_sample=True,
                temperature=temperature,
                max_length=len(prompt) + max_length,
                pad_token_id=self.tokenizer.eos_token_id  # suppress warning
            )
        return self.tokenizer.batch_decode(gen_tokens)[0]

    def inference_with_seed(self, prompt, temperature=0.9, max_length=128, seed=INIT_SEED, device='cuda'):
        torch.manual_seed(seed)
        return self.inference(prompt, temperature=temperature, max_length=max_length, device=device)

    # def train(self, dataset, num_epochs=2):
    #     pass

    # def test(self, dataset):
    #     pass
