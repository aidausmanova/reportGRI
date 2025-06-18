#!/bin/bash
#SBATCH --gpus-per-node=1
#SBATCH --constraint=48GB
#SBATCH --job-name=gri
#SBATCH -o /reportGRI/backend/logs/run_retrieve_%j.out # STDOUT

export CUDA_VISIBLE_DEVICES=0,1
export VLLM_WORKER_MULTIPROC_METHOD=spawn

python ./routers/retrieval.py \
    --report 'astrazeneca-sustainability-2023'