import csv
import os
import shutil
import uuid
import json
from pathlib import Path
from collections import defaultdict
import asyncio
from routers.parse_docling import run_parser

# from traceback import print_tb
from typing import List, Optional, Any

from fastapi import (
    APIRouter,
    Request,
    UploadFile,
    File,
    Response,
    Depends,
    Cookie,
    Body,
    HTTPException,
    Query,
)
from fastapi.responses import FileResponse

router = APIRouter()
DATA_FOLDER = Path("data")

# Ensure the data folder exists
DATA_FOLDER.mkdir(exist_ok=True)


@router.get("/industries")
def get_industries(request: Request):
    session_id = request.headers.get("X-Session-ID", "unknown")
    print(f"[INFO] industries: {session_id}")

    file_path = os.path.join(DATA_FOLDER, "industries_reports.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="industries_reports.csv not found.")

    try:
        industries = set()
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                industries.add(row["industry"])
        return sorted(industries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")


@router.get("/reports/{industry}")
def get_reports_by_industry(industry: str, request: Request):
    session_id = request.headers.get("X-Session-ID", "unknown")
    print(f"[INFO] reports - industry: {session_id}")

    file_path = os.path.join(DATA_FOLDER, "industries_reports.csv")
    orgs = set()
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["industry"] == industry:
                orgs.add(row["organization"])
    return sorted(orgs)


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    session_id = request.headers.get("X-Session-ID", "unknown")
    print(f"[INFO] upload: {session_id}")

    session_folder = os.path.join(DATA_FOLDER, "uploaded_reports", session_id)
    Path(session_folder).mkdir(parents=True, exist_ok=True)

    # get the uploaded file name without extension
    uploaded_report_name = Path(file.filename).stem
    uploaded_report_folder = os.path.join(session_folder, uploaded_report_name)

    if not os.path.exists(uploaded_report_folder):
        Path(uploaded_report_folder).mkdir(parents=True, exist_ok=True)

        uploaded_report = os.path.join(uploaded_report_folder, file.filename)
        with open(uploaded_report, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"[INFO] file copied {uploaded_report}")

        # Parse the uploaded report and generate the json output file
        parsed_file = run_parser(uploaded_report)

    files = list_uploaded_files(session_id)
    return {"my_reports": files, "parsed_file": uploaded_report}


def list_uploaded_files(session_id: str) -> List[str]:
    session_folder = os.path.join(DATA_FOLDER, "uploaded_reports", session_id)
    if not Path(session_folder).exists():
        return []
    return sorted(os.listdir(session_folder))


@router.post("/export")
def export_report_assessment(request: Request):
    session_id = request.headers.get("X-Session-ID", "unknown")
    print(f"[INFO] export: {session_id}")

    session_folder = os.path.join(DATA_FOLDER, "uploaded_reports", session_id)
    for f in Path(session_folder).glob("*.json"):
        session_file = os.path.join(session_folder, f.name)
        return FileResponse(
            path=session_file,
            filename=f.name,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{f.name}"'},
        )


@router.get("/my-reports")
def get_my_reports(request: Request) -> Any:
    session_id = request.headers.get("X-Session-ID", "unknown")
    print(f"[INFO] my-reports: {session_id}")

    return list_uploaded_files(session_id)


@router.post("/chart-data")
def get_chart_data_new(request: Request, body: dict = Body(...)):
    session_id = request.headers.get("X-Session-ID", "unknown")
    print(f"[INFO] chart-data: {session_id}")

    gri_topic_counts = {
        "gri_2": 11,
        "gri_201": 2,
        "gri_301": 3,
        "gri_302": 5,
        "gri_303": 5,
        "gri_304": 4,
        "gri_305": 5,
        "gri_306": 3,
        "gri_307": 2,
        "gri_308": 2,
        "gri_401": 3,
        "gri_403": 4,
        "gri_404": 1,
        "gri_405": 2,
        "gri_413": 1,
        "gri_415": 1,
        "gri_416": 1,
        "gri_418": 1,
    }
    gri_topic_map = {
        "gri_2": "General disclosure",
        "gri_201": "Economic performance",
        "gri_301": "Materials",
        "gri_302": "Energy",
        "gri_303": "Water",
        "gri_304": "Biodiversity",
        "gri_305": "Emissions",
        "gri_306": "Waste",
        "gri_307": "Environmental compliance",
        "gri_308": "Supplier assessment",
        "gri_401": "Employment",
        "gri_403": "Employee safety",
        "gri_404": "Training",
        "gri_405": "Diversity",
        "gri_413": "Communities",
        "gri_415": "Public policy",
        "gri_416": "Customer safety",
        "gri_418": "Customer privacy",
    }
    gri_disclosure_titles = {
        "gri_2-2": "Entities included in report",
        "gri_2-5": "External assurance",
        "gri_2-9": "Governance structure",
        "gri_2-13": "Delegation of responsibility for managing impacts",
        "gri_2-23": "Policy commitments",
        "gri_2-24": "Embedding policy commitments",
        "gri_2-22": "Statement on sustainable development and climate goals",
        "gri_2-25": "Processes to remediate negative impacts",
        "gri_2-27": "Compliance with laws and regulations",
        "gri_2-28": "Membership associations",
        "gri_2-29": "Approach to stakeholder engagement",
        "gri_201-1": "Direct economic value generated",
        "gri_201-2": "Financial implications due to climate change",
        "gri_301-1": "Materials used",
        "gri_301-2": "Recycled input materials used",
        "gri_301-3": "Reclaimed products and their packaging materials",
        "gri_302-1": "Energy consumption within company",
        "gri_302-2": "Energy consumption outside company",
        "gri_302-3": "Energy intensity",
        "gri_302-4": "Reduction of energy consumption",
        "gri_302-5": "Reductions in energy requirements of products and services",
        "gri_303-1": "Interactions with water as a shared resource",
        "gri_303-2": "Management of water discharge-related impacts",
        "gri_303-3": "Water withdrawal",
        "gri_303-4": "Water discharge",
        "gri_303-5": "Water consumption",
        "gri_304-1": "Operational sites owned/managed",
        "gri_304-2": "Significant impacts on biodiversity",
        "gri_304-3": "Habitats protected or restored",
        "gri_304-4": "Affected IUCN Red List and Conservation List Species",
        "gri_305-1": "Scope 1: direct emissions",
        "gri_305-2": "Scope 2: indirect emissions",
        "gri_305-3": "Scope 3: indirect emissions",
        "gri_305-4": "GHG emissions intensity",
        "gri_305-5": "GHG emissions reduction",
        "gri_306-1": "Waste-related impacts",
        "gri_306-2": "Waste impact management",
        "gri_306-3": "Waste generated",
        "gri_307-1": "Environmental fines",
        "gri_307-2": "Environmental non-monetary sanctions",
        "gri_308-1": "Environmental screening of new suppliers",
        "gri_308-2": "Negative environmental impacts in the supply chain",
        "gri_401-1": "New employee hires and employee turnover",
        "gri_401-2": "Employee benefits",
        "gri_401-3": "Parental leave",
        "gri_403-1": "Occupational health and safety management",
        "gri_403-2": "Hazard identification",
        "gri_403-3": "Occupational health services",
        "gri_403-5": "Worker training on occupational health and safety",
        "gri_404-2": "Programs for upgrading employee skills",
        "gri_405-1": "Diversity of governance bodies and employees",
        "gri_405-2": "Ratio of basic salary and remuneration of women to men",
        "gri_413-1": "Operations with local community engagement",
        "gri_415-1": "Political contributions",
        "gri_416-1": "Assessment of the health and safety impacts of product",
        "gri_418-1": "Customer privacy complaints",
    }

    report_names = body.get("report_names", [])
    if not report_names:
        raise HTTPException(status_code=400, detail="No reported selected.")

    print(f"selected reports: {report_names}")

    try:
        existing_reports = os.listdir(os.path.join(DATA_FOLDER, "reports"))
    except Exception as ex:
        print(f"existing reports listing error: {ex}")

    try:
        current_session_uploaded_reports = os.listdir(
            os.path.join(DATA_FOLDER, "uploaded_reports", session_id)
        )
    except Exception as ex:
        print(f"current session reports listing error: {ex}")

    response_data = {}
    bar_chart_data = defaultdict(lambda: defaultdict(list))
    radar_chart_data = defaultdict(lambda: defaultdict(list))
    scatter_chart_data = defaultdict(list)

    for report_name in report_names:
        if report_name in existing_reports:
            final_json_report = os.path.join(
                DATA_FOLDER, "reports", report_name, report_name + "_final.json"
            )
        elif report_name in current_session_uploaded_reports:
            final_json_report = os.path.join(
                DATA_FOLDER,
                "uploaded_reports",
                session_id,
                report_name,
                report_name + "_final.json",
            )

        if not os.path.exists(final_json_report):
            print("[INFO] Path to report doesn't exist.")
            continue  # Optionally log missing file
        try:
            with open(final_json_report, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            reported_disclosure_topics = {}

            for item in report_data:
                disclosure = item.get("disclosure")
                disclosure_title = item.get("disclosure_title")
                section_count = len(item.get("section_ids", []))
                standard = disclosure.split("-")[0]
                # standard = item.get("topic")
                # standard_title = item.get("topic_title")
                # paragraphs = item.get("paragraphs", [])

                if standard in reported_disclosure_topics.keys():
                    reported_disclosure_topics[standard] += 1
                else:
                    reported_disclosure_topics[standard] = 1

                completeness = item.get("completeness", 0)
                materiality = item.get("materiality", 0)
                comment = item.get("comment", "")
                # disclosure_title = gri_disclosure_titles[disclosure]

                disclosure_esg = None
                if "gri_2" in disclosure:
                    disclosure_esg = "g"
                elif "gri_3" in disclosure:
                    disclosure_esg = "e"
                else:
                    disclosure_esg = "s"

                # bar_chart_data[report_name][disclosure] = section_count
                bar_chart_data[report_name][disclosure].append(
                    {
                        "gri_disclosure": " ".join(disclosure.upper().split("_")),
                        "gri_disclosure_title": disclosure_title,
                        "paragraph_count": section_count,
                    }
                )

                scatter_chart_data[report_name].append(
                    {
                        "disclosure": disclosure,
                        "title": disclosure_title,
                        "esg": disclosure_esg,
                        "completeness": completeness,
                        "materiality": materiality,
                        "comment": comment,
                    }
                )

            for standard, reported_count in reported_disclosure_topics.items():
                total = gri_topic_counts[standard]
                percentage = (reported_count / total * 100) if total > 0 else 0
                topic = gri_topic_map[standard]
                # radar_chart_data[report_name][topic] = round(percentage, 2)
                radar_chart_data[report_name][topic].append(
                    {
                        "gri_topic": " ".join(standard.upper().split("_")),
                        "gri_topic_title": topic,
                        "value": round(percentage, 2),
                        "description": "",
                    }
                )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing {final_json_report}: {e}"
            )
    # response_data["bar_chart"] = {k: dict(v) for k, v in bar_chart_data.items()}
    # response_data["radar_chart"] = {k: dict(v) for k, v in radar_chart_data.items()}
    response_data["bar_chart"] = dict(bar_chart_data)
    response_data["radar_chart"] = dict(radar_chart_data)
    response_data["scatter_chart"] = dict(scatter_chart_data)
    return response_data
