import argparse


def argparser():
    parser = argparse.ArgumentParser(description='Hyperparameters')

    parser.add_argument('--dataset', metavar='D', type=str, default="samsum",
                        help='Dataset to use')

    parser.add_argument('--port', metavar='P', type=int, default=30327,
                        help='Port number')

    # TODO: select bot (chatbot, sqlbot, etc.)

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = argparser()
    print(args)
