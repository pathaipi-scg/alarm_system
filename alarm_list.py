
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import pyodbc, os
import subprocess
import sys

from config.config import *

from pyModbusTCP.client import ModbusClient

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

MP3_FOLDER = r"Z:\\"

def get_conn():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SQL_SERVER};DATABASE={SQL_DB};UID={SQL_USER};PWD={SQL_PASS};"
    )

def reload_alarm():

    try:

        c = ModbusClient(
            host="172.28.231.251",
            port=502,
            auto_open=True
        )

        regs = c.read_holding_registers(
            12002,
            1
        )

        if not regs:

            print(
                "READ RELOAD_ALARM FAILED"
            )

            return

        current = regs[0]

        c.write_single_register(
            12002,
            current + 1
        )

        print(
            f"RELOAD_ALARM => {current+1}"
        )

    except Exception as ex:

        print(
            "RELOAD_ALARM ERROR:",
            ex
        )

def build_tree(rows):
    tree = {}

    for tagid, path, dtype in rows:
        parts = path.split("/")
        node = tree

        for p in parts[:-1]:
            node = node.setdefault(p, {})

        node[parts[-1]] = {
            "tagid": tagid,
            "datatype": dtype,
            "fullpath": path,
            "_leaf": True
        }

    return tree

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT TagId, Path, DataType
        FROM TagMaster
        WHERE IsActive = 1
        AND TagId NOT IN (
            SELECT TagId
            FROM Alarm_Lists
        )
        ORDER BY Path
    """)

    tags = cur.fetchall()

    tree = build_tree(tags)

    mp3_files = []
    if os.path.exists(MP3_FOLDER):
        mp3_files = sorted([f for f in os.listdir(MP3_FOLDER) if f.lower().endswith(".mp3")])

    cur.execute("""
        SELECT AlarmId, TagId, TagPath, AlarmMode,
               ThresholdHigh, ThresholdLow, Mp3File,
               Priority, EnableAlarm
        FROM Alarm_Lists
        ORDER BY TagPath
    """)
    alarms = cur.fetchall()

    conn.close()

    return templates.TemplateResponse(request, "alarm_list.html", {
        "request": request,
        "tree": tree,
        "mp3_files": mp3_files,
        "alarms": alarms
    })

@app.post("/save")
def save_alarm(
    alarmid: str = Form(""),
    tagid: int = Form(...),
    tagpath: str = Form(...),
    alarmmode: str = Form(...),
    thresholdhigh: float = Form(None),
    thresholdlow: float = Form(None),
    mp3file: str = Form(...),
    priority: int = Form(1)
):
    conn = get_conn()
    cur = conn.cursor()

    # กัน Tag ซ้ำ
    if not alarmid:

        cur.execute("""
            SELECT COUNT(*)
            FROM Alarm_Lists
            WHERE TagId = ?
        """, (tagid,))

        if cur.fetchone()[0] > 0:

            conn.close()

            return RedirectResponse(
                "/",
                status_code=303
            )

    if alarmid:
        cur.execute("""
            UPDATE Alarm_Lists
            SET TagId = ?,
                TagPath = ?,
                AlarmMode = ?,
                ThresholdHigh = ?,
                ThresholdLow = ?,
                Mp3File = ?,
                Priority = ?,
                UpdatedTime = GETDATE()
            WHERE AlarmId = ?
        """, (
            tagid,
            tagpath,
            alarmmode,
            thresholdhigh,
            thresholdlow,
            mp3file,
            priority,
            int(alarmid)
        ))
    else:
        cur.execute("""
            INSERT INTO Alarm_Lists (
                TagId,
                TagPath,
                AlarmMode,
                ThresholdHigh,
                ThresholdLow,
                Mp3File,
                Priority,
                RepeatEnable,
                EnableAlarm,
                CreatedTime,
                UpdatedTime
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, 1, 1,
                GETDATE(),
                GETDATE()
            )
        """, (
            tagid,
            tagpath,
            alarmmode,
            thresholdhigh,
            thresholdlow,
            mp3file,
            priority
        ))

    conn.commit()
    conn.close()
    reload_alarm()

    return RedirectResponse("/", status_code=303)

@app.post("/delete/{alarm_id}")
def delete_alarm(alarm_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM Alarm_Lists
        WHERE AlarmId = ?
    """, (alarm_id,))

    conn.commit()
    conn.close()
    reload_alarm()

    return RedirectResponse("/", status_code=303)

@app.post("/refresh")
def refresh_browser():

    #subprocess.Popen([
    subprocess.run([
        sys.executable,
        r"D:\AI\opc_service\app\browser.py"
    ])

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        DELETE a
        FROM Alarm_Lists a
        INNER JOIN TagMaster t
            ON a.TagId = t.TagId
        WHERE t.IsActive = 0
    """)

    deleted = cur.rowcount

    conn.commit()
    conn.close()

    if deleted > 0:
        print(f"DELETE INVALID ALARMS = {deleted}")
        reload_alarm()

    return RedirectResponse(
        "/",
        status_code=303
    )

@app.get("/mp3/{filename}")
def serve_mp3(filename: str):
    # serve an MP3 from MP3_FOLDER so the browser can preview the alarm sound.
    # restrict to a plain basename ending in .mp3 to block path traversal.
    name = os.path.basename(filename)

    if name != filename or not name.lower().endswith(".mp3"):
        return HTMLResponse("Invalid file", status_code=400)

    path = os.path.join(MP3_FOLDER, name)

    if not os.path.isfile(path):
        return HTMLResponse("Not found", status_code=404)

    return FileResponse(path, media_type="audio/mpeg")
