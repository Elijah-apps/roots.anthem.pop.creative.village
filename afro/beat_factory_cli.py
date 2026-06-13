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
import shutil
import sqlite3
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
        table.add_column("Rating", justify="center")
        table.add_column("Timestamp", style="dim")
        
        for r in rows:
            pref = r.get('user_preference', 0)
            pref_str = "—"
            if pref == 1:
                pref_str = "[bold green]👍 Like[/bold green]"
            elif pref == -1:
                pref_str = "[bold red]👎 Dislike[/bold red]"
                
            table.add_row(
                r['hex_id'], 
                r['title'], 
                f"{r['bpm']:.1f}", 
                f"{r['composite_score']:.2f}",
                pref_str,
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
    prompt = Prompt.ask("Describe the vibe")
    
    console.print("\n[1] ⚡ [bold]Direct Production[/bold] (Fast, use AI's first draft)")
    console.print("[2] 🧬 [bold]Genetic Search[/bold] (Slower, runs trials to find best groove)")
    mode = Prompt.ask("Select mode", choices=["1", "2"], default="1")
    
    cmd = [sys.executable, "run_pipeline.py", "--prompt", prompt]
    if mode == "2":
        trials = IntPrompt.ask("Number of optimization trials", default=10)
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

def play_beat(hex_id):
    out_dir = Path("output") / hex_id
    audio_files = list(out_dir.glob(f"BEAT_{hex_id}.mp3")) + \
                  list(out_dir.glob(f"BEAT_{hex_id}.wav")) + \
                  list(out_dir.glob("MASTER.mp3")) + \
                  list(out_dir.glob("MASTER.wav"))
                  
    if not audio_files:
        console.print("[red]No audio file found to play.[/red]")
        return
        
    file_to_play = audio_files[0]
    console.print(f"[bold green]▶ Playing {file_to_play.name} in background...[/bold green]")
    played = False
    for player in ["xdg-open", "mpv", "ffplay", "aplay"]:
        if shutil.which(player):
            try:
                if player == "xdg-open":
                    subprocess.Popen([player, str(file_to_play)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif player == "ffplay":
                    subprocess.Popen([player, "-nodisp", "-autoexit", str(file_to_play)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif player == "mpv":
                    subprocess.Popen([player, "--no-video", str(file_to_play)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen([player, str(file_to_play)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                played = True
                console.print(f"[dim]Playback started via {player}.[/dim]")
                break
            except Exception:
                pass
    if not played:
        console.print(f"[yellow]Could not launch system player. File path: {file_to_play.absolute()}[/yellow]")

def view_details(hex_id):
    out_dir = Path("output") / hex_id
    bp_path = out_dir / "blueprint.json"
    lyrics_path = out_dir / "lyrics.txt"
    
    if bp_path.exists():
        try:
            bp = json.loads(bp_path.read_text())
            console.print(Panel(
                f"[bold cyan]🎵 Title: {bp.get('title', 'Untitled')}[/bold cyan]\n"
                f"[bold]BPM:[/bold] {bp.get('bpm', 124)} | [bold]Key:[/bold] {bp.get('key', 'Unknown')}\n"
                f"[bold]SoundFont ID:[/bold] {bp.get('selected_soundfont_id', 'N/A')}\n"
                f"[bold]Scenes:[/bold] {len(bp.get('scenes', []))} total",
                title=f"Beat Details: {hex_id}", border_style="cyan"
            ))
        except Exception as e:
            console.print(f"[red]Error reading blueprint: {e}[/red]")
            
    if lyrics_path.exists():
        console.print(Panel(lyrics_path.read_text(), title="Songwriter's Lyric Book", border_style="magenta"))
    else:
        if bp_path.exists():
            try:
                bp = json.loads(bp_path.read_text())
                lyrics_txt = ""
                for scene in bp.get("scenes", []):
                    lyrics_txt += f"--- {scene.get('name', 'Scene')} ---\n"
                    lyrics_txt += f"Vocal Vibe: {scene.get('story_beats', 'N/A')}\n"
                    if "lyrics" in scene:
                        lyrics_txt += f"Lyrics:\n{scene['lyrics']}\n"
                    lyrics_txt += "\n"
                console.print(Panel(lyrics_txt, title="Songwriter's Lyric Book (from blueprint)", border_style="magenta"))
            except Exception:
                console.print("[yellow]No lyrics or blueprint found.[/yellow]")

def toggle_preference(hex_id):
    pref = Prompt.ask("Rate this beat", choices=["like", "dislike", "neutral"])
    val = 1 if pref == "like" else (-1 if pref == "dislike" else 0)
    try:
        factory_db.update_preference(hex_id, val)
        console.print(f"[green]Preference rating for {hex_id} updated successfully![/green]")
    except Exception as e:
        console.print(f"[red]Error updating preference: {e}[/red]")

def delete_beat(hex_id):
    if Confirm.ask(f"[bold red]⚠️ Are you sure you want to permanently delete beat {hex_id}?[/bold red]"):
        try:
            out_dir = Path("output") / hex_id
            if out_dir.exists():
                shutil.rmtree(out_dir)
                console.print(f"[green]Deleted directory: {out_dir}[/green]")
            conn = sqlite3.connect("beat_factory.db")
            c = conn.cursor()
            c.execute("DELETE FROM beats WHERE hex_id = ?", (hex_id,))
            conn.commit()
            conn.close()
            console.print(f"[green]Deleted beat {hex_id} from SQLite database.[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Error deleting beat: {e}[/red]")
    return False

def history_menu():
    while True:
        clear_screen()
        show_banner()
        rows = list_history()
        if not rows:
            Prompt.ask("\nPress Enter to return to menu")
            return
            
        target_hex = Prompt.ask("\nEnter Hex ID to manage (or press Enter to go back)")
        if not target_hex:
            break
            
        hex_ids = [r['hex_id'] for r in rows]
        target_hex = target_hex.upper().strip()
        if target_hex not in hex_ids:
            console.print("[red]Invalid Hex ID. Please select from the list.[/red]")
            time.sleep(1.5)
            continue
            
        while True:
            clear_screen()
            show_banner()
            console.print(Panel(f"[bold cyan]🎵 Managing Beat: {target_hex}[/bold cyan]", border_style="cyan"))
            console.print("[p] ▶ Play Beat (Background playback)")
            console.print("[v] 🔍 View Blueprint & Lyrics")
            console.print("[l] 👍 Rate / Preference (Like/Dislike)")
            console.print("[d] ❌ Delete Beat")
            console.print("[r] 🔄 React & Refine")
            console.print("[b] ⬅ Back to History List")
            
            action = Prompt.ask("\nSelect action", choices=["p", "v", "l", "d", "r", "b"])
            
            if action == "p":
                play_beat(target_hex)
                Prompt.ask("\nPress Enter to continue")
            elif action == "v":
                view_details(target_hex)
                Prompt.ask("\nPress Enter to continue")
            elif action == "l":
                toggle_preference(target_hex)
                Prompt.ask("\nPress Enter to continue")
                break # Refresh history list
            elif action == "d":
                if delete_beat(target_hex):
                    Prompt.ask("\nPress Enter to continue")
                    break # Refresh history list
            elif action == "r":
                bp_path = Path("output") / target_hex / "blueprint.json"
                if not bp_path.exists():
                    console.print("[red]Original blueprint not found![/red]")
                    Prompt.ask("\nPress Enter to continue")
                    break
                original_json = bp_path.read_text()
                console.print(Panel("[bold yellow]REFINEMENT WORKFLOW[/bold yellow]"))
                console.print(f"1. Copy [bold cyan]MASTER_PROMPT.md[/bold cyan].")
                console.print(f"2. Use [bold green]REFINEMENT MODE[/bold green] in your Browser AI.")
                console.print(f"3. Paste your feedback.")
                console.print(f"4. Paste this original JSON when asked:")
                console.print(f"[dim]{original_json[:200]}...[/dim]")
                
                ready = Confirm.ask("\nHave you saved the refined JSON to input/manual_blueprint.json?")
                if ready:
                    cmd = [sys.executable, "run_pipeline.py", "--manual"]
                    hex_id = run_with_progress(cmd, "Applying AI refinement...")
                    if hex_id:
                        console.print(f"[green]Refinement complete! New Hex: {hex_id}[/green]")
                Prompt.ask("\nPress Enter to continue")
                break
            elif action == "b":
                break

def main_menu():
    while True:
        clear_screen()
        show_banner()
        
        console.print("[1] 🎹 Produce New Beat (AI Story)")
        console.print("[2] 🧬 Optimize Existing Beat (Combinatoronics)")
        console.print("[3] 📜 View Factory History")
        console.print("[4] 📝 Manual AI Entry (API Fallback)")
        console.print("[5] 🔄 React & Refine (Contextual Edit)")
        console.print("[q] 🚪 Exit")
        
        choice = Prompt.ask("\nSelect action", choices=["1", "2", "3", "4", "5", "q"])
        
        if choice == "1":
            produce_new_beat()
            Prompt.ask("\nPress Enter to return to menu")
        elif choice == "2":
            optimize_existing()
            Prompt.ask("\nPress Enter to return to menu")
        elif choice == "3":
            history_menu()
        elif choice == "4":
            manual_ai_entry()
        elif choice == "5":
            react_and_refine()
        elif choice == "q":
            break


def react_and_refine():
    clear_screen()
    show_banner()
    rows = list_history()
    if not rows:
        Prompt.ask("\nPress Enter to return to menu")
        return
    
    target_hex = Prompt.ask("Enter Hex ID to refine")
    reaction = Prompt.ask("What is your reaction? (e.g., 'Bass is too loud', 'Make it more soulful')")
    
    # Load original context
    bp_path = Path("output") / target_hex / "blueprint.json"
    if not bp_path.exists():
        console.print("[red]Original blueprint not found![/red]")
        return
    
    original_json = bp_path.read_text()
    
    console.print(Panel("[bold yellow]REFINEMENT WORKFLOW[/bold yellow]"))
    console.print(f"1. Copy [bold cyan]MASTER_PROMPT.md[/bold cyan].")
    console.print(f"2. Use [bold green]REFINEMENT MODE[/bold green] in your Browser AI.")
    console.print(f"3. Paste your feedback: [italic white]\"{reaction}\"[/italic white]")
    console.print(f"4. Paste this original JSON when asked:")
    console.print(f"[dim]{original_json[:200]}...[/dim]")
    
    ready = Confirm.ask("\nHave you saved the refined JSON to input/manual_blueprint.json?")
    if ready:
        cmd = [sys.executable, "run_pipeline.py", "--manual"]
        hex_id = run_with_progress(cmd, "Applying AI refinement...")
        if hex_id:
            console.print(f"[green]Refinement complete! New Hex: {hex_id}[/green]")
            tracker.log("ArrangementEngine", "Refinement", f"Applied reaction: {reaction}")
    Prompt.ask("\nPress Enter to return to menu")

def manual_ai_entry():
    clear_screen()
    show_banner()
    console.print(Panel("[bold yellow]MANUAL AI FALLBACK MODE (Asset-Aware)[/bold yellow]"))
    
    # AUTO-SYNC REGISTRY INTO PROMPT
    try:
        with open("sound_registry.json", "r") as f:
            registry = json.load(f)
        clean_registry = {
            "soundfonts": [{"id": s["id"], "name": s["name"], "tags": s.get("tags", []), "desc": s.get("description", "")} for s in registry.get("soundfonts", [])]
        }
        prompt_path = Path("MASTER_PROMPT.md")
        content = prompt_path.read_text()
        import re
        pattern = r"## 🎹 LOCAL ASSET REGISTRY.*?(?=## 📐 OUTPUT SCHEMA)"
        replacement = f"## 🎹 LOCAL ASSET REGISTRY (Use these IDs!)\n{json.dumps(clean_registry, indent=2)}\n\n"
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        prompt_path.write_text(new_content)
        console.print("[green]✅ Local Asset Registry synced to MASTER_PROMPT.md[/green]")
    except Exception as e:
        console.print(f"[red]Could not sync registry: {e}[/red]")

    console.print("\n1. Open [bold cyan]MASTER_PROMPT.md[/bold cyan] and copy its content.")
    console.print("2. Paste it into ChatGPT, Claude, or any browser AI.")
    console.print("3. Copy the [bold green]JSON[/bold green] output from the AI.")
    console.print("4. Paste that JSON into [bold cyan]input/manual_blueprint.json[/bold cyan].")
    
    ready = Confirm.ask("\nHave you saved the JSON to input/manual_blueprint.json?")
    if ready:
        manual_path = Path("input/manual_blueprint.json")
        try:
            with open(manual_path, "r") as f:
                data = json.load(f)
            
            if "manual_optimization" in data:
                console.print("[bold green]✨ Deep Manual Override detected! Skipping internal search.[/bold green]")
                cmd = [sys.executable, "run_pipeline.py", "--manual"]
            else:
                console.print("\n[1] ⚡ [bold]Direct Production[/bold]")
                console.print("[2] 🧬 [bold]Genetic Search[/bold]")
                mode = Prompt.ask("Select mode", choices=["1", "2"], default="1")
                cmd = [sys.executable, "run_pipeline.py", "--manual"]
                if mode == "2":
                    trials = IntPrompt.ask("Optimization trials", default=10)
                    cmd += ["--optimize", "--trials", str(trials)]
            
            hex_id = run_with_progress(cmd, "Processing manual AI blueprint...")
            if hex_id:
                show_story_guide(data)
        except Exception as e:
            console.print(f"[red]Error reading manual blueprint: {e}[/red]")
    Prompt.ask("\nPress Enter to return to menu")

if __name__ == "__main__":
    if not Path("beat_factory.db").exists():
        factory_db.init_db()
    main_menu()
