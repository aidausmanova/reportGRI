import os
import sys

sys.path.append(os.getcwd())
import re
import time
import argparse
import logging
from pathlib import Path
import json
import docling
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
    EasyOcrOptions,
)
import warnings
import shutil
from utils.utils import *

warnings.filterwarnings("ignore")

_log = logging.getLogger(__name__)


def clean_text(text, rgx_list=[]):
    rgx_list = ["<!-- image -->", "; ->", "&gt", "amp;"]
    new_text = text
    for rgx_match in rgx_list:
        new_text = re.sub(rgx_match, "", new_text)
    return new_text


def parse(uploaded_report_folder, report_name):
    logging.basicConfig(level=logging.INFO)
    input_doc_path = os.path.join(uploaded_report_folder, report_name + ".pdf")

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = False
    pipeline_options.table_structure_options.do_cell_matching = False

    pipeline_options.ocr_options.lang = ["en"]
    # pipeline_options.ocr_options.download_enabled = False
    # pipeline_options.ocr_options.model_storage_directory = "docling/models/EasyOcr"

    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=4, device=AcceleratorDevice.AUTO
    )

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    _log.info("Document conversion started")

    start_time = time.time()
    conv_result = doc_converter.convert(input_doc_path)
    end_time = time.time() - start_time

    _log.info(f"Document converted in {end_time:.2f} seconds.")

    # Export Text format:
    with open(
        os.path.join(uploaded_report_folder, report_name + ".txt"),
        "w",
        encoding="utf-8",
    ) as fp:
        text = conv_result.document.export_to_text()
        fp.write(conv_result.document.export_to_text())
    _log.info("Converted document saved as txt file")

    # Export Markdown format:
    # with (os.path.join(uploaded_report_folder, report_name+ ".md").open("w", encoding="utf-8") as fp:
    #     fp.write(conv_result.document.export_to_markdown())

    return text


def download_models():
    docling.utils.model_downloader.download_models(output_dir=Path("docling/models"))
    print("models downloaded successfully.")


def run_parser(uploaded_report_folder, report_name):
    print(f"[INFO] run parser - {report_name}")
    file_name = "-".join(report_name.split())

    print(f"[INFO] Parsing {report_name}")
    text = parse(uploaded_report_folder, report_name)

    print("[INFO] Text preprocessing ...")
    p = re.compile("##.*\n")
    section_titles = re.findall(p, text)
    mod_section_titles = []
    for title in section_titles:
        mod_section_titles.append(title[3 : len(title) - 1])

    sections = text.split("##")
    sections.pop(0)
    print(f"[INFO] # sections: {len(sections)}, # titles: {len(mod_section_titles)}")
    # assert(len(sections) == len(mod_section_titles))

    chunked_paragraphs = []
    for idx, (section, title) in enumerate(
        zip(sections[: len(mod_section_titles)], mod_section_titles)
    ):
        # Append paragraph data
        sec_text = section[len(title) + 2 :]
        sec_text = sec_text.split(". ")
        if len(sec_text) > 2:
            sec_text = ".".join(sec_text).replace("\n", "").replace("\u25cf", "")
            if not any(row["title"] == title for row in chunked_paragraphs):
                chunked_paragraphs.append(
                    {
                        "title": title,
                        "text": sec_text,
                        "section_idx": file_name + "-" + str(idx),
                    }
                )
            else:
                for row in chunked_paragraphs:
                    if row["title"] == title:
                        row["text"] += sec_text

    # output_dir = os.path.dirname(report_file)
    corpus_file = os.path.join(uploaded_report_folder, report_name+ "-corpus.json")
    with open(corpus_file, "w") as f:
        json.dump(chunked_paragraphs, f, indent=4)

    print(f"[INFO] Document chunked and saved as json: {corpus_file}")
    _log.info(f"Document chunked and saved as json:  at {corpus_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--report", type=str)
    print("PATH: ", os.getcwd())

    args = parser.parse_args()
    report_file = args.report

    # run_parser(report_file)
