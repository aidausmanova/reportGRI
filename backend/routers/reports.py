import csv
import os
import shutil
import uuid
import time
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
)
# from fastapi.responses import JSONResponse
# from starlette.responses import FileResponse

from pathlib import Path
from collections import defaultdict
import asyncio

router = APIRouter()
DATA_PATH = Path("data")

# Ensure the data folder exists
DATA_PATH.mkdir(exist_ok=True)

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
    industries = set()
    with open(DATA_PATH / "data.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            industries.add(row["industry"])
    return sorted(industries)


@router.get("/reports/{industry}")
def get_reports_by_industry(industry: str):
    orgs = set()
    with open(DATA_PATH / "data.csv", newline="", encoding="utf-8") as f:
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
    session_folder = DATA_PATH / session_id
    session_folder.mkdir(exist_ok=True)

    dest = session_folder / file.filename
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Simulate parsing: generate a dummy CSV based on the filename
    await asyncio.sleep(5)

    # Fake parsed CSV with same columns
    dummy_csv = session_folder / (file.filename.replace(".pdf", ".csv"))
    with open(dummy_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "index",
                "organization",
                "industry",
                "section",
                "gri_l1",
                "gri_l2",
                "sim_score",
                "gri_desc",
            ],
        )
        writer.writeheader()
        for i in range(1, 6):
            writer.writerow(
                {
                    "index": i,
                    "organization": file.filename.replace(".pdf", ""),
                    "industry": "MyIndustry",
                    "section": f"Section {i}",
                    "gri_l1": f"GRI-{i % 3 + 1}00",
                    "gri_l2": f"GRI-{i % 3 + 1}01",
                    "sim_score": round(0.6 + 0.1 * (i % 3), 2),
                    "gri_desc": f"Description for GRI-{i % 3 + 1}00",
                }
            )

    files = list_uploaded_files(session_id)
    return {"uploaded": file.filename, "my_reports": files}


def list_uploaded_files(session_id: str) -> List[str]:
    session_folder = DATA_PATH / session_id
    if not session_folder.exists():
        return []
    return sorted(
        [
            f.name.replace(".csv", "")
            for f in session_folder.glob("*.csv")
            if f.is_file()
        ]
    )


@router.get("/my-reports")
def get_my_reports(session_id: str = Depends(get_or_create_session_id)) -> Any:
    return list_uploaded_files(session_id)


@router.post("/chart-data")
def get_chart_data(
    body: dict = Body(...),
    session_id: str = Depends(get_or_create_session_id),
):
    report_names = body.get("report_names", [])
    gri_level = body.get("gri_level", "l1")
    chart_type = body.get("chart", "bar")  # bar or heatmap

    assert gri_level in ("l1", "l2")
    assert chart_type in ("bar", "radar", "heatmap")

    all_rows = []

    # Load from main data.csv
    with open(DATA_PATH / "data.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["organization"] in report_names:
                all_rows.append(row)

    # Load from user's uploaded session files
    session_folder = DATA_PATH / session_id
    if session_folder.exists():
        for path in session_folder.glob("*.csv"):
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["organization"] in report_names:
                        all_rows.append(row)

    response_data = {}
    if chart_type == "bar":
        bar_chart_data = defaultdict(lambda: defaultdict(int))  # report -> GRI -> count
        sections_by_gri = defaultdict(list)

        for row in all_rows:
            gri = row["gri_l1"] if gri_level == "l1" else row["gri_l2"]
            report = row["organization"]
            bar_chart_data[report][gri] += 1

            section = row["section"]
            desc = row["gri_desc"]
            sections_by_gri[gri].append({"section": section, "gri_desc": desc})

        response_data["bar_chart"] = bar_chart_data
        response_data["sections_by_gri"] = sections_by_gri

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

    elif chart_type == "heatmap":
        heatmap_data = []
        sections_by_gri = defaultdict(list)

        for row in all_rows:
            gri = row["gri_l1"] if gri_level == "l1" else row["gri_l2"]
            section = row["section"]
            score = float(row["sim_score"])
            desc = row["gri_desc"]

            heatmap_data.append(
                {"section": section, "GRI_code": gri, "score": score, "gri_desc": desc}
            )
            sections_by_gri[gri].append({"section": section, "gri_desc": desc})

        response_data["heatmap_chart"] = heatmap_data
        response_data["sections_by_gri"] = sections_by_gri

    elif chart_type == "radar":
        e_category = ['gri_301', 'gri_302', 'gri_303', 'gri_304', 'gri_305', 'gri_306', 'gri_307', 'gri_308']
        s_category = ['gri_401', 'gri_402', 'gri_403', 'gri_404', 'gri_405', 'gri_413', 'gri_415', 'gri_416', 'gri_418']
        g_category = ['gri_2', 'gri_201']

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
            "gri_418": "Customer privacy"
        }
        radar_chart_data = defaultdict(lambda: {"Environmental": 0, "Social": 0, "Governance": 0})
        radar_chart_data = defaultdict(lambda: {"General disclosure": 0, "Economic performance": 0, "Materials": 0,
                                                "Energy": 0, "Water": 0, "Biodiversity": 0, "Emissions": 0, "Waste": 0,
                                                "Environmental compliance": 0, "Supplier assessment": 0, "Employment": 0,
                                                "Employee safety": 0, "Training": 0, "Diversity": 0,"Communities": 0,
                                                "Public policy": 0, "Customer safety": 0, "Customer privacy": 0})
        sections_by_gri = defaultdict(list)

        for row in all_rows:
            if gri_level == "l2":
                gri = row["gri_l2"].split("-")[0]
            else:
                gri = row["gri_l1"]

            report = row["organization"]

            radar_chart_data[report][gri_standards[gri]] += 1
            # if gri in e_category:
            #     radar_chart_data[report]["Environmental"] += 1
            # elif gri in s_category:
            #     radar_chart_data[report]["Social"] += 1
            # elif gri in g_category:
            #     radar_chart_data[report]["Governance"] += 1

        # Convert counts to percentages
        for report, counts in radar_chart_data.items():
            total = sum(counts.values())
            # if total > 0:
            #     for cat in ["Environmental", "Social", "Governance"]:
            #         counts[cat] = float(round((counts[cat] / total) * 100, 2))
            # else:
            #     for cat in ["Environmental", "Social", "Governance"]:
            #         counts[cat] = float(0.0)
            if total > 0:
                for cat in gri_standards.values():
                    counts[cat] = float(round((counts[cat] / total) * 100, 2))
            else:
                for cat in gri_standards.values():
                    counts[cat] = float(0.0)

        response_data["radar_chart"] = radar_chart_data
        # response_data["bar_chart"] = bar_chart_data
        # response_data["sections_by_gri"] = sections_by_gri
        print(response_data["radar_chart"])

    # print(response_data)
    return response_data
