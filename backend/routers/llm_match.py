import argparse
import os
import re
import sys
sys.path.append(os.getcwd())
import torch
import csv
import json
import pandas as pd
from tqdm import tqdm
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    AutoModelForCausalLM,
    pipeline
)

from utils.utils import *
from utils.api_utils import *
from utils.prompt_utils import *

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

def extract_code(response):
    response_content = response.split()
    code_list = []
    for i in range(len(response_content)):
        if response_content[i].startswith("gri_"):
            code_list.append(response_content[i].lower())


    # p = re.compile("##.*\n")
    # section_titles = re.findall(p, text)
    return list(set(code_list))

def extract_score(response):
    response_content = response.lower().split()
    code_list = []
    for i in range(len(response_content)):
        if response_content[i].startswith("score"):
            code_list.append(response_content[i+1].lower())


    # p = re.compile("##.*\n")
    # section_titles = re.findall(p, text)
    return list(set(code_list))

def process_openai(section_corpus, gri_standards, gri_disclosures, model, report_name, is_few_shot):
    # os.makedirs(os.path.dirname(f"output/{report_name}/gri_matches/{model}/{report_name}/"), exist_ok=True)
    for paragraph in tqdm(section_corpus):
        standard_messages = message_format(gri_standard_prompt, is_few_shot,
                                  {'paragraph': paragraph['text'], 'standards': "\n".join(gri_standards)})
        responses = get_response(standard_messages, model="gpt-3.5-turbo-1106", max_tokens=128, temperature=0.7, candidate_n=1)
        # responses = get_api_request(messages, max_tokens=256)
        gri_matchings = extract_code(responses)

        standard_output_entry = {
            'section_idx': paragraph['section_idx'],
            'section_title': paragraph['title'],
            "gri": gri_matchings,
            'response':  responses,
        }
        with open(f"data/gri_matches/{model}/{report_name}/gri_standards.json", 'a') as f:
            f.write(json.dumps(standard_output_entry))
            f.write('\n')

        for gri_standard in gri_matchings:
            disclosure_messages = message_format(gri_disclosure_prompt.format(""), is_few_shot,
                                  {'paragraph': paragraph['text'], 'disclosures': "\n".join(gri_disclosures)})
            responses = get_response(disclosure_messages, model="gpt-3.5-turbo-1106", max_tokens=128, temperature=0.7, candidate_n=1)
            # responses = get_api_request(messages, max_tokens=256)
            gri_disclosure_matchings = extract_code(responses)
            scores = extract_score(responses)

            disclosure_output_entry = {
                'section_idx': paragraph['section_idx'],
                'section_title': paragraph['title'],
                "gri": gri_disclosure_matchings,
                "score": scores,
                'response':  responses,
            }
            with open(f"output/{report_name}/gri_discosures.json", 'a') as f:
                f.write(json.dumps(disclosure_output_entry))
                f.write('\n')
    print(f"[INFO] GRI matches are saved at data/gri_matches/{model}/gri_completeness_{model}.json")

def process_causal_lm(section_corpus, gri_docs, model, tokenizer, report_name):
    os.makedirs(os.path.dirname(f"data/gri_matches/{model}/"), exist_ok=True)

    prompt_instructions = """You are an expert in corporate disclosure with vast knowledge of climate change, human rights, ethics and social science, and expert in Global Reporting Initiative (GRI).
    Given paragraph predict the GRI indicator out of the following 22 options. Return the indicator code that best addresses paragraph content.
    GRIs:"""

    gri_instructions = "\n".join(gri_docs)

    print(f"[INFO] Start GRI prediction for # {len(section_corpus)} pragraphs")
    tokenizer.pad_token_id = model.config.eos_token_id[0]
    pipe = pipeline("text-generation", 
                    model=model,
                    tokenizer=tokenizer,
                    return_full_text=False,
                    max_new_tokens=1000,
                    do_sample=False,
                    trust_remote_code=True,
                    truncation=True,
                    device=device)
    
    # with open(output_path, 'wt') as out_file:
    #     tsv_writer = csv.writer(out_file, delimiter='\t')
    #     for idx, row in tqdm(data.iterrows()):
    #         messages=[{"role":"system","content":prompt_instructions},
    #                 {"role":"user","content":f"Claim: {row['claim']} \nEvidence: {row['abstract']}"}]
            
    #         output = pipe(messages)
    #         label_prediction = extract_prediction(output[0]["generated_text"])

    #         tsv_writer.writerow([row['claim_id'], row['claim'], row['abstract_id'], row['abstract'], row['rank'], label_prediction])

    for entry in tqdm(section_corpus):
        messages=[{"role":"system","content":prompt_instructions+gri_instructions},
                    {"role":"user","content":f"Paragraph: {entry['text']}"}]
            
        output = pipe(messages)
        # label_prediction = extract_prediction(output[0]["generated_text"])

        entry = {
            'section_idx': entry['section_idx'],
            'section_title': entry['title'],
            'gri':  output[0]['generated_text']
        }
        with open(f"data/gri_matches/{model}/{report_name}_gri.json", 'a') as f:
            f.write(json.dumps(entry))
            f.write('\n')

    return 0    

