# Week 4 - Watch Variables CLI Commands
# CLI commands for variable watching functionality

import click
from pychronicle.storage import StateStorage
from ui.watch_variables import WatchVariables, WatchVariablesUI
import json


@click.group()
def watch():
    """Watch variable commands"""
    pass


@watch.command()
@click.argument('variables', nargs=-1, required=True)
@click.option('--db', default='pychronicle.db', help='Database path')
def add(variables, db):
    """Add variables to watch list"""
    watcher = WatchVariables(db)
    for var in variables:
        watcher.add_watch(var)


@watch.command()
@click.argument('variables', nargs=-1, required=True)
@click.option('--db', default='pychronicle.db', help='Database path')
def history(variables, db):
    """Show history of watched variables"""
    watcher = WatchVariables(db)
    for var in variables:
        watcher.add_watch(var)
    watcher.get_watch_history()


@watch.command()
@click.argument('variables', nargs=-1, required=True)
@click.option('--db', default='pychronicle.db', help='Database path')
def timeline(variables, db):
    """Show timeline of watched variables"""
    watcher = WatchVariables(db)
    for var in variables:
        watcher.add_watch(var)
    watcher.display_timeline()


@watch.command()
@click.option('--db', default='pychronicle.db', help='Database path')
def ui(db):
    """Launch interactive watch variables UI"""
    click.echo("🚀 Launching Watch Variables UI...")
    app = WatchVariablesUI(db_path=db)
    app.run()


@watch.command()
@click.argument('var1')
@click.argument('var2')
@click.option('--db', default='pychronicle.db', help='Database path')
def compare(var1, var2, db):
    """Compare two variables"""
    watcher = WatchVariables(db)
    watcher.add_watch(var1)
    watcher.add_watch(var2)
    watcher.compare_variables(var1, var2)


@watch.command()
@click.option('--db', default='pychronicle.db', help='Database path')
def list_all(db):
    """List all available variables in database"""
    storage = StateStorage(db)
    cursor = storage.conn.execute(
        '''SELECT DISTINCT variable_name, COUNT(*) as changes
           FROM variable_states 
           GROUP BY variable_name
           ORDER BY changes DESC'''
    )
    
    click.echo("\n" + "="*60)
    click.echo("📋 AVAILABLE VARIABLES")
    click.echo("="*60)
    
    for row in cursor.fetchall():
        click.echo(f"  {row[0]:<30} | {row[1]:4} changes")


if __name__ == "__main__":
    watch()
