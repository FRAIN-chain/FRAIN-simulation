import os  # nopep8
import sys  # nopep8
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/bot')  # nopep8
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/net')  # nopep8


"""flask"""

from flask import Flask, request, jsonify  # nopep8
from flask_cors import CORS  # nopep8

app = Flask(__name__)
CORS(app)


"""bot"""

from bot.chatbot import Chatbot  # nopep8
from net.gptj_lora import gptj_lora  # nopep8

config, tokenizer, model = gptj_lora(
    "models/36eca1e38b0d04afd013a735f4af49f77c15fbb1e93167ddd083b1548b66ab0a"
)
chatbot = Chatbot(tokenizer, model)


"""init"""

from datasets import load_dataset


"""server"""

@app.route('/chat', methods=['POST'])
def chat():
    params = request.get_json()
    result = chatbot(**params)
    return jsonify(dict({
        'result': result
    }))

@app.route('/train', methods=['POST'])
def train():
    params = request.get_json()
    params['dataset'] = load_dataset(
        "samsum",
        split=f"train[{params['from']}:{params['to']}]"
    )
    prev_version = chatbot.version
    curr_version = chatbot.train(**params)
    return jsonify(dict({
        'previous': prev_version,
        'current': curr_version
    }))

@app.route('/aggregate', methods=['POST'])
def aggregate():
    params = request.get_json()
    prev_version = chatbot.version
    curr_version = chatbot.aggregate(**params)
    return jsonify(dict({
        'previous': prev_version,
        'current': curr_version
    }))


"""main"""

if __name__ == "__main__":
    # argparse
    from args import argparser

    args = argparser()
    print(args)

    # init
    train_dataset = load_dataset(args.dataset)

    # run
    app.run(host='0.0.0.0', port=args.port)