def evaluate_disclosure_coverage(report_name, retrieval_results, gri_disclosure_corpus, section_index_corpus, is_few_shot):
    print("[INFO] Start disclosure coverage evaluation")
    evaluation_results = []
    for row in tqdm(retrieval_results):
        gri_disclosure = gri_disclosure_corpus[row["gri_disclosure"]]
        paragraphs = ""
        for section_idx in row['section_ids']:
            paragraphs += f"\n{section_index_corpus[section_idx]}"
        if len(paragraphs) > 5:
            standard_messages = message_format(scoring_agent_disclosure_prompt, is_few_shot,
                                            {'disclosure': gri_disclosure, 'paragraphs': paragraphs})

            responses = get_response(standard_messages, model="gpt-3.5-turbo-1106", max_tokens=128, temperature=0.7, candidate_n=1)
            disclosure_output_entry = {
                # 'gri_standard': row['gri_standard'],
                'disclosure': row['gri_disclosure'],
                "section_ids": row['section_ids'],
                'response':  responses,
            }
            evaluation_results.append(disclosure_output_entry)
    with open(f"data/reports/{report_name}/gri_coverage_evaluation.json", 'w') as f:
        json.dump(evaluation_results, f)

def run_llm(report_name, model_name, is_few_shot):
    gri_standards_corpus, gri_standards = get_gri_standards("data/taxonomies/gri_taxonomy_full_new.json")
    gri_disclosure_corpus, gri_disclosures = get_gri_disclosures("data/taxonomies/gri_taxonomy_full_new.json")
    print("[INFO] GRI taxonomy loaded")

    corpus_path = f"data/reports/{report_name}/{report_name}_corpus.json"
    with open(corpus_path, "r") as f:
        corpus = json.load(f)
    # section_docs, section_corpus = get_section_passages(corpus)
    section_corpus = corpus

    new_section_corpus = preprocess_paragraph(section_corpus)
    section_index_corpus = {}
    for passage in new_section_corpus:
        section_index_corpus[passage['section_idx']] = passage['text']

    with open(f'data/reports/{report_name}/top_retrieved_paragraphs.json', 'r') as f:
        data = json.load(f)
    print("[INFO] Report corpus loaded")

    if 'llama' in model_name:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        process_causal_lm(section_corpus, gri_standards, model, tokenizer, report_name, "")
    else:
        # process_openai(section_corpus, gri_standards, gri_disclosures, model_name, report_name, is_few_shot)
        evaluate_disclosure_coverage(report_name, data, gri_disclosure_corpus, section_index_corpus, is_few_shot)

    print("Finished execution.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--model", type=str)
    parser.add_argument("--report", type=str, help="Name of the processed report file")
    parser.add_argument("--run_type", type=str, default="zero-shot")
    # parser.add_argument("--gri_level", type=str, default="standard", help="Match with standard or disclosure")

    args = parser.parse_args()

    model_name = args.model
    report_name = args.report
    is_few_shot = True if args.run_type == "few-shot" else False

    run_llm(report_name, model_name, is_few_shot)
