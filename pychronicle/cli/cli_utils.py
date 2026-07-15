# Week 4 - CLI Utils - July 14 - Athrva
# Utility functions for CLI

import click
from pychronicle.storage import StateStorage

def print_header():
    click.echo("=" * 50)
    click.echo("  PyChronicle - Time Travel Debugger v1.0")
    click.echo("=" * 50)

def print_state(state):
    click.echo(
        f"Line {state[2]:3} | "
        f"{state[3]:<15} | "
        f"{state[4][:30]}"
    )

def get_stats(db_path="pychronicle.db"):
    storage = StateStorage(db_path)
    states = storage.get_all_states()
    vars = set(s[3] for s in states)
    lines = set(s[2] for s in states)
    return {
        'total_states': len(states),
        'unique_vars': len(vars),
        'unique_lines': len(lines)
    }

def print_stats(db_path="pychronicle.db"):
    stats = get_stats(db_path)
    click.echo("\n=== PyChronicle Stats ===")
    click.echo(f"Total states:    {stats['total_states']}")
    click.echo(f"Unique variables:{stats['unique_vars']}")
    click.echo(f"Lines traced:    {stats['unique_lines']}")

if __name__ == "__main__":
    print_header()
    print_stats()
    