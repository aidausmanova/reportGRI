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
)

router = APIRouter()
DATA_FOLDER = Path("data")

# Ensure the data folder exists
DATA_FOLDER.mkdir(exist_ok=True)

SESSION_COOKIE_NAME = "session_id"


# Dependency to get or create session ID
def get_or_create_session_id(
    session_id: Optional[str] = Cookie(None), response: Response = None
) -> str:
    if not session_id:
        session_id = str(uuid.uuid4())
        if response:
            response.set_cookie(
                key=SESSION_COOKIE_NAME, value=session_id, httponly=True
            )
    return session_id


@router.get("/session-id")
def get_session_id(request: Request, response: Response):
    session_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(key=SESSION_COOKIE_NAME, value=session_id, httponly=True)
    return {"session_id": session_id}


@router.get("/industries")
def get_industries():
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
def get_reports_by_industry(industry: str):
    file_path = os.path.join(DATA_FOLDER, "industries_reports.csv")
    orgs = set()
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["industry"] == industry:
                orgs.add(row["organization"])
    return sorted(orgs)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Depends(get_or_create_session_id),
):
    session_folder = os.path.join(DATA_FOLDER, "uploaded_reports", session_id)
    Path(session_folder).mkdir(exist_ok=True)

    uploaded_report = os.path.join(session_folder, file.filename)
    with open(uploaded_report, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse the uploaded report and generate the json output file
    run_parser(uploaded_report)

    # await asyncio.sleep(5)

    # # Fake parsed CSV with same columns
    # dummy_json = os.path.join(session_folder, file.filename.replace(".pdf", ".json"))

    # data = {}
    # for i in range(1, 5):
    #     name = str(i)
    #     x = i + 1
    #     y = i + 2
    #     z = i + 3
    #     data[name] = {"x": x, "y": y, "z": z}
    # with open(dummy_json, "w") as f:
    #     json.dump(data, f, indent=4)

    files = list_uploaded_files(session_id)
    return {"uploaded": file.filename, "my_reports": files}


def list_uploaded_files(session_id: str) -> List[str]:
    session_folder = os.path.join(DATA_FOLDER, "uploaded_reports", session_id)
    if not Path(session_folder).exists():
        return []
    return sorted(
        [
            f.name.replace(".json", "")
            for f in Path(session_folder).glob("*.json")
            if f.is_file()
        ]
    )


@router.get("/my-reports")
def get_my_reports(session_id: str = Depends(get_or_create_session_id)) -> Any:
    return list_uploaded_files(session_id)


@router.post("/chart-data")
def get_chart_data_new(
    body: dict = Body(...),
    session_id: str = Depends(get_or_create_session_id),
):
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

    base_path = os.path.join(DATA_FOLDER, "existing_reports")

    response_data = {}
    all_rows = []
    bar_chart_data = defaultdict(lambda: defaultdict(int))
    radar_chart_data = defaultdict(lambda: defaultdict(int))
    scatter_chart_data = defaultdict(list)

    for report_name in report_names:
        json_filename = f"{report_name}.json"
        json_path = os.path.join(base_path, json_filename)

        if not os.path.exists(json_path):
            continue  # Optionally log missing file
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
            reported_disclosure_topics = {}

            for item in report_data:
                disclosure = item.get("disclosure")
                section_count = len(item.get("section_ids", []))
                bar_chart_data[report_name][disclosure] = section_count
                standard = disclosure.split("-")[0]
                if standard in reported_disclosure_topics.keys():
                    reported_disclosure_topics[standard] += 1
                else:
                    reported_disclosure_topics[standard] = 1
                completeness = item.get("completeness", 0)
                materiality = item.get("materiality", 0)
                comment = item.get("comment", "")
                disclosure_title = gri_disclosure_titles[disclosure]
                disclosure_esg = None
                if "gri_2" in disclosure:
                    disclosure_esg = "g"
                elif "gri_3" in disclosure:
                    disclosure_esg = "e"
                else:
                    disclosure_esg = "s"

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
                radar_chart_data[report_name][topic] = round(percentage, 2)

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing {json_filename}: {e}"
            )
    response_data["bar_chart"] = {k: dict(v) for k, v in bar_chart_data.items()}
    response_data["radar_chart"] = {k: dict(v) for k, v in radar_chart_data.items()}
    response_data["scatter_chart"] = dict(scatter_chart_data)
    # print(response_data['scatter_chart'])
    return response_data


