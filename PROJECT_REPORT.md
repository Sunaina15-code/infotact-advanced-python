# PyChronicle — Project Report

**Infotact Advanced Python Engineering**
**Month 1 | July 5–18, 2026**

---

## Executive Summary

PyChronicle is a time-travel execution debugger for Python, built over four weeks by a four-person team. The tool hooks into the Python interpreter via `sys.settrace` to capture variable states at every line of execution, stores them in a compressed SQLite database, and exposes them through both an interactive terminal UI and a command-line interface. All planned deliverables were completed on schedule.

---

## Team

| Member | Role | Primary Contributions |
|---|---|---|
| **Sunaina** | Team Lead | Tracer core, delta tracking, Timeline UI, Watch Variables, CLI |
| **Athrva** | Storage Engineer | Database schema, query engine, state exporter, stats, CLI utils |
| **John** | Documentation | Weekly progress reports, progress tracking |
| **Noah** | QA & Performance | sys.settrace research, performance benchmarking, memory profiling, final testing |

**Branch model:** each team member worked on their own named branch (`sunaina`, `athrva`, `john`, `noah`); Sunaina (Team Lead) merged to `main`.

---

## Week-by-Week Progress

### Week 1 — Foundations (July 5–11, 2025)

The first week established the core building blocks of PyChronicle: a working tracer, a storage schema, an AST static analyzer, and an initial TUI scaffold.

#### Sunaina
- Built `ASTParser` to read Python source files, walk the Abstract Syntax Tree, and identify all variable assignment locations
- Implemented the base `ExecutionTracer` using `sys.settrace` to hook into the Python interpreter and capture live variable states into SQLite
- Tested both modules on `test_script.py`; AST parser found 9 assignments

#### Athrva
- Designed the SQLite schema (`variable_states` table) with fields: `id`, `timestamp`, `line_number`, `variable_name`, `serialized_value`, `event_type`
- Added an index on `line_number` for fast time-travel queries
- Ran a performance baseline: 1,000 inserts completed successfully

#### Noah
- Researched and documented `sys.settrace` behavior (events, frame objects, tracing lifecycle)
- Built `SettraceDemo` — an annotated working demo capturing variable state through a simple arithmetic sequence

#### Noah (TUI Scaffolding)
- Initialized the Textual application shell
- Created the two-panel layout (timeline + code view)
- Added a timeline slider structure placeholder

**Week 1 Outcome:** Core tracer pipeline working end-to-end. Variable states captured and stored in SQLite.

---

### Week 2 — Optimization & UI (July 5–11, 2026)

Week 2 focused on reducing redundant storage and connecting the database to a live UI.

#### Sunaina
- Built `DeltaTracker` — tracks the previous variable state and emits only variables that have actually *changed* since the last line
- Built `OptimizedTracer` — integrates `DeltaTracker` with the base tracer; reports compression savings after each run
- Built `TimelineUI` — a full Textual TUI connected to the live SQLite database; left panel shows the timeline, right panel shows detailed state at the current position
- Built `WatchVariables` — lets users register named variables and view their entire change history in chronological order

#### Athrva
- Built `AdvancedStorage` (extends `StateStorage`) with per-variable history, per-line state snapshot, and summary queries
- Built `QueryEngine` — enables searching by value, filtering by line range, and retrieving the latest state of all variables

#### Noah
- Benchmarked storage performance at 100, 1,000, and 10,000 inserts
- Confirmed throughput exceeds ~5,000 inserts/second — well above the realistic `sys.settrace` event rate
- Benchmarked end-to-end tracer vs. native script execution for overhead measurement

#### John
- Wrote Week 2 progress documentation and tracked deliverable completion

**Week 2 Outcome:** Storage optimized with delta compression. UI connected to database. Watch Variables feature added.

---

### Week 3 — Compression & Export (July 13–18, 2026)

Week 3 introduced the full compression pipeline and data export capabilities.

#### Sunaina
- Built `TraceFilter` — a pre-delta filter that strips Python internal (`__dunder__`) variables and built-in function references before the delta check, further reducing noise
- Built `CompressedTracer` — the production tracer combining all three stages in sequence: `TraceFilter → DeltaTracker → StateStorage`; achieved up to ~90% memory savings compared to the Week 1 naive tracer

