# Alarm System Business Rules Questionnaire

This document lists the business rules that must be confirmed before implementing
the alarm evaluation engine for `alarm_list.py`.

Current project boundary:

- `poller_sub.py` is already implemented in a separate project.
- InfluxDB is the runtime source for live tag values.
- SQL Server `Alarm_Lists` is the configuration source for alarm definitions.
- `alarm_list.py` will evaluate alarms and send alarm events to `alarm_sound.py`
  running on the Mini-PC.

No alarm engine implementation should begin until the rules below are answered.

---

## 1. AlarmMode Evaluation

### 1.1 Supported Alarm Modes

Assumption to confirm:

- `AlarmMode` defines how a live tag value should be compared against
  `ThresholdHigh` and/or `ThresholdLow`.

Questions:

- What exact `AlarmMode` values exist in `Alarm_Lists`?
- Are the values text names, numeric codes, or both?
- Are the allowed modes fixed or user-configurable?
- Should unsupported/unknown `AlarmMode` values be ignored, logged, or treated as
  system errors?

Possible modes to confirm:

- High alarm
- Low alarm
- High-high alarm
- Low-low alarm
- High/low range alarm
- Boolean true alarm
- Boolean false alarm
- Equal-to alarm
- Not-equal alarm
- Change-of-state alarm

### 1.2 Threshold Rules

Assumptions to confirm:

- High alarm means current value is greater than or equal to `ThresholdHigh`.
- Low alarm means current value is less than or equal to `ThresholdLow`.

Questions:

- Should high alarms trigger on `>` or `>=`?
- Should low alarms trigger on `<` or `<=`?
- Can `ThresholdHigh` be empty/null?
- Can `ThresholdLow` be empty/null?
- What should happen if a required threshold is missing?
- Are thresholds always numeric?
- Do thresholds need units?
- Are decimal values supported?
- Should values be rounded before comparison?

### 1.3 Value Type Rules

Assumptions to confirm:

- Numeric tags use threshold-based alarm modes.
- Boolean tags use true/false alarm modes.

Questions:

- What data types can come from InfluxDB?
- What data types are stored in `TagMaster.DataType`?
- Should `TagMaster.DataType` control evaluation behavior?
- How should string values be evaluated?
- How should null values be handled?
- How should non-numeric values be handled for numeric alarm modes?

### 1.4 Missing, Stale, or Bad Values

Assumption to confirm:

- If InfluxDB has no recent value for a tag, the alarm state should become
  `UNKNOWN`.

Questions:

- How old can an InfluxDB value be before it is considered stale?
- Should stale values trigger an alarm?
- Should stale values trigger a separate system alarm?
- Should missing values be displayed in the UI?
- Should missing values be sent to `alarm_sound.py`?
- Should the engine continue evaluating other alarms if one tag value is missing?

### 1.5 Alarm Reset Rules

Assumption to confirm:

- An active alarm clears automatically when the live value returns to the normal
  range.

Questions:

- Should alarms clear automatically?
- Is hysteresis required?
- Is a clear delay required?
- Should an alarm remain active until acknowledged even if the value returns to
  normal?
- Should clearing an alarm generate an event to `alarm_sound.py`?

---

## 2. Priority Handling

### 2.1 Priority Scale

Assumption to confirm:

- `Priority` controls alarm ordering and sound behavior.

Questions:

- What values can `Priority` contain?
- Does `1` mean highest priority or lowest priority?
- Are priorities numeric only?
- Are there named priorities such as Critical, High, Medium, Low?
- Is priority required for every alarm?
- What is the default priority if missing?

### 2.2 Priority Behavior

Assumptions to confirm:

- Higher-priority alarms should be sent before lower-priority alarms.
- Priority should affect which alarm sound plays first when multiple alarms are
  active.

Questions:

- Should priority affect display order?
- Should priority affect sound selection?
- Should priority affect repeat frequency?
- Should priority affect color in the UI?
- Should priority affect escalation behavior?
- Should lower-priority alarms be suppressed while a higher-priority alarm is
  active?

### 2.3 Priority Ties

Assumption to confirm:

- If alarms have equal priority, the oldest active alarm should be processed
  first.

Questions:

- If two alarms have the same priority, which one should play first?
- Should newer alarms interrupt older alarms?
- Should same-priority alarms be queued by activation time?
- Should same-priority alarms be sorted by `TagPath`, `AlarmId`, or another
  field?

---

## 3. Alarm State Transitions

