import re
import nltk
import spacy
import json
from tqdm import tqdm
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

nltk.download('punkt')
nltk.download('stopwords')
spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")

boilerplate_patterns = [
    r"we are committed to[^.]*\.",
    r"is committed to[^.]*\.",
    r"we continue to [^.]*\.",
    r"in line with our values[^.]*\.",
    r"as part of our continuous improvement[^.]*\.",
    r"our mission is to[^.]*\.",
    # r"^this report.*?\.",
    r"^read more about[^.]*\.",
    r"^see more about[^.]*\.",
    r"^you can find[^.]*\.",
    r"^we strive to[^.]*\.",
    r"for more details[^.]*\."
]

def save_json(path, content):
    with open(path, 'w') as f:
        json.dump(content, f, indent=2)

def read_json(path):
    with open(path) as json_data:
        content = json.load(json_data)
    return content

def get_gri_standards(path):
    with open(path, "r") as file:
        gri_data = json.load(file)

    gri_standards_corpus = {}
    gri_list = []
    for gri in gri_data:
        gri_standards_corpus[gri['idx']] = f"{gri['title']} ({', '.join(gri['topics'])}). {gri['description']}"
        gri_list.append(f"{gri['idx']}: {gri['description']}")

    return gri_standards_corpus, gri_list

def get_gri_disclosures(path):
    with open(path, "r") as file:
        gri_data = json.load(file)

    gri_disclosures_corpus = {}
    gri_disclosures_list = []
    for gri in gri_data:
        disclosures = gri["disclosures"]
        for disclosure in disclosures:
            gri_disclosures_corpus[disclosure['idx']] = f"{disclosure['title']} ({disclosure['description']})"
            gri_disclosures_list.append(f"{disclosure['idx']}: {disclosure['description']}")
    return gri_disclosures_corpus, gri_disclosures_list

def get_gri_topic(gri_disclosure):
    gri_2_organization = ["gri_2-1", "gri_2-2", "gri_2-3", "gri_2-5", "gri_2-6", "gri_2-7", "gri_2-8"]
    gri_2_governance = ["gri_2-9", "gri_2-10", "gri_2-11", "gri_2-12", "gri_2-13", "gri_2-14"]
    gri_2_ethics = ["gri_2-23", "gri_2-24"]
    gri_2_strategy = ["gri_2-22", "gri_2-25", "gri_2-26", "gri_2-27", "gri_2-28", "gri_2-29"]

    if gri_disclosure.startswith("gri_2-"):
        if gri_disclosure in gri_2_organization:
            return "gri_2-organization"
        elif gri_disclosure in gri_2_governance:
            return "gri_2-governance"
        elif gri_disclosure in gri_2_ethics:
            return "gri_2-ethics"
        elif gri_disclosure in gri_2_strategy:
            return "gri_2-strategy"
    else:
        split1 = gri_disclosure.split("_")
        gri_hl = f"{split1[0]}_{split1[1].split('-')[0]}"
        return gri_hl

def get_section_passages(corpus):
    section_data = []
    cur_section = corpus[0]['idx'].split("_")[0]
    cur_title = corpus[0]['title']
    # section_docs = [f"{corpus[0]['title']}\n{corpus[0]['text']}"]
    section_corpus = {
        cur_section: f"{corpus[0]['title']}\n{corpus[0]['text']}"
    }
    section_data.append({"section_idx": cur_section, "title": cur_title, "text": corpus[0]['text'], "gri": []})

    for i in range (1, len(corpus)):
        chunk = corpus[i]
        section_id = chunk['idx'].split("_")[0]
        if chunk['idx'].startswith(cur_section):
            section_corpus[cur_section] += f"\n{chunk['text']}"
            section_data[-1]["text"] += f"\n{chunk['text']}" 
            # section_docs[-1] += f"\n{chunk['text']}"
        else:
            # section_docs.append(f"{chunk['title']}\n{chunk['text']}")
            cur_section = section_id
            cur_title = chunk['title']
            section_corpus[cur_section] = f"{chunk['title']}\n{chunk['text']}"
            section_data.append({"section_idx": cur_section, "title": cur_title, "text": chunk['text'], "gri": []})
        
    print("Section corpus length: ", len(section_corpus))
    return section_corpus, section_data


# def get_section_passages(corpus):
#     cur_section = corpus[0]['idx'].split("_")[0]
#     # section_docs = [f"{corpus[0]['title']}\n{corpus[0]['text']}"]
#     section_corpus = {
#         cur_section: f"{corpus[0]['title']}\n{corpus[0]['text']}"
#     }

#     for i in range (1, len(corpus)):
#         chunk = corpus[i]
#         section_id = chunk['idx'].split("_")[0]
#         if chunk['idx'].startswith(cur_section):
#             section_corpus[cur_section] += f"\n{chunk['text']}"
#             # section_docs[-1] += f"\n{chunk['text']}"
#         else:
#             # section_docs.append(f"{chunk['title']}\n{chunk['text']}")
#             cur_section = section_id
#             section_corpus[cur_section] = f"{chunk['title']}\n{chunk['text']}"
#     print("Section corpus length: ", len(section_corpus))
#     return section_corpus

