# MeshWeaver - Dashboard - Aug 5 - Noah
# Live CLI dashboard showing mesh topology

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from datetime import datetime

console = Console()

class MeshDashboard:
    def __init__(self):
        self.nodes = {}
        self.tasks = []

    def add_node(self, node_id, host, port, cpu=0, status="active"):
        self.nodes[node_id] = {
            'host': host,
            'port': port,
            'cpu': cpu,
            'status': status,
            'last_seen': datetime.now().strftime("%H:%M:%S")
        }

    def add_task(self, task_id, func_name, status, node_id):
        self.tasks.append({
            'id': task_id,
            'function': func_name,
            'status': status,
            'node': node_id,
            'time': datetime.now().strftime("%H:%M:%S")
        })

    def display(self):
        console.clear()
        console.print(Panel(
            "[bold green]MeshWeaver - P2P Task Broker Dashboard[/bold green]",
            style="green"
        ))

        # Nodes table
        node_table = Table(
            title="Active Nodes",
            box=box.ROUNDED,
            style="blue"
        )
        node_table.add_column("Node ID", style="cyan")
        node_table.add_column("Address", style="white")
        node_table.add_column("CPU %", style="yellow")
        node_table.add_column("Status", style="green")
        node_table.add_column("Last Seen", style="white")

        for node_id, info in self.nodes.items():
            status_color = "green" if info['status'] == "active" else "red"
            node_table.add_row(
                node_id[:12],
                f"{info['host']}:{info['port']}",
                f"{info['cpu']}%",
                f"[{status_color}]{info['status']}[/{status_color}]",
                info['last_seen']
            )

        console.print(node_table)

        # Tasks table
        task_table = Table(
            title="Task Execution",
            box=box.ROUNDED,
            style="purple"
        )
        task_table.add_column("Task ID", style="cyan")
        task_table.add_column("Function", style="white")
        task_table.add_column("Status", style="yellow")
        task_table.add_column("Node", style="white")
        task_table.add_column("Time", style="white")

        for task in self.tasks[-10:]:
            status_color = "green" if task['status'] == "complete" else "yellow"
            task_table.add_row(
                task['id'],
                task['function'],
                f"[{status_color}]{task['status']}[/{status_color}]",
                task['node'][:12],
                task['time']
            )

        console.print(task_table)

if __name__ == "__main__":
    dashboard = MeshDashboard()

    # Demo data
    dashboard.add_node("node1abc", "127.0.0.1", 8001, cpu=23)
    dashboard.add_node("node2def", "127.0.0.1", 8002, cpu=45)
    dashboard.add_node("node3ghi", "127.0.0.1", 8003, cpu=12)

    dashboard.add_task("t001", "add_numbers", "complete", "node1abc")
    dashboard.add_task("t002", "ml_compute", "running", "node2def")
    dashboard.add_task("t003", "data_process", "pending", "node3ghi")

    dashboard.display()
# Aug 5 update
