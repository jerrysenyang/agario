#!/bin/bash
echo "Generating proto grpc files..."
python3 -m grpc_tools.protoc -I=proto/ --python_out=proto/ --grpc_python_out=proto/ proto/game.proto
python3 -m grpc_tools.protoc -I=proto/ --python_out=proto/ --grpc_python_out=proto/ proto/replica.proto
echo "DONE" 