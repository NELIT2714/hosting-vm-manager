# vm-manager

gRPC service that receives VM management requests from the API and routes them to node agents.

## Stack

- **Python 3.13**
- **gRPC + TLS** — secure communication with API and node agents

## Architecture

```
API (Spring Boot) ──(gRPC/TLS)──> vm-manager ──(gRPC/TLS)──> node-agent
```

## Project structure

```
vm-manager/
├── main.py              # gRPC server
├── core/
│   ├── node_client.py   # gRPC client for node agents
│   └── scheduler.py     # node selection logic
├── proto/               # generated protobuf files
├── certs/               # TLS certificates (not in git)
├── .env                 # environment config (not in git)
└── .gen-proto.sh        # proto generation script
```

## How it works

API sends CreateVM request with node addresses and VM parameters. VM Manager picks the best node via Scheduler and forwards the request to the node agent.

```
API: CreateVM(vm_name, ram_mb, vcpus, disk_gb, nodes=[...])
    ↓
Scheduler picks best node
    ↓
NodeClient sends CreateVM to node agent
```

## Environment

```env
GRPC_PORT=50052

CERTS_CA_PATH=certs/ca.crt
CERTS_CLIENT_PATH=certs/client.crt
CERTS_CLIENT_KEY_PATH=certs/client.key

CERTS_SERVER_PATH=certs/server.crt
CERTS_SERVER_KEY_PATH=certs/server.key
```