#### Athrva
- Built `StateExporter` — exports all stored states to JSON or CSV format with a simple function call
- Built `StorageStats` — provides aggregate analytics: total states, unique variable count, top-5 most-changed variables

#### Noah
- Built `MemoryProfiler` — a side-by-side measurement comparing uncompressed vs. compressed storage under identical conditions; confirmed ~90% record reduction

#### John
- Wrote Week 3 progress documentation

**Week 3 Outcome:** Full three-stage compression pipeline implemented. Export to JSON/CSV added. Memory usage reduced by ~90%.

---

### Week 4 — CLI Packaging & Final Review (July 14–18, 2026)

The final week packaged everything into a user-facing CLI and validated the complete system.

#### Sunaina
- Built `pychronicle/cli/main.py` using Click with three top-level commands:
  - `pychronicle run <script>` — trace a target script
  - `pychronicle history` — browse the stored execution history
  - `pychronicle watch <variable>` — inspect a named variable's full history

#### Athrva
- Built `cli_utils.py` — shared display helpers (`print_header`, `print_state`, `get_stats`, `print_stats`) used across CLI commands

#### Noah
- Built `final_test.py` — a four-stage end-to-end integration test covering `TraceFilter`, `DeltaTracker`, `StateStorage`, and `CompressedTracer` in sequence; all assertions pass

#### John
- Wrote Week 4 progress documentation and compiled the final review checklist

**Week 4 Outcome:** CLI packaging complete. `pychronicle run myscript.py` works end-to-end. All modules integrated and verified.

---

## Feature Completion Checklist

| Feature | Owner | Status |
|---|---|---|
| AST Parser | Sunaina | ✅ Complete |
| Execution Tracer (`sys.settrace`) | Sunaina | ✅ Complete |
| SQLite Storage schema | Athrva | ✅ Complete |
| Delta Compression | Sunaina | ✅ Complete |
| Variable Filtering (TraceFilter) | Sunaina | ✅ Complete |
| Compressed Tracer (full pipeline) | Sunaina | ✅ Complete |
| Terminal UI (Textual TimelineUI) | Sunaina | ✅ Complete |
| Watch Variables | Sunaina | ✅ Complete |
| Advanced Storage queries | Athrva | ✅ Complete |
| Query Engine | Athrva | ✅ Complete |
| State Exporter (JSON + CSV) | Athrva | ✅ Complete |
| Storage Statistics | Athrva | ✅ Complete |
| CLI (`run`, `history`, `watch`) | Sunaina + Athrva | ✅ Complete |
| Performance benchmarking | Noah | ✅ Complete |
| End-to-end test suite | Noah | ✅ Complete |
| Weekly documentation | John | ✅ Complete |

---

## Technical Highlights

### Delta Compression

The most impactful optimization. Instead of saving all variable values at every executed line, the `DeltaTracker` maintains a snapshot of the previous state and only emits entries when a value actually changes. On typical scripts this results in ~90% fewer database records — making time-travel queries faster and the database far smaller.

### Three-Stage Filter Pipeline

```
frame.f_locals
    → TraceFilter (remove Python internals)
    → DeltaTracker (remove unchanged values)
    → StateStorage (persist survivors only)
```

The three stages are independent and composable. Each has its own class and can be tested in isolation (which `final_test.py` does).

### sys.settrace as the Capture Mechanism

Python's `sys.settrace` fires a callback before every line executes, on every function call, and on every return. PyChronicle listens on the `'line'` event, reads `frame.f_locals` (the current local variable dictionary), and runs it through the filter pipeline. This captures computed values at runtime — not just static structure — which is why the tool is genuinely useful for debugging loops, conditionals, and function calls.

### SQLite for Zero-Dependency Persistence

Using SQLite (Python stdlib `sqlite3`) means no external database process, no network, and no configuration. A trace session is a single `.db` file that can be opened, queried, exported, or shared without any additional setup. The index on `line_number` makes time-travel by source position fast even for large traces.

---

## Performance Results

