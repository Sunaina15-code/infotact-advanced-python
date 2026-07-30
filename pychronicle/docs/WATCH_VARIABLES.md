# Watch Variables Feature - User Guide

## Overview
The Watch Variables feature allows you to track specific variable values throughout your program's execution timeline. This is essential for debugging complex state changes and understanding variable behavior.

## Features

### 1. Interactive UI
- **Add/Remove watches** on any variable
- **Real-time history** showing all value changes
- **Timeline view** with line numbers and timestamps
- **Export to CSV** for external analysis

### 2. CLI Commands
```bash
# Launch interactive UI
pychronicle watch ui

# Add variables to watch
pychronicle watch add variable1 variable2 variable3

# Show history of specific variables
pychronicle watch history x y z

# Show timeline view
pychronicle watch timeline counter result

# Compare two variables
pychronicle watch compare var1 var2

# List all available variables
pychronicle watch list-all
