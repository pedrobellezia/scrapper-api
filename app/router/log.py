import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter
import os
from app.schemas import LogFilter

router = APIRouter(prefix="/devlogs")

log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../logs"))


def foo():
    files = os.listdir(log_dir)

    dates = []
    for f in files:
        if f.endswith(".jsonl"):
            try:
                date = datetime.strptime(f.replace(".jsonl", ""), "%Y-%m-%d").date()
                dates.append(date)
            except ValueError:
                continue

    if not dates:
        return None, None

    dates.sort()
    return dates[0], dates[-1], files


def get_log_files(init_date: Optional[str] = None, end_date: Optional[str] = None):

    oldest, newest, files = foo()
    files = set(files)

    if not oldest or not newest:
        return []

    start = datetime.strptime(init_date, "%d-%m-%Y").date() if init_date else oldest
    end = datetime.strptime(end_date, "%d-%m-%Y").date() if end_date else newest

    result = []
    current = start

    while current <= end:
        filename = f"{current.isoformat()}.jsonl"
        if filename in files:
            result.append(filename)
        current += timedelta(days=1)

    return result


@router.post("")
async def show_log(data: LogFilter):
    log_list = get_log_files(data.init_date, data.end_date)

    if not log_list:
        return []

    logs = []

    for file in log_list:
        file_path = os.path.join(log_dir, file)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                bar = json.loads(line)
                if not (
                    (bar.get("level", None) in data.level or not data.level)
                    and (bar.get("cnpj", None) in data.cnpj or not data.cnpj)
                    and (
                        bar.get("error_type") in data.error_type or not data.error_type
                    )
                    and (bar.get("tipo_cnd") in data.tipo_cnd or not data.tipo_cnd)
                ):
                    logs.append(bar)

    return logs