### 3.1 Required Alarm States

Assumption to confirm:

- The engine needs to track alarm state, not only current alarm condition.

Questions:

- Which states are required for the first version?
- Should the system distinguish active/unacknowledged and active/acknowledged?
- Should the system distinguish cleared/unacknowledged and cleared/acknowledged?
- Should disabled alarms appear in the runtime state list?
- Should unknown/stale data appear as a state?

Possible states to confirm:

- `NORMAL`
- `ACTIVE_UNACKED`
- `ACTIVE_ACKED`
- `CLEARED_UNACKED`
- `CLEARED_ACKED`
- `DISABLED`
- `UNKNOWN`
- `MUTED`

### 3.2 Activation Transition

Assumption to confirm:

- Alarm activation occurs when a previously normal alarm condition becomes true.

Questions:

- Should activation create an event every time the condition is true?
- Or only when state changes from normal to active?
- Should repeated active readings resend alarm events?
- Is an activation delay required?

### 3.3 Clear Transition

Assumption to confirm:

- Alarm clear occurs when a previously active alarm condition becomes false.

Questions:

- Should clear create an event?
- Should clear stop sound?
- Should clear remove the alarm from active display?
- Should clear require acknowledgement?
- Should cleared-but-unacknowledged alarms remain visible?

### 3.4 Disabled Transition

Assumption to confirm:

- If `EnableAlarm` is false, the engine should not evaluate or sound that alarm.

Questions:

- If an active alarm is disabled, should it clear immediately?
- Should disabling an active alarm stop sound?
- Should disabling generate an event?
- Should disabled alarms still be visible in the UI?

### 3.5 Engine Restart Behavior

Assumption to confirm:

- The first version can keep runtime alarm state in memory.

Questions:

- Should active alarm state survive server restart?
- Should acknowledgement state survive restart?
- Should mute state survive restart?
- Should the engine resend active alarm events after restart?
- Should state be restored from SQL Server, InfluxDB, event history, or memory
  only?

---

## 4. Multiple Simultaneous Alarms

### 4.1 Event Generation

Assumption to confirm:

- Each alarm state change should produce one event.

Questions:

- If 10 alarms activate in one engine cycle, should the system send 10 events?
- Should events be sent individually or as a batch?
- Should events be sorted by priority before sending?
- Should duplicate MP3 files be collapsed into one event?

### 4.2 Sound Selection

Assumption to confirm:

- `alarm_sound.py` should decide playback behavior based on events and priority.

Questions:

- Should `alarm_list.py` send all active alarms or only the highest-priority
  alarm?
- Should only one MP3 play at a time?
- Can MP3 sounds overlap?
- Should lower-priority sounds wait in a queue?
- Should a high-priority alarm interrupt a currently playing lower-priority
  alarm?

### 4.3 Repeated Active Alarms

Assumption to confirm:

- The engine should not continuously resend the same active alarm unless a repeat
  rule requires it.

Questions:

- Should active alarms repeat sound until acknowledged?
- Should repeat interval depend on priority?
- Should repeat stop when acknowledged?
- Should repeat stop when muted?
- Should repeat stop when alarm clears?

---

## 5. Alarm Event Delivery To `alarm_sound.py`

### 5.1 Transport Method

Assumption to confirm:

- `alarm_list.py` needs a defined network or file-based protocol to send events
  to `alarm_sound.py`.

Questions:

- How should `alarm_list.py` communicate with `alarm_sound.py`?
- HTTP request?
- TCP socket?
- UDP packet?
- Shared folder/file drop?
- Message queue?
- Database table?
- Does the Mini-PC have a fixed IP address or hostname?

### 5.2 Delivery Reliability

Assumption to confirm:

- Alarm events should be logged and retryable if delivery fails.

Questions:

- Should event delivery require acknowledgement from `alarm_sound.py`?
- Should failed events be retried?
- How many retries?
- What retry interval?
- Should old events expire?
- Should failed delivery trigger a system alarm?

### 5.3 Event Payload

Assumption to confirm:

- Events should contain enough information for `alarm_sound.py` to play the
  correct sound and log what happened.

Questions:

- What fields does `alarm_sound.py` need?
- Should the event include `AlarmId`?
- Should the event include `TagPath`?
- Should the event include current value?
- Should the event include thresholds?
- Should the event include `Priority`?
- Should the event include `Mp3File`?
- Should the event include alarm message text?
- Should the event include timestamp from InfluxDB, server time, or both?