# @router.post("/chart-data")
def get_chart_data(
    body: dict = Body(...),
    session_id: str = Depends(get_or_create_session_id),
):
    report_names = body.get("report_names", [])
    if not report_names:
        raise HTTPException(status_code=400, detail="No reported selected.")

    # gri_level = body.get("gri_level", "l1")
    # chart_type = body.get("chart", "bar")  # bar or heatmap

    # assert gri_level in ("l1", "l2")
    # assert chart_type in ("bar", "radar", "heatmap")

    base_path = os.path.join(DATA_FOLDER, "existing_reports")

    all_rows = []

    response_data = {}

    # Coverage distribution
    def load_coverage_distribution_data(response_data):
        bar_chart_data = defaultdict(lambda: defaultdict(int))  # report -> GRI -> count
        nonlocal base_path, report_names
        for report_name in report_names:
            json_filename = f"{report_name}.json"
            json_path = os.path.join(base_path, json_filename)

            if not os.path.exists(json_path):
                continue  # Optionally log missing file

            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    report_data = json.load(f)

                print(report_data)

                for item in report_data:
                    disclosure = item.get("disclosure")
                    section_ids = item.get("section_ids", [])
                    if disclosure:
                        bar_chart_data[report_name][disclosure] = len(section_ids)

                response_data["bar_chart"] = bar_chart_data

            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Error processing {json_filename}: {e}"
                )

    load_coverage_distribution_data(response_data)

    # # Load from main data.csv
    # with open(DATA_FOLDER / "data.csv", newline="", encoding="utf-8") as f:
    #     reader = csv.DictReader(f)
    #     for row in reader:
    #         if row["organization"] in report_names:
    #             all_rows.append(row)

    # # Load from user's uploaded session files
    # session_folder = DATA_FOLDER / session_id
    # if session_folder.exists():
    #     for path in session_folder.glob("*.csv"):
    #         with open(path, newline="", encoding="utf-8") as f:
    #             reader = csv.DictReader(f)
    #             for row in reader:
    #                 if row["organization"] in report_names:
    #                     all_rows.append(row)

    # Coverage distribution

    # bar_chart_data = defaultdict(lambda: defaultdict(int))  # report -> GRI -> count
    # sections_by_gri = defaultdict(list)

    # for row in all_rows:
    #     gri = row["gri_l2"]  # gri_disclosure
    #     report = row["organization"]
    #     bar_chart_data[report][gri] += 1

    #     section = row["section"]
    #     desc = row["gri_desc"]
    #     sections_by_gri[gri].append({"section": section, "gri_desc": desc})

    # response_data["bar_chart"] = bar_chart_data
    # response_data["sections_by_gri"] = sections_by_gri

    # e_category = ['gri_301', 'gri_302', 'gri_303', 'gri_304', 'gri_305', 'gri_306', 'gri_307', 'gri_308']
    # s_category = ['gri_401', 'gri_402', 'gri_403', 'gri_404', 'gri_405', 'gri_413', 'gri_415', 'gri_416', 'gri_418']
    # g_category = ['gri_2', 'gri_201']
    #
    # radar_chart_data = defaultdict(lambda: {"Environmental": 0, "Social": 0, "Governance": 0})
    #
    # for row in all_rows:
    #     if gri_level == "l2":
    #         gri = row["gri_l2"].split("-")[0]
    #     else:
    #         gri = row["gri_l1"]
    #
    #     report = row["organization"]
    #
    #     if gri in e_category:
    #         radar_chart_data[report]["Environmental"] += 1
    #     elif gri in s_category:
    #         radar_chart_data[report]["Social"] += 1
    #     elif gri in g_category:
    #         radar_chart_data[report]["Governance"] += 1
    #
    # # Convert counts to percentages
    # for report, counts in radar_chart_data.items():
    #     total = sum(counts.values())
    #     if total > 0:
    #         for cat in ["Environmental", "Social", "Governance"]:
    #             counts[cat] = float(round((counts[cat] / total) * 100, 2))
    #     else:
    #         for cat in ["Environmental", "Social", "Governance"]:
    #             counts[cat] = float(0.0)
    #
    # response_data["radar_chart"] = radar_chart_data

    # # Heatmap
    # heatmap_data = []
    # sections_by_gri = defaultdict(list)

    # for row in all_rows:
    #     gri = row["gri_l1"]  # gri_standards
    #     section = row["section"]
    #     score = float(row["sim_score"])
    #     desc = row["gri_desc"]

    #     heatmap_data.append(
    #         {"section": section, "GRI_code": gri, "score": score, "gri_desc": desc}
    #     )
    #     sections_by_gri[gri].append({"section": section, "gri_desc": desc})

    # response_data["heatmap_chart"] = heatmap_data
    # response_data["sections_by_gri"] = sections_by_gri

    # Radar
    e_category = [
        "gri_301",
        "gri_302",
        "gri_303",
        "gri_304",
        "gri_305",
        "gri_306",
        "gri_307",
        "gri_308",
    ]
    s_category = [
        "gri_401",
        "gri_402",
        "gri_403",
        "gri_404",
        "gri_405",
        "gri_413",
        "gri_415",
        "gri_416",
        "gri_418",
    ]
    g_category = ["gri_2", "gri_201"]

    gri_standards = {
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
    radar_chart_data = defaultdict(
        lambda: {"Environmental": 0, "Social": 0, "Governance": 0}
    )
    radar_chart_data = defaultdict(
        lambda: {
            "General disclosure": 0,
            "Economic performance": 0,
            "Materials": 0,
            "Energy": 0,
            "Water": 0,
            "Biodiversity": 0,
            "Emissions": 0,
            "Waste": 0,
            "Environmental compliance": 0,
            "Supplier assessment": 0,
            "Employment": 0,
            "Employee safety": 0,
            "Training": 0,
            "Diversity": 0,
            "Communities": 0,
            "Public policy": 0,
            "Customer safety": 0,
            "Customer privacy": 0,
        }
    )
    sections_by_gri = defaultdict(list)

    # for row in all_rows:
    #     gri = row["gri_l1"]
    #     report = row["organization"]

    #     radar_chart_data[report][gri_standards[gri]] += 1
    #     # if gri in e_category:
    #     #     radar_chart_data[report]["Environmental"] += 1
    #     # elif gri in s_category:
    #     #     radar_chart_data[report]["Social"] += 1
    #     # elif gri in g_category:
    #     #     radar_chart_data[report]["Governance"] += 1

    # # Convert counts to percentages
    # for report, counts in radar_chart_data.items():
    #     total = sum(counts.values())
    #     # if total > 0:
    #     #     for cat in ["Environmental", "Social", "Governance"]:
    #     #         counts[cat] = float(round((counts[cat] / total) * 100, 2))
    #     # else:
    #     #     for cat in ["Environmental", "Social", "Governance"]:
    #     #         counts[cat] = float(0.0)
    #     if total > 0:
    #         for cat in gri_standards.values():
    #             counts[cat] = float(round((counts[cat] / total) * 100, 2))
    #     else:
    #         for cat in gri_standards.values():
    #             counts[cat] = float(0.0)

    # response_data["radar_chart"] = radar_chart_data
    # # response_data["bar_chart"] = bar_chart_data
    # # response_data["sections_by_gri"] = sections_by_gri
    # # print(response_data["radar_chart"])

    # print(response_data)
    return response_data
