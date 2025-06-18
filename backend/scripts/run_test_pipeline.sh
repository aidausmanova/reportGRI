#!/bin/bash
#SBATCH --gpus-per-node=1
#SBATCH --constraint=48GB
#SBATCH --job-name=gri_match
#SBATCH -o /reportGRI/backend/logs/run_test_%j.out # STDOUT

export CUDA_VISIBLE_DEVICES=0,1
export EASYOCR_MODULE_PATH='/storage/usmanova/.EasyOCR/'

python ./test_piepeline.py --report 'HM Sustainability 2022' --llm 'gpt-3.5-turbo-1106' --run_type 'zero-shot'