| Benchmark | Result |
|---|---|
| Storage throughput | ~5,000 inserts / second |
| 100-insert time | < 0.01 s |
| 1,000-insert time | < 0.2 s |
| 10,000-insert time | < 2 s |
| Delta compression savings | ~90% fewer records |
| Memory reduction vs. uncompressed | ~90% |

The storage layer comfortably outpaces the realistic event rate of `sys.settrace`, meaning I/O is not the bottleneck — the tracer itself runs at interpreter speed.

---

## Challenges & Solutions

| Challenge | Solution |
|---|---|
| Storing all variables at every line produced massive state counts | Introduced DeltaTracker in Week 2; cut records by ~90% |
| Python built-in and dunder variables polluted the trace | Introduced TraceFilter in Week 3 to strip them pre-delta |
| Connecting the live database to the UI during active tracing | Tracer writes synchronously; UI reads after execution completes — clean separation |
| CLI entry point needed to work against any `.db` file | Used Click's `--db` option with a sensible default throughout all commands |

---

## Repository Structure

```
infotact-advanced-python-main/
├── pychronicle/
│   ├── __init__.py
│   ├── ast_parser/
│   │   └── __init__.py           # ASTParser
│   ├── tracer/
│   │   ├── __init__.py           # ExecutionTracer (Week 1)
│   │   ├── delta_tracker.py      # DeltaTracker (Week 2)
│   │   ├── optimized_tracer.py   # OptimizedTracer (Week 2)
│   │   ├── trace_filter.py       # TraceFilter (Week 3)
│   │   ├── compressed_tracer.py  # CompressedTracer (Week 3) ← production
│   │   ├── settrace_research.py  # Noah: research + demo
│   │   ├── performance_test.py   # Noah: storage benchmarks
│   │   ├── tracer_benchmark.py   # Noah: end-to-end benchmark
│   │   ├── memory_profiler.py    # Noah: compression profiling
│   │   └── final_test.py         # Noah: e2e integration tests
│   ├── storage/
│   │   ├── __init__.py           # StateStorage (Week 1)
│   │   ├── advanced_storage.py   # AdvancedStorage (Week 2)
│   │   ├── query_engine.py       # QueryEngine (Week 2)
│   │   ├── state_exporter.py     # StateExporter (Week 3)
│   │   ├── storage_stats.py      # StorageStats (Week 3)
│   │   └── test_storage.py       # Athrva: schema tests
│   ├── ui/
│   │   ├── timeline.py           # TimelineUI — Textual TUI
│   │   └── watch_variables.py    # WatchVariables
│   ├── cli/
│   │   ├── main.py               # Click CLI (run / history / watch)
│   │   └── cli_utils.py          # Display helpers
│   └── WEEK1_PROGRESS.md … WEEK4_PROGRESS.md
├── meshweaver/
│   └── __init__.py               # Month 2 stub
├── test_script.py                # Sample target script
├── pychronicle.db                # Persistent trace database
├── requirements.txt
└── README.md
```

---

## Next Steps — Month 2: MeshWeaver

The team's Month 2 project is **MeshWeaver**, a decentralized peer-to-peer asynchronous task broker. It shares this repository (the `meshweaver/` stub is already in place) and builds on the same team foundation.

**Planned features:**
- `asyncio`-based event loop and coroutine task pipeline
- Kademlia DHT for peer discovery and distributed task routing
- `cloudpickle` for serializing Python callables and passing them between nodes
- Flask + SQLAlchemy REST API and web dashboard (dependencies pre-installed)

PyChronicle's export and storage patterns may inform MeshWeaver's own state persistence layer.

---

## Conclusion

PyChronicle was delivered on schedule with all eight planned features complete. The project demonstrated:

- **Advanced Python internals** — `sys.settrace`, `ast.walk`, `frame` objects
- **Storage engineering** — schema design, indexing, in-memory testing, delta compression
- **Software architecture** — staged pipeline design, class inheritance, separation of concerns
- **Developer tooling** — CLI packaging with Click, TUI with Textual
- **Performance discipline** — measured benchmarks at every optimization stage

The team is ready for Month 2.