def preprocess_paragraph(section_corpus):
    stop_words = set(stopwords.words('english'))
    max_sentences = 5
    new_section_corpus = section_corpus

    with open("data/taxonomies/gri_taxonomy_full_new.json", "r") as file:
        gri_data = json.load(file)

    disclosure_keywords = {}
    for gri in gri_data:
        disclosure_keywords[gri['idx']] = gri['topics']

    for section in tqdm(new_section_corpus):
        for pattern in boilerplate_patterns:
            paragraph = re.sub(pattern, '', section['text'], flags=re.IGNORECASE)
        sentences = sent_tokenize(paragraph)
        
        keywords = []
        for disclosure_keyword in disclosure_keywords.values():
            keywords.extend(disclosure_keyword)

        keyword_filtered = [
            s for s in sentences if any(kw.lower() in s.lower() for kw in keywords)
        ]

        cleaned_sentences = []
        for sent in keyword_filtered:
            words = word_tokenize(sent)
            non_stop = [w for w in words if w.lower() not in stop_words and w.isalnum()]
            if len(non_stop) >= 3:
                cleaned_sentences.append(sent)
        # print("Cleaned: ", len(cleaned_sentences))
        if not cleaned_sentences:
            cleaned_sentences = keyword_filtered
        
        if len(cleaned_sentences) <= max_sentences:
            section['text'] = " ".join(cleaned_sentences)
        else:
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(cleaned_sentences)
            sentence_scores = np.asarray(tfidf_matrix.sum(axis=1)).ravel()
            top_indices = sentence_scores.argsort()[-max_sentences:][::-1]
            top_sentences = [cleaned_sentences[i] for i in sorted(top_indices)]
            section['text'] = " ".join(top_sentences)
    return new_section_corpus

def process_llm_response(report_name):
    with open(f"data/reports/{report_name}/gri_coverage_evaluation.json", "r") as f:
        data = json.load(f)

    with open(f"data/reports/{report_name}/{report_name}_corpus.json", "r") as f:
        section_corpus = json.load(f)
    section_index_corpus = {}
    for passage in section_corpus:
        section_index_corpus[passage['section_idx']] = (passage['title'], passage['text'])

    with open(f"data/taxonomies/gri_taxonomy_full_new.json", "r") as f:
        gri_data = json.load(f)

    gri_disclosure_titles = {}
    gri_topic_titles = {}
    for gri_standard in tqdm(gri_data):
        gri_topic_titles[gri_standard['idx']] = gri_standard['title']
        for gri_disclosure in gri_standard['disclosures']:
            gri_disclosure_titles[gri_disclosure['idx']] = (gri_disclosure['code'], gri_disclosure['title'])

    completeness_pattern = re.compile(r'''(?i)completeness[\\]?[\s"']*[:=]?[\s"']*(?P<completeness>\d+)''', re.VERBOSE)
    materiality_pattern = re.compile(r'''(?i)materiality[\\]?[\s"']*[:=]?[\s"']*(?P<materiality>\d+)''', re.VERBOSE)

    results = []
    for row in data:
        standard_idx = get_gri_topic(row['disclosure'])
        output_text = row['response']
        responses = output_text.split("\n")
        completeness_score, materiality_score = None, None
        comment = ""
        
        completeness_match = completeness_pattern.search(row['response'])
        materiality_match = materiality_pattern.search(row['response'])
        
        if completeness_match:
            # print("Completeness:", completeness_match.group(0))
            output_text = re.sub(completeness_pattern, '', output_text)
            matches = re.findall(r'\d+', completeness_match.group(0))
            if completeness_score == None and matches:
                completeness_score = int(matches[0])
        if materiality_match:
            # print("Materiality:", materiality_match.group(0))
            output_text = re.sub(materiality_pattern, '', output_text)
            matches = re.findall(r'\d+', materiality_match.group(0))
            if materiality_score == None and matches:
                materiality_score = int(matches[0])

        paragraphs = []
        for section_id in row['section_ids']:
            section = section_index_corpus[section_id]
            paragraphs.append(
                {
                'section_idx': section_id,
                'title': section[0],
                'text': section[1]
                }
            )
        
        comment += output_text.replace('comment', '').replace('Comment', '').replace('"', '').replace(':', '').replace(",\n", '').replace("\n", '').replace("  ", '').replace("{", '').replace("}", '').replace(",,", '').replace("```", '').replace("json", '')
        results.append(
            {
                'topic': standard_idx,
                'topic_title': gri_topic_titles[standard_idx],
                'disclosure': row['disclosure'],
                'disclosure_code': gri_disclosure_titles[row['disclosure']][0],
                'disclosure_title': gri_disclosure_titles[row['disclosure']][1],
                'section_ids': row['section_ids'],
                'completeness': completeness_score if completeness_score else 0,
                'materiality': materiality_score if materiality_score else 0,
                'comment': comment,
                'paragraphs': paragraphs
                
            }
        )
    
    with open(f"data/reports/{report_name}/{report_name}_final.json", "w") as f:
        json.dump(results, f)
