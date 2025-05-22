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
    assert chart_type in ("bar", "heatmap")

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

    return response_data
