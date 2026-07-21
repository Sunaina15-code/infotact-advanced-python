# PyChronicle — Project Documentation

**Infotact Advanced Python Engineering**
**Month 1 Project | July 2026**

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Module Reference](#3-module-reference)
   - 3.1 [AST Parser](#31-ast-parser)
   - 3.2 [Tracer](#32-tracer)
   - 3.3 [Storage](#33-storage)
   - 3.4 [UI](#34-ui)
   - 3.5 [CLI](#35-cli)
4. [Database Schema](#4-database-schema)
5. [Data Flow](#5-data-flow)
6. [Installation & Setup](#6-installation--setup)
7. [Usage Guide](#7-usage-guide)
8. [Testing](#8-testing)
9. [Performance Benchmarks](#9-performance-benchmarks)
10. [Future Work — MeshWeaver](#10-future-work--meshweaver)

---

## 1. Project Overview

**PyChronicle** is a time-travel execution tracer for Python programs. It hooks into the Python interpreter using `sys.settrace`, captures variable states at every line of execution, and stores them in a SQLite database. Users can then replay or inspect any point in a program's execution — effectively "traveling back in time" through their code.

### Core Capabilities

| Capability | Description |
|---|---|
| Execution tracing | Captures variable state at every executed line via `sys.settrace` |
| AST parsing | Statically identifies all variable assignments before execution |
| Delta compression | Records only changed values, cutting storage by up to ~90% |
| Variable filtering | Strips built-in and dunder variables from the trace |
| Terminal UI | Interactive Textual-based timeline for stepping through states |
| Watch Variables | Track specific named variables across the full execution |
| Export | Dump stored states to JSON or CSV |
| CLI | `pychronicle run / history / watch` command-line interface |

### Team

| Member | Role |
|---|---|
| Sunaina | Team Lead — tracer core, delta tracking, CLI, Timeline UI |
| Athrva | Storage layer, query engine, export, stats |
| John | Documentation and progress tracking |
| Noah | Performance testing, benchmarking, sys.settrace research |

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PyChronicle                              │
│                                                                 │
│   ┌──────────────┐     ┌─────────────────────────────────┐     │
│   │  AST Parser  │     │          Tracer Pipeline         │     │
│   │              │     │                                  │     │
│   │ Reads source │     │  TraceFilter → DeltaTracker      │     │
│   │ Finds assign-│     │       ↓                          │     │
│   │ ments before │     │  CompressedTracer (sys.settrace) │     │
│   │ execution    │     │       ↓                          │     │
│   └──────────────┘     │  StateStorage (SQLite)           │     │
│                        └─────────────────────────────────┘     │
│                                      ↓                         │
│            ┌─────────────────────────────────────────┐         │
│            │           Storage Layer                 │         │
│            │                                         │         │
│            │  StateStorage (base CRUD)               │         │
│            │  AdvancedStorage (queries + summaries)  │         │
│            │  QueryEngine (search/filter queries)    │         │
│            │  StorageStats (analytics)               │         │
│            │  StateExporter (JSON / CSV output)      │         │
│            └─────────────────────────────────────────┘         │
│                              ↓                                  │
│     ┌──────────────────┐   ┌───────────────────────────────┐   │
│     │   Terminal UI    │   │            CLI                │   │
│     │                  │   │                               │   │
│     │  TimelineUI      │   │  pychronicle run <script>     │   │
│     │  WatchVariables  │   │  pychronicle history          │   │
│     │  (Textual TUI)   │   │  pychronicle watch <var>      │   │
│     └──────────────────┘   └───────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

- **Delta-only storage**: rather than saving every variable at every line, only *changed* values are persisted. This reduces state count by up to 90% on typical scripts.
- **Three-stage filter pipeline**: `TraceFilter` removes built-ins → `DeltaTracker` removes unchanged values → `StateStorage` saves only what remains.
- **SQLite as the persistence layer**: lightweight, file-based, zero external dependencies. Indexed on `line_number` for fast time-travel queries.
- **`sys.settrace` over AST execution**: the tracer hooks into the live interpreter so it captures runtime values (including computed results and loop iterations), not just static structure.

---

## 3. Module Reference

### 3.1 AST Parser

**Location:** `pychronicle/ast_parser/__init__.py`
**Author:** Sunaina (Week 1)

Statically analyzes a Python source file before execution using the `ast` module. Identifies all variable assignment locations so they can be compared with the runtime trace.

#### Class: `ASTParser`

```python
ASTParser(filepath: str)
```

| Method | Returns | Description |
|---|---|---|
| `parse()` | `list[dict]` | Parses the file; returns list of assignment records |
| `_extract_assignments(tree)` | `None` | Internal: walks AST nodes for `Assign` and `AugAssign` |
| `display()` | `None` | Prints all found assignments to stdout |

**Assignment record shape:**

```python
{
    'line': int,          # Line number in source file
    'variable': str,      # Variable name
    'type': str           # 'assignment' or 'aug_assignment'
}
```

**Example:**

```python
from pychronicle.ast_parser import ASTParser

parser = ASTParser("myscript.py")
assignments = parser.parse()
parser.display()
# Line   2 | assignment      | Variable: x
# Line   3 | assignment      | Variable: y
```

---

### 3.2 Tracer

**Location:** `pychronicle/tracer/`

The tracer subsystem has evolved across four weeks into a fully optimized pipeline. Three tracer classes are provided, each building on the previous.

---

#### Class: `ExecutionTracer` — Base Tracer

**File:** `pychronicle/tracer/__init__.py`
**Author:** Sunaina (Week 1)

The original tracer. Records **every** local variable at every executed line.

```python
ExecutionTracer(db_path: str = "pychronicle.db")
```

| Method | Description |
|---|---|
| `start_trace(target_script: str)` | Compiles and executes the target script under `sys.settrace` |
| `get_history()` | Returns all stored states from the database |
| `display_history()` | Prints all stored states to stdout |

---

#### Class: `OptimizedTracer` — Delta-Aware Tracer

**File:** `pychronicle/tracer/optimized_tracer.py`
**Author:** Sunaina (Week 2)

Adds delta tracking. Only records variables whose values have *changed* since the previous line.

```python
OptimizedTracer(db_path: str = "pychronicle.db")
```

| Method | Description |
|---|---|
| `start_trace(target_script: str)` | Traces script; prints optimization stats on completion |
| `display_history()` | Delegates to `DeltaTracker.display_deltas()` |

After tracing, reports:
- **Changes saved** — number of state records written
- **Lines skipped** — lines where no variables changed
- **Memory saved %** — `skipped / (saved + skipped) * 100`

---

#### Class: `CompressedTracer` — Full Pipeline Tracer

**File:** `pychronicle/tracer/compressed_tracer.py`
**Author:** Sunaina (Week 3)

The production-ready tracer. Combines all three optimizations in sequence:

1. `TraceFilter.filter_locals()` — remove built-ins and dunder variables
2. `DeltaTracker.compute_delta()` — keep only changed values
3. `StateStorage.insert_state()` — persist survivors

```python
CompressedTracer(db_path: str = "pychronicle.db")
```

| Method | Description |
|---|---|
| `run(script_path: str)` | Runs the full pipeline; prints compression summary |

This is the tracer used by the CLI.

---

#### Class: `DeltaTracker`

**File:** `pychronicle/tracer/delta_tracker.py`
**Author:** Sunaina (Week 2)

Maintains a dictionary of the previous variable state. For each new line, only returns variables that have changed.

```python
DeltaTracker()
```

| Method | Returns | Description |
|---|---|---|
| `compute_delta(line_no, local_vars)` | `dict` | Returns only changed variables with `old`, `new`, `type` keys |
| `display_deltas()` | `None` | Prints a formatted change log |

**Delta record shape:**

```python
{
    'var_name': {
        'old': str | None,     # Previous value (None if new variable)
        'new': str,            # Current value
        'type': 'new_variable' | 'changed'
    }
}
```

---

#### Class: `TraceFilter`

**File:** `pychronicle/tracer/trace_filter.py`
**Author:** Sunaina (Week 3)

Filters a `frame.f_locals` dictionary to remove Python internals that should not be stored.

```python
TraceFilter()
```

Automatically skips variables named: `__name__`, `__doc__`, `__package__`, `__loader__`, `__spec__`, `__builtins__`, `__file__`, `__cached__`, and any variable whose name starts with `__`.

Also skips variables of type `builtin_function_or_method`.

| Method | Returns | Description |
|---|---|---|
| `should_track(var_name, value)` | `bool` | True if the variable should be recorded |
| `filter_locals(local_vars)` | `dict` | Returns a filtered copy of the locals dict |
| `display_filtered(local_vars)` | `dict` | Filters and prints reduction stats |

---

#### Research Files

| File | Author | Purpose |
|---|---|---|
| `settrace_research.py` | Noah (Week 1) | Demo and documentation of how `sys.settrace` works |
| `performance_test.py` | Noah (Week 2) | Benchmarks storage insert speed at 100 / 1000 / 10 000 inserts |
| `tracer_benchmark.py` | Noah (Week 2) | End-to-end benchmark: native execution vs. traced execution |
| `memory_profiler.py` | Noah (Week 3) | Measures memory reduction from delta compression |
| `final_test.py` | Noah (Week 4) | End-to-end integration test covering all four modules |

---

### 3.3 Storage

**Location:** `pychronicle/storage/`

All storage classes are backed by a single SQLite database file (`pychronicle.db` by default, or `:memory:` for tests).

---

#### Class: `StateStorage` — Base Storage

**File:** `pychronicle/storage/__init__.py`
**Author:** Athrva (Week 1)

Creates the database schema and provides basic insert + retrieve operations.

```python
StateStorage(db_path: str = ":memory:")
```

| Method | Returns | Description |
|---|---|---|
| `insert_state(line_number, variable_name, value, event_type)` | `None` | Inserts one state record |
| `get_all_states()` | `list[tuple]` | Returns all records ordered by `line_number` |
| `close()` | `None` | Closes the SQLite connection |

---

#### Class: `AdvancedStorage` — Extended Queries

**File:** `pychronicle/storage/advanced_storage.py`
**Author:** Athrva (Week 2)

Extends `StateStorage` with variable-level and line-level query methods.

```python
AdvancedStorage(db_path: str = "pychronicle.db")
```

| Method | Returns | Description |
|---|---|---|
| `get_variable_history(variable_name)` | `list[tuple]` | All states for a named variable |
| `get_states_at_line(line_number)` | `list[tuple]` | All variable states at a given line |
| `get_summary()` | `list[tuple]` | Per-variable change count, first line, last line |
| `display_summary()` | `None` | Formatted table of the summary |

---

#### Class: `QueryEngine` — Search Queries

**File:** `pychronicle/storage/query_engine.py`
**Author:** Athrva (Week 2)

Provides search and range queries over stored state.

```python
QueryEngine(db_path: str = "pychronicle.db")
```

| Method | Returns | Description |
|---|---|---|
| `search_by_value(value)` | `list[tuple]` | All states where serialized value contains the search string |
| `get_line_range(start_line, end_line)` | `list[tuple]` | All states between two line numbers |
| `get_latest_state()` | `list[tuple]` | Most recent recorded value for each variable |

---

#### Class: `StateExporter` — Export

**File:** `pychronicle/storage/state_exporter.py`
**Author:** Athrva (Week 3)

Exports stored states to JSON or CSV files.

```python
StateExporter(db_path: str = "pychronicle.db")
```

| Method | Description |
|---|---|
| `export_to_json(output_file)` | Writes all states to a JSON file |
| `export_to_csv(output_file)` | Writes all states to a CSV file |
| `export_summary()` | Prints total state count and tracked variable names |

---

#### Class: `StorageStats` — Analytics

**File:** `pychronicle/storage/storage_stats.py`
**Author:** Athrva (Week 3)

Provides aggregate statistics about the stored trace.

```python
StorageStats(db_path: str = "pychronicle.db")
```

| Method | Returns | Description |
|---|---|---|
| `get_total_states()` | `int` | Total number of stored state records |
| `get_unique_variables()` | `int` | Count of distinct variable names tracked |
| `get_most_changed()` | `list[tuple]` | Top 5 variables by change count |
| `display_stats()` | `None` | Prints a full stats summary |

---

### 3.4 UI

**Location:** `pychronicle/ui/`

---

#### Class: `TimelineUI`

**File:** `pychronicle/ui/timeline.py`
**Author:** Sunaina (Week 2)

A Textual terminal application that loads stored states from the database and presents them as a navigable timeline.

```python
TimelineUI(db_path: str = "pychronicle.db")
```

**Layout:**
- **Status bar** — shows total state count and keyboard shortcuts
- **Timeline panel (left)** — scrollable list of state entries with the current position marked `►`
- **Code panel (right)** — detail view: line number, variable name, value, timestamp, event type

**Keyboard controls:**

| Key | Action |
|---|---|
| `←` / `→` | Step backward / forward through states |
| `Q` | Quit |

**Run the UI:**

```bash
python -m pychronicle.ui.timeline
```

---

#### Class: `WatchVariables`

**File:** `pychronicle/ui/watch_variables.py`
**Author:** Sunaina (Week 2)

A non-interactive watcher that prints a focused change history for specific named variables.

```python
WatchVariables(db_path: str = "pychronicle.db")
```

| Method | Description |
|---|---|
| `add_watch(variable_name)` | Registers a variable to track |
| `get_watch_history()` | Prints per-watched-variable change history with timestamps |
| `display_timeline()` | Prints each variable's value changes as a `→`-separated timeline |

---

### 3.5 CLI

**Location:** `pychronicle/cli/`
**Author:** Sunaina + Athrva (Week 4)

A Click-based command-line interface providing the main user-facing entry point.

#### Commands

```
pychronicle [OPTIONS] COMMAND [ARGS]
```

| Command | Arguments | Options | Description |
|---|---|---|---|
| `run` | `script` (path) | `--db PATH` | Trace a Python script and store results |
| `history` | — | `--db PATH` | Print the last 20 stored execution states |
| `watch` | `variable` (name) | `--db PATH` | Print full change history of a named variable |

All commands default to `pychronicle.db` if `--db` is not specified.

**Examples:**

```bash
# Trace a script
pychronicle run myscript.py

# Use a custom database file
pychronicle run myscript.py --db session1.db

# Show execution history
pychronicle history --db session1.db

# Watch a specific variable
pychronicle watch total --db session1.db
```

#### Helper: `cli_utils.py`

Provides display utilities used by CLI commands:

| Function | Description |
|---|---|
| `print_header()` | Prints the PyChronicle version banner |
| `print_state(state)` | Formats a single state row |
| `get_stats(db_path)` | Returns dict with `total_states`, `unique_vars`, `unique_lines` |
| `print_stats(db_path)` | Prints the stats dict to the terminal |

---

## 4. Database Schema

PyChronicle uses a single SQLite table.

```sql
CREATE TABLE IF NOT EXISTS variable_states (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp        TEXT    NOT NULL,     -- ISO 8601 datetime string
    line_number      INTEGER NOT NULL,     -- Source line where capture occurred
    variable_name    TEXT    NOT NULL,     -- Name of the variable
    serialized_value TEXT,                 -- JSON-encoded string representation
    event_type       TEXT                  -- 'assignment', 'changed', 'new_variable'
);

CREATE INDEX IF NOT EXISTS idx_line ON variable_states(line_number);
```

**Notes:**
- `serialized_value` is stored as `json.dumps(str(value))` — a JSON string of the Python string representation.
- The index on `line_number` supports fast time-travel queries by source position.
- In-memory mode (`:memory:`) is used in all unit and performance tests to avoid file I/O.

---

## 5. Data Flow

A full tracing session with the `CompressedTracer` follows this path:

```
Target script (myscript.py)
        │
        ▼
sys.settrace(CompressedTracer._trace)
        │
        │  [For each executed line:]
        ▼
TraceFilter.filter_locals(frame.f_locals)
  → Removes __dunder__ vars and builtins
        │
        ▼
DeltaTracker.compute_delta(line_no, filtered)
  → Compares against previous line's state
  → Returns only NEW or CHANGED variables
        │
        ├── [No changes] → skip (skipped += 1)
        │
        └── [Changes present]
              ▼
        StateStorage.insert_state(line_no, var, value, event_type)
          → Persists to SQLite with timestamp
```

After execution, the user can:
- View the timeline via the TUI (`TimelineUI`)
- Query specific variables via `WatchVariables` or `QueryEngine`
- Export to JSON/CSV via `StateExporter`
- Browse via CLI (`pychronicle history`, `pychronicle watch`)

---

## 6. Installation & Setup

### Prerequisites

- Python 3.11+
- pip

### Install

```bash
pip install -r requirements.txt
```

**Key dependencies:**

| Package | Version | Purpose |
|---|---|---|
| `click` | 8.2.1 | CLI framework |
| `textual` | (implicit) | Terminal UI framework |
| `sqlite3` | stdlib | State database |
| `ast` | stdlib | AST parsing |
| `sys` | stdlib | `sys.settrace` hook |

> Note: The `requirements.txt` also includes Flask, SQLAlchemy, and related packages in preparation for the MeshWeaver web dashboard (Month 2 project).

### Running Without Install

All modules are importable from the project root:

```bash
cd infotact-advanced-python-main

# Run tracer directly
python -m pychronicle.tracer test_script.py

# Run CLI
python -m pychronicle.cli.main run test_script.py

# Launch TUI
python -m pychronicle.ui.timeline
```

---

## 7. Usage Guide

### Basic: Trace a Script

```python
from pychronicle.tracer.compressed_tracer import CompressedTracer

tracer = CompressedTracer("session.db")
tracer.run("myscript.py")
```

### Query History After Tracing

```python
from pychronicle.storage.advanced_storage import AdvancedStorage

db = AdvancedStorage("session.db")

# See all states of a variable
db.get_variable_history("total")

# See all variables at line 10
db.get_states_at_line(10)

# See summary table
db.display_summary()
```

### Search the Trace

```python
from pychronicle.storage.query_engine import QueryEngine

engine = QueryEngine("session.db")

# Find all states where a variable equaled 15
engine.search_by_value("15")

# Get states between lines 5 and 20
engine.get_line_range(5, 20)

# Get the final value of every variable
engine.get_latest_state()
```

### Export

```python
from pychronicle.storage.state_exporter import StateExporter

exporter = StateExporter("session.db")
exporter.export_to_json("trace.json")
exporter.export_to_csv("trace.csv")
```

### Watch Specific Variables

```python
from pychronicle.ui.watch_variables import WatchVariables

watcher = WatchVariables("session.db")
watcher.add_watch("total")
watcher.add_watch("result")
watcher.get_watch_history()
watcher.display_timeline()
```

---

## 8. Testing

### End-to-End Test

```bash
python -m pychronicle.tracer.final_test
```

Covers four test stages:
1. **TraceFilter** — verifies dunder removal and user-variable retention
2. **DeltaTracker** — verifies change detection and no-change skipping
3. **StateStorage** — verifies insert and retrieval
4. **Full trace** — runs `CompressedTracer` against `test_script.py`

### Storage Unit Test

```bash
python -m pychronicle.storage.test_storage
```

Tests schema creation, single insert, multi-insert, retrieval, and 1,000-insert performance.

### Performance Tests

```bash
python -m pychronicle.tracer.performance_test    # Storage speed: 100 / 1K / 10K inserts
python -m pychronicle.tracer.tracer_benchmark    # Native vs traced execution time
python -m pychronicle.tracer.memory_profiler     # Compression memory reduction
```

---

## 9. Performance Benchmarks

Results from Week 2–3 benchmarking (Noah):

| Metric | Value |
|---|---|
| Storage throughput | ~5,000 inserts/second |
| 1,000-insert time | < 0.2 seconds |
| 10,000-insert time | < 2 seconds |
| Delta compression savings | ~90% on typical scripts |
| Memory reduction (compression) | ~90% vs. naive all-states approach |

The storage throughput exceeds the realistic maximum of `sys.settrace` line events for most scripts, making the storage layer the non-bottleneck.

---

## 10. Future Work — MeshWeaver

Month 2 of the Infotact Advanced Python Engineering program targets **MeshWeaver**, a decentralized P2P asynchronous task broker. This project shares the repository (`meshweaver/` package placeholder) and the same team.

**Planned stack:**
- `asyncio` — event loop and coroutine orchestration
- Kademlia DHT — peer discovery and task routing
- `cloudpickle` — task serialization across processes
- Flask + SQLAlchemy — web dashboard and REST API (dependencies pre-installed in `requirements.txt`)

The `meshweaver/__init__.py` package stub is in place; implementation begins Month 2.
