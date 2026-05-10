#!/bin/bash
python -m grpc_tools.protoc \
    -Iproto \
    --python_out=proto \
    --grpc_python_out=proto \
    proto/node_agent.proto \
    proto/vm_manager.proto

echo "Proto generated"