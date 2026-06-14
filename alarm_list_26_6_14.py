
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pyodbc, os
from config.config import *

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

MP3_FOLDER = r"Z:\\"

def get_conn():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SQL_SERVER};DATABASE={SQL_DB};UID={SQL_USER};PWD={SQL_PASS};"
    )

def build_tree(rows):
    tree = {}
    for tagid, path, dtype in rows:
        parts = path.split("/")
        node = tree
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        node[parts[-1]] = {"tagid": tagid, "datatype": dtype, "_leaf": True}
    return tree

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT TagId, Path, DataType
        FROM TagMaster
        WHERE IsActive = 1
        ORDER BY Path
    """)
    tags = cur.fetchall()

    tree = build_tree(tags)

    mp3_files = []
    if os.path.exists(MP3_FOLDER):
        mp3_files = sorted([f for f in os.listdir(MP3_FOLDER) if f.lower().endswith(".mp3")])

    cur.execute("""
        SELECT AlarmId, TagPath, Mp3File, AlarmMode,
               ThresholdHigh, ThresholdLow,
               Priority, EnableAlarm
        FROM Alarm_Lists
        ORDER BY TagPath
    """)
    alarms = cur.fetchall()

    conn.close()

    return templates.TemplateResponse("alarm_list.html", {
        "request": request,
        "tree": tree,
        "mp3_files": mp3_files,
        "alarms": alarms
    })
