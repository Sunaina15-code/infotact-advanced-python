# Week 4 - CLI Main - July 14 - Sunaina
# PyChronicle CLI using Click

import click
import sys
from pychronicle.tracer.compressed_tracer import CompressedTracer
from pychronicle.storage import StateStorage

@click.group()
def cli():
    """PyChronicle - Time Travel Debugger"""
    pass

@cli.command()
@click.argument('script')
@click.option('--db', default='pychronicle.db', help='Database path')
def run(script, db):
    """Run and trace a Python script"""
    click.echo(f"🔍 Tracing: {script}")
    tracer = CompressedTracer(db_path=db)
    tracer.run(script)
    click.echo("✅ Tracing complete!")

@cli.command()
@click.option('--db', default='pychronicle.db', help='Database path')
def history(db):
    """Show execution history"""
    storage = StateStorage(db)
    states = storage.get_all_states()
    click.echo(f"\n=== Execution History ({len(states)} states) ===")
    for state in states[:20]:
        click.echo(f"Line {state[2]:3} | {state[3]:<15} = {state[4]}")

@cli.command()
@click.argument('variable')
@click.option('--db', default='pychronicle.db', help='Database path')
def watch(variable, db):
    """Watch a specific variable"""
    storage = StateStorage(db)
    cursor = storage.conn.execute(
        'SELECT * FROM variable_states WHERE variable_name = ?',
        (variable,)
    )
    states = cursor.fetchall()
    click.echo(f"\n=== History of '{variable}' ===")
    for s in states:
        click.echo(f"Line {s[2]:3} | {s[4]}")

if __name__ == "__main__":
    cli()