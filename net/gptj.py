import torch
# from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import AutoTokenizer, AutoModelForCausalLM


"""load model"""


tokenizer = AutoTokenizer.from_pretrained(
    "EleutherAI/gpt-j-6B"
)
tokenizer.add_special_tokens({'pad_token': tokenizer.eos_token})
model = AutoModelForCausalLM.from_pretrained(
    "EleutherAI/gpt-j-6B", revision="float16",
    torch_dtype=torch.float16, low_cpu_mem_usage=True
).to(device='cuda', non_blocking=True)

# _ = model.eval()  # by default
print("Model Loaded.")


if __name__ == "__main__":
    import os  # nopep8
    import sys  # nopep8
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))  # nopep8
    sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))+'/bot')  # nopep8
    from bot.chatbot import Chatbot  # nopep8

    chatbot = Chatbot(tokenizer, model)

    print(chatbot.model)
