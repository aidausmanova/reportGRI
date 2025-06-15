#!/bin/bash
#SBATCH --gpus-per-node=2
#SBATCH --constraint=48GB
#SBATCH --job-name=pdfparse
#SBATCH -o /storage/usmanova/reportGRI/backend/logs/run_parse_%j.out # STDOUT

export CUDA_VISIBLE_DEVICES=0,1
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export EASYOCR_MODULE_PATH='/storage/usmanova/.EasyOCR/'

python ./routers/parse_docling.py --report 'AstraZeneca Sustainability 2023'