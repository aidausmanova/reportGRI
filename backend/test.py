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
    # report_name = run_parser(report)


    print("Start disclosure-paragraph alignment")
    report_name = "microsoft-sustainability-2022"
    run_retrieval(report_name)
    
    print("Start report assessment")
    run_llm(report_name, model, is_few_shot)
    process_llm_response(report_name)

    print("Finished exxecution")