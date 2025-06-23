import os
import re
import json
import tqdm
import random
import argparse
import threading
from queue import Queue
# import ipdb
from utils.utils import *
from utils.prompt_utils import *
from routers.parse_docling import run_parser
from routers.retrieval import run_retrieval
from routers.llm_match import run_llm


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--report', type=str, default='')
    parser.add_argument('--llm', type=str, default='meta-llama/Llama-3.1-8B')
    parser.add_argument('--run_type', type=str, default='zero-shot')

    args = parser.parse_args()

    report = args.report
    model = args.llm
    is_few_shot = args.run_type


    print("Start report parsing")
    run_parser("data/reports/original/", report)

    file_name = "-".join(report.lower().split())
    report_folder = f"data/reports/{file_name}/"
    print("Start disclosure-paragraph alignment")
    run_retrieval(report_folder, file_name)

    print("Start report assessment")
    run_llm(report_folder, file_name, model, is_few_shot)
    print("Finished exxecution")
