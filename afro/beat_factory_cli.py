"""
beat_factory_cli.py
───────────────────
Interactive Command Center for Afro-house & Amapiano Production.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.markdown import Markdown

# Import engines for guidance
from vocal_guidance_engine import VocalGuidanceEngine

try:
    import factory_db
except ImportError:
    pass

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    banner = """
    [bold cyan]╔════════════════════════════════════════════════════════════╗[/bold cyan]
    [bold cyan]║[/bold cyan] [bold white]   Afro-house & Amapiano BEAT FACTORY (Master KG Style)  [/bold white] [bold cyan]║[/bold cyan]
    [bold cyan]╚════════════════════════════════════════════════════════════╝[/bold cyan]
    """
    console.print(banner)

def list_history():
    """Fetches history from the SQLite DB."""
    try:
        rows = factory_db.get_top_genomes(limit=10)
        if not rows:
            console.print("[yellow]No production history found.[/yellow]")
            return None
        
        table = Table(title="Recent Factory Output")
        table.add_column("Hex ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("BPM", justify="right")
        table.add_column("Score", justify="right", style="green")
        table.add_column("Timestamp", style="dim")
        
        for r in rows:
            table.add_row(
                r['hex_id'], 
                r['title'], 
                f"{r['bpm']:.1f}", 
                f"{r['composite_score']:.2f}",
                str(r['timestamp'])[:16]
            )
        console.print(table)
        return rows
    except Exception as e:
        console.print(f"[red]Error reading database: {e}[/red]")
        return None

def show_story_guide(blueprint):
    """Generates and displays the vocal/story guidance."""
    console.print("\n" + Panel("[bold magenta]🎤 SONG STORY & VOCAL GUIDE[/bold magenta]"))
    
    vocal_engine = VocalGuidanceEngine()
    guide = vocal_engine.generate_guide(blueprint.get("scenes", []))
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Scene", style="dim", width=15)
    table.add_column("Vocal Pattern / Story Beats", style="white")
    
    for entry in guide:
        # Find original scene for story_beats
        orig_scene = next((s for s in blueprint.get("scenes", []) if s['name'] == entry['scene']), {})
        story_beats = orig_scene.get("story_beats", "N/A")
        
        content = f"[bold cyan]Flow:[/bold cyan] {entry['pattern']}\n"
        content += f"[bold yellow]Theme:[/bold yellow] {story_beats}\n"
        content += "[italic dim]" + "\n".join(entry['story_placeholders']) + "[/italic dim]"
        
        table.add_row(
            f"{entry['scene']}\n({entry['bars']} bars)",
            content
        )
        table.add_section()
        
    console.print(table)

def produce_new_beat():
    """Guides user through producing a new beat."""
    console.print(Panel("[bold green]NEW PRODUCTION REQUEST[/bold green]"))
    prompt = Prompt.ask("Describe the vibe (e.g., 'Soulful Amapiano with deep logs')")
    optimize = Confirm.ask("Run genetic optimization (slow but better quality)?")
    trials = 0
    if optimize:
        trials = IntPrompt.ask("Number of optimization trials", default=10)
    
    cmd = [sys.executable, "run_pipeline.py", "--prompt", prompt]
    if optimize:
        cmd += ["--optimize", "--trials", str(trials)]
    
    hex_id = run_with_progress(cmd, "Generating new story and groove...")
    
    if hex_id:
        # Load blueprint to show story guide
        bp_path = Path("output") / hex_id / "blueprint.json"
        if bp_path.exists():
            blueprint = json.loads(bp_path.read_text())
            show_story_guide(blueprint)

def optimize_existing():
    """Combinatoronics mode: rearrange an existing beat."""
    rows = list_history()
    if not rows: return
    
    target_hex = Prompt.ask("Enter Hex ID to rearrange (or 'back')")
    if target_hex.lower() == 'back': return
    
    trials = IntPrompt.ask("Number of rearrangement trials", default=15)
    
    cmd = [sys.executable, "run_pipeline.py", "--source-beat", target_hex, "--optimize", "--trials", str(trials)]
    hex_id = run_with_progress(cmd, f"Rearranging and optimizing {target_hex}...")
    
    if hex_id:
        bp_path = Path("output") / hex_id / "blueprint.json"
        if bp_path.exists():
            blueprint = json.loads(bp_path.read_text())
            show_story_guide(blueprint)

# ... imports ...
from workflow_tracker import tracker

# ... rest of file ...

def run_with_progress(cmd, initial_text):
    """Runs the pipeline and shows a status spinner. Returns last Hex ID."""
    console.print(f"\n[bold yellow]>>> Starting Production Pipeline...[/bold yellow]")
    
    last_hex = None
    with console.status(f"[bold green]{initial_text}[/bold green]") as status:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            clean_line = line.strip()
            if "STEP 1" in clean_line:
                status.update("[bold cyan]Step 1: AI Brain Composition...[/bold cyan]")
            elif "STEP 2" in clean_line:
                status.update("[bold cyan]Step 2: Story-Driven MIDI Orchestration...[/bold cyan]")
            elif "STEP 3" in clean_line:
                status.update("[bold cyan]Step 3: Asset-Aware Rendering...[/bold cyan]")
            elif "STEP 4" in clean_line:
                status.update("[bold cyan]Step 4: DSP Mastering Chain...[/bold cyan]")
            
            if "[HEX]" in clean_line:
                last_hex = clean_line.split(":")[-1].strip()
                console.print(f"  {clean_line}")
            if "[OPT]" in clean_line or "[DB]" in clean_line:
                console.print(f"  {clean_line}")

        process.wait()
    
    if process.returncode == 0:
        console.print("\n[bold green]✅ Production Success![/bold green]")
        # Display the evolution tracker summary
        from workflow_tracker import tracker
        console.print("\n" + Panel(tracker.get_summary_table(), border_style="blue"))
        return last_hex
    else:
        console.print("\n[bold red]❌ Production failed.[/bold red]")
        return None

def main_menu():
    while True:
        clear_screen()
        show_banner()
        
        console.print("[1] 🎹 Produce New Beat (AI Story)")
        console.print("[2] 🧬 Optimize Existing Beat (Combinatoronics)")
        console.print("[3] 📜 View Factory History")
        console.print("[4] 📝 Manual AI Entry (API Fallback)")
        console.print("[q] 🚪 Exit")
        
        choice = Prompt.ask("\nSelect action", choices=["1", "2", "3", "4", "q"])
        
        if choice == "1":
            produce_new_beat()
            Prompt.ask("\nPress Enter to return to menu")
        elif choice == "2":
            optimize_existing()
            Prompt.ask("\nPress Enter to return to menu")
        elif choice == "3":
            clear_screen()
            show_banner()
            list_history()
            Prompt.ask("\nPress Enter to return to menu")
        elif choice == "4":
            manual_ai_entry()
        elif choice == "q":
            break

def manual_ai_entry():
    clear_screen()
    show_banner()
    console.print(Panel("[bold yellow]MANUAL AI FALLBACK MODE[/bold yellow]"))
    console.print("1. Open [bold cyan]MASTER_PROMPT.md[/bold cyan] and copy its content.")
    console.print("2. Paste it into ChatGPT, Claude, or any browser AI.")
    console.print("3. Copy the [bold green]JSON[/bold green] output from the AI.")
    console.print("4. Paste that JSON into [bold cyan]input/manual_blueprint.json[/bold cyan].")
    
    ready = Confirm.ask("\nHave you saved the JSON to input/manual_blueprint.json?")
    if ready:
        optimize = Confirm.ask("Run genetic optimization on this manual blueprint?")
        trials = 0
        if optimize:
            trials = IntPrompt.ask("Number of optimization trials", default=10)
        
        cmd = [sys.executable, "run_pipeline.py", "--manual"]
        if optimize:
            cmd += ["--optimize", "--trials", str(trials)]
            
        hex_id = run_with_progress(cmd, "Processing manual AI blueprint...")
        if hex_id:
            bp_path = Path("output") / hex_id / "blueprint.json"
            if bp_path.exists():
                show_story_guide(json.loads(bp_path.read_text()))
        Prompt.ask("\nPress Enter to return to menu")

if __name__ == "__main__":
    if not Path("beat_factory.db").exists():
        factory_db.init_db()
    main_menu()
