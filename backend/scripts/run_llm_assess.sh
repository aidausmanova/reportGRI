#!/bin/bash
#SBATCH --gpus-per-node=1
#SBATCH --constraint=48GB
#SBATCH --job-name=gri
#SBATCH -o /storage/usmanova/reportGRI/backend/logs/run_eval_%j.out # STDOUT

export CUDA_VISIBLE_DEVICES=0,1
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export OPENAI_API_KEY
export BASE_URL

python ./routers/llm_match.py \
    --model 'gpt-3.5-turbo-1106' \
    --report 'astrazeneca-sustainability-2023' \
    --run_type 'zero-shot'