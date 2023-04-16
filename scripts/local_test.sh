#!bin/bash

kubectl port-forward service/el-embedded-trigger-listener 8080

curl -X POST http://localhost:8080 -H 'Content-Type: application/json' -d '{ }'