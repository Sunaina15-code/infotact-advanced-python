# PyChronicle - Week 1 Progress Report

## Team: Infotact Advanced Python Engineering
## Week: 1 (July 5-11, 2025)

## Completed Tasks

### 1. AST Parser (Sunaina)
- Built script to read target Python files
- Parses Abstract Syntax Tree
- Identifies all variable assignments
- Tested on test_script.py — found 9 assignments

### 2. Storage Schema (Athrva)
- Designed SQLite database schema
- Fields: id, timestamp, line_number, variable_name, serialized_value, event_type
- Added index on line_number for fast queries
- Performance tested: 1000 inserts successfully

### 3. Tracer Module (Sunaina)
- Implemented sys.settrace
- Records execution flow of target script
- Captures variable states during runtime
- Saves states to SQLite database

### 4. TUI Scaffolding (Noah)
- Initialized Textual App
- Created basic layout
- Code view pane added
- Timeline slider structure ready

## Project Structure