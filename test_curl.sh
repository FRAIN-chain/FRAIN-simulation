# Run on the client-side.


# TODO: empty connection to avoid 'Recv failure: Connection reset by peer'


# get results-0
curl -X POST -H 'Content-Type: application/json' http://localhost:30327/chat -d '{"prompt": "Hello, World!", "max_length": 128, "seed":950327}'
curl -X POST -H 'Content-Type: application/json' http://localhost:30327/chat -d '{"prompt": "Hello, World!", "max_length": 128, "seed":950328}'


# train-1
curl -X POST -H 'Content-Type: application/json' http://localhost:30327/train -d '{"from": 0, "to": 10}'

# get results-1
curl -X POST -H 'Content-Type: application/json' http://localhost:30327/chat -d '{"prompt": "Hello, World!", "max_length": 128, "seed":950327}'
curl -X POST -H 'Content-Type: application/json' http://localhost:30327/chat -d '{"prompt": "Hello, World!", "max_length": 128, "seed":950328}'


# train-2
curl -X POST -H 'Content-Type: application/json' http://localhost:30327/train -d '{"from": 10, "to": 20, "base":0}'

# get results-2
curl -X POST -H 'Content-Type: application/json' http://localhost:30327/chat -d '{"prompt": "Hello, World!", "max_length": 128, "seed":950327}'
curl -X POST -H 'Content-Type: application/json' http://localhost:30327/chat -d '{"prompt": "Hello, World!", "max_length": 128, "seed":950328}'


# train-3
curl -X POST -H 'Content-Type: application/json' http://localhost:30327/train -d '{"from": 20, "to": 30, "base":1}'

# get results-3
curl -X POST -H 'Content-Type: application/json' http://localhost:30327/chat -d '{"prompt": "Hello, World!", "max_length": 128, "seed":950327}'
curl -X POST -H 'Content-Type: application/json' http://localhost:30327/chat -d '{"prompt": "Hello, World!", "max_length": 128, "seed":950328}'
