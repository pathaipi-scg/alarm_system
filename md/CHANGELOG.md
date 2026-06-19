
# CHANGELOG

All significant project changes should be documented here.

---

## Unreleased

### 2026-06-19 (Repeat field)

Change Summary

Add a "Repeat" field (times to play, default 3) to the Create Alarm form, persisted to the new Alarm_Lists.[Repeat] int column. save_alarm reads repeatcount, falling back to 3 when blank/invalid; INSERT/UPDATE write [Repeat]; home() SELECT and the Edit button/JS carry the value so editing restores it.

Files Modified

- alarm_list.py
- templates/alarm_list.html
- md/CHANGELOG.md

Reason

Let operators configure how many times an alarm sound plays.

Risks

Low. [Repeat] is nullable; existing rows stay NULL and the form defaults to 3. Bracketed because Repeat is a SQL reserved word. The runtime sound engine (separate project) must read [Repeat] to honor it.

Rollback Method

Revert Git Commit

### 2026-06-19 (paths to .env)

Change Summary

Move filesystem paths MP3_FOLDER (Z:\) and the OPC browser.py script path out of alarm_list.py into config/config.py, read from .env via os.getenv with the previous hardcoded values as defaults. Lets each machine point MP3_FOLDER at a local test folder without code edits; production is unaffected when .env omits them.

Files Modified

- config/config.py
- alarm_list.py
- md/CHANGELOG.md

Reason

Allow local testing of the Test-sound feature without mapping Z:\, and make deploy not require editing code to switch paths.

Risks

Very low. Defaults equal the prior hardcoded values, so behavior is identical unless .env sets MP3_FOLDER / BROWSER_SCRIPT. No DB or runtime contract change.

Rollback Method

Revert Git Commit

### 2026-06-19

Change Summary

Add draggable splitters to resize the top panels (OPC tree / MP3 list / Create form) and a "Test" button in the Current Alarm Mapping Actions column that previews the row's MP3 sound in the browser. Added a GET /mp3/{filename} route that streams an MP3 from MP3_FOLDER (Z:\) with a basename + .mp3 guard against path traversal.

Files Modified

- alarm_list.py
- templates/alarm_list.html
- md/CHANGELOG.md

Reason

Operators could not adjust panel widths and had no way to hear a configured alarm sound before saving/using it.

Risks

Low. Splitter/Test are front-end only; the new /mp3 route is read-only and restricted to plain .mp3 basenames inside MP3_FOLDER. Audio only plays where the Z:\ share is mapped (production); on dev it shows a "file not found" alert. No change to save/delete/refresh or reload_alarm() Modbus behavior.

Rollback Method

Revert Git Commit

### Added

- Initial Alarm System project structure
    
- Flask web interface
    
- Alarm list display
    
### 2026-06-14

Change Summary

Add edit and delete functionality for Current Alarm Mapping

Files Modified

- alarm_list.py
- templates/alarm_list.html
- md/CHANGELOG.md

Reason

Allow saved alarm mappings to be updated or removed from the existing alarm list page.

Risks

Low. Changes are limited to the alarm mapping save/delete flow and table actions.

Rollback Method

Revert Git Commit


### Planned

- OPC-UA integration
    
- Alarm engine
    
- Audio notification
    
- Logging system
    
- Deployment automation
    

---

## Rules For AI Agents

Whenever changes are made

Update this file with:

### Date

YYYY-MM-DD

### Change Summary

Short description

### Files Modified

List of files

### Reason

Why the change was made

### Risks

Potential side effects

### Rollback Method

How to revert the change

---

## Example Entry

### 2026-06-14

Change Summary

Refactor alarm handling module

Files Modified

- alarm_list.py
    
- alarm_engine.py
    

Reason

Improve maintainability

Risks

Low

Rollback Method

Revert Git Commit
