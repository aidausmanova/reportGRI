import os
import sys
import json
import torch
import argparse
from tqdm import tqdm
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import CrossEncoder
from transformers import AutoTokenizer, AutoModelForSequenceClassification

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.utils import *

device = "cuda" if torch.cuda.is_available() else "cpu"


def paragraph2gri_matching(section_index_corpus, gri_data, model, tokenizer):
    msmarco_rankings = {}
    msmarco_ranking_rows = []

    passage_ids = list(section_index_corpus.keys())
    paragraphs = list(section_index_corpus.values())

    for gri_standard in tqdm(gri_data):
        for gri_disclosure in gri_standard["disclosures"]:
            gri_description = (
                gri_disclosure["title"] + " " + gri_disclosure["description"]
            )
            gri_texts = [gri_description] * len(paragraphs)
            inputs = tokenizer(
                gri_texts,
                paragraphs,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=512,
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            model.eval()
            with torch.no_grad():
                # scores = model(**inputs).logits.squeeze().tolist()
                scores = model(**inputs).logits
                if scores.dim() == 1:
                    scores = scores.tolist()
                else:
                    scores = scores.squeeze(1).tolist()

            scored_passages = list(zip(passage_ids, scores))
            scored_passages.sort(key=lambda x: x[1], reverse=True)

            msmarco_rankings[gri_disclosure["idx"]] = scored_passages
            for passage_id, score in scored_passages:
                msmarco_ranking_rows.append(
                    {
                        "gri_standard": gri_standard["idx"],
                        "gri_disclosure": gri_disclosure["idx"],
                        "section_idx": passage_id,
                        "score": score,
                    }
                )
    return msmarco_ranking_rows


def run_retrieval(uploaded_report_folder, report_name):
    # Prepare report data
    with open(
        os.path.join(uploaded_report_folder, "corpus.json"), "r"
    ) as f:
        section_corpus = json.load(f)
    section_index_corpus = {}
    for passage in section_corpus:
        section_index_corpus[passage["section_idx"]] = (
            f"{passage['title']}\n{passage['text']}"
        )

    with open("data/taxonomies/gri_taxonomy_full_new.json", "r") as file:
        gri_data = json.load(file)

    model_name = "cross-encoder/ms-marco-MiniLM-L12-v2"
    rerank_tokenizer = AutoTokenizer.from_pretrained(model_name)
    rerank_model = AutoModelForSequenceClassification.from_pretrained(model_name)
    rerank_model = rerank_model.to(device)

    matchings = paragraph2gri_matching(
        section_index_corpus, gri_data, rerank_model, rerank_tokenizer
    )
    similarity_df = pd.DataFrame(matchings)
    top_similarity_df = similarity_df[similarity_df.score >= 0.2]

    data_dict = []
    for gri_disclosure in top_similarity_df["gri_disclosure"].unique():
        section_ids = list(
            top_similarity_df[top_similarity_df.gri_disclosure == gri_disclosure][
                "section_idx"
            ].tolist()
        )
        scores = list(
            set(
                top_similarity_df[top_similarity_df.gri_disclosure == gri_disclosure][
                    "score"
                ].tolist()
            )
        )
        data_dict.append(
            {
                "gri_disclosure": gri_disclosure,
                "section_ids": section_ids,
                "scores": scores,
            }
        )

    top_retrieved_paragraphs_json_file = os.path.join(
        uploaded_report_folder, "top_retrieved_paragraphs.json"
    )
    with open(top_retrieved_paragraphs_json_file, "w") as f:
        json.dump(data_dict, f)
    print(f"[INFO] Retrieval output saved to {top_retrieved_paragraphs_json_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--report", type=str)
    args = parser.parse_args()

    # run_retrieval(args.report)