### 5.4 Event Types

Assumption to confirm:

- At minimum, the sound system needs activation and clear events.

Questions:

- Which event types should be supported?
- Does `alarm_sound.py` need clear events?
- Does `alarm_sound.py` need acknowledge events?
- Does `alarm_sound.py` need mute/unmute events?
- Should heartbeat or health events be sent?

Possible event types to confirm:

- `ALARM_ACTIVE`
- `ALARM_CLEAR`
- `ALARM_ACK`
- `ALARM_MUTE`
- `ALARM_UNMUTE`
- `SYSTEM_HEALTH`

---

## 6. Acknowledge Behavior

### 6.1 Acknowledge Scope

Assumption to confirm:

- Acknowledge means an operator has seen the alarm; it does not make the alarm
  condition normal.

Questions:

- Should acknowledge be implemented in the first version?
- Is acknowledgement per alarm event, per tag, or global?
- Can users acknowledge multiple alarms at once?
- Can users acknowledge cleared alarms?
- Can users acknowledge disabled alarms?

### 6.2 Acknowledge Effect

Assumption to confirm:

- Acknowledging an active alarm should stop or reduce repeated audio, but the
  alarm remains active until the value returns to normal.

Questions:

- Does acknowledge stop sound immediately?
- Does acknowledge prevent repeat sounds?
- Does acknowledge change UI color/state?
- Does acknowledge send an event to `alarm_sound.py`?
- If an acknowledged alarm clears and becomes active again, should it become
  unacknowledged again?

### 6.3 Acknowledge Audit

Assumption to confirm:

- Acknowledgement should eventually be auditable.

Questions:

- Do users need to log in before acknowledging?
- Should the system store acknowledged user?
- Should the system store acknowledged timestamp?
- Where should acknowledgement history be stored?
- Is an acknowledgement comment required?

---

## 7. Mute Behavior

### 7.1 Mute Scope

Assumption to confirm:

- Mute is different from acknowledge.

Questions:

- Is mute global, per alarm, per priority, or per MP3 file?
- Can mute be applied to active alarms only?
- Can mute be applied before alarms happen?
- Should mute affect all Mini-PC audio or only selected alarms?

### 7.2 Mute Duration

Assumption to confirm:

- Mute is temporary unless explicitly configured otherwise.

Questions:

- Is mute temporary or permanent?
- What is the default mute duration?
- Can the operator choose mute duration?
- Should mute survive engine restart?
- Should mute survive Mini-PC restart?

### 7.3 Mute Override Rules

Assumption to confirm:

- A new higher-priority alarm may need to override mute.

Questions:

- Can critical alarms play even while muted?
- Can a new alarm override existing mute?
- Does mute stop currently playing audio?
- Does mute prevent future repeat audio?
- Does unmute replay active alarms?

### 7.4 Mute Audit

Assumption to confirm:

- Mute actions should eventually be auditable.

Questions:

- Should mute require user identity?
- Should mute timestamp be stored?
- Should mute reason/comment be required?
- Should mute/unmute events be sent to `alarm_sound.py`?

---

## 8. Cross-Cutting Rules To Confirm

### 8.1 Time Source

Assumption to confirm:

- Server local time should be used for alarm event timestamps unless InfluxDB
  timestamps are required.

Questions:

- Should event time use InfluxDB sample timestamp?
- Should event time use server processing time?
- What timezone should be used?
- Should timestamps be stored as UTC or local time?

### 8.2 Logging And History

Assumption to confirm:

- Alarm state changes and delivery attempts should be logged.

Questions:

- Should alarm events be stored in SQL Server?
- Should alarm events be stored in InfluxDB?
- Should delivery failures be stored?
- How long should history be retained?

### 8.3 Configuration Reload

Assumption to confirm:

- Alarm definitions should reload periodically from SQL Server without restarting
  the app.

Questions:

- How often should `Alarm_Lists` be reloaded?
- Should UI changes take effect immediately?
- What happens if an alarm definition changes while active?
- What happens if `Mp3File`, `Priority`, or thresholds change while active?

### 8.4 System Failure Behavior

Assumption to confirm:

- System failures should not crash the entire app if other alarms can still be
  evaluated.

Questions:

- What happens if SQL Server is unavailable?
- What happens if InfluxDB is unavailable?
- What happens if the Mini-PC is unreachable?
- What happens if the MP3 file does not exist?
- Should system failures generate sound alarms?

