"""
workflow_tracker.py
───────────────────
Tracks the evolution of musical intent through the pipeline engines.
"""

import time
from rich.console import Console
from rich.table import Table

console = Console()

class WorkflowTracker:
    def __init__(self):
        self.logs = []
        self.start_time = time.time()

    def log(self, engine, action, detail):
        """Records a transformation step."""
        self.logs.append({
            "timestamp": time.time() - self.start_time,
            "engine": engine,
            "action": action,
            "detail": detail
        })

    def get_summary_table(self):
        """Returns a Rich table summarizing the AI refinement workflow."""
        table = Table(title="🤖 AI WORKFLOW EVOLUTION LOG", show_header=True, header_style="bold blue")
        table.add_column("Time (s)", justify="right", style="dim")
        table.add_column("Specialist", style="cyan")
        table.add_column("Transformation", style="white")
        table.add_column("Insight", style="italic yellow")

        for entry in self.logs:
            table.add_row(
                f"{entry['timestamp']:.2f}",
                entry['engine'],
                entry['action'],
                entry['detail']
            )
        return table

# Global instance
tracker = WorkflowTracker()
