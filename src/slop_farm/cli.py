"""CLI interface for slop-farm agent task management."""

import argparse
from rich.console import Console
from rich.table import Table

console = Console()

def cmd_status():
    """Show farm status."""
    table = Table(title="🌱 slop-farm Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Version", "0.1.0")
    table.add_row("Agents active", "0")
    table.add_row("PRs open", "0")
    table.add_row("Reviews pending", "0")
    console.print(table)

def cmd_plant(task: str):
    """Plant a new task for agents."""
    console.print(f"[green]🌱 Planted task:[/green] {task}")
    console.print("[dim]Agents will discover and work on this task.[/dim]")

def cmd_harvest():
    """Harvest completed work."""
    console.print("[yellow]🌾 Harvesting completed tasks...[/yellow]")
    console.print("[green]✓ No ripe tasks to harvest.[/green]")

def main():
    parser = argparse.ArgumentParser(description="slop-farm — agent-governed task farming")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show farm status")
    
    plant = sub.add_parser("plant", help="Plant a new task")
    plant.add_argument("task", help="Task description")
    
    sub.add_parser("harvest", help="Harvest completed tasks")

    args = parser.parse_args()
    
    if args.command == "status":
        cmd_status()
    elif args.command == "plant":
        cmd_plant(args.task)
    elif args.command == "harvest":
        cmd_harvest()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
