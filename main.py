import os
import sys
import subprocess
import requests
import platform
import shutil
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from rich.text import Text
import inquirer

console = Console()

PAPER_API_BASE = "https://api.papermc.io/v2/projects/paper"
PURPUR_API_BASE = "https://api.purpurmc.org/v2/purpur"

AIKARS_FLAGS = (
    "java -Xms{ram} -Xmx{ram} "
    "-XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 "
    "-XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch "
    "-XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M "
    "-XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 "
    "-XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 "
    "-XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem "
    "-XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs "
    "-Daikars.new.flags=true -jar {jar_name} nogui"
)

def get_versions(software):
    """Fetch available Minecraft versions."""
    url = PAPER_API_BASE if software == "Paper" else PURPUR_API_BASE
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["versions"]
    except requests.RequestException as e:
        console.print(f"[bold red]Error fetching versions:[/bold red] {e}")
        sys.exit(1)

def get_builds(software, version):
    """Fetch available builds for a specific version."""
    url = f"{PAPER_API_BASE}/versions/{version}" if software == "Paper" else f"{PURPUR_API_BASE}/{version}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if software == "Paper":
            # Paper returns a list of integers
            return [str(b) for b in data["builds"]]
        else:
            # Purpur returns a list of strings in 'all'
            return data["builds"]["all"]
    except requests.RequestException as e:
        console.print(f"[bold red]Error fetching builds:[/bold red] {e}")
        sys.exit(1)

def download_server(software, version, build):
    """Download the server JAR."""
    jar_name = f"{software.lower()}-{version}-{build}.jar"
    
    if software == "Paper":
        url = f"{PAPER_API_BASE}/versions/{version}/builds/{build}/downloads/paper-{version}-{build}.jar"
    else:
        url = f"{PURPUR_API_BASE}/{version}/{build}/download"
    
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))
            
            with Progress() as progress:
                task = progress.add_task(f"[cyan]Downloading {jar_name}...", total=total_size)
                with open(jar_name, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                        progress.update(task, advance=len(chunk))
        
        console.print(f"[bold green]Successfully downloaded {jar_name}![/bold green]")
        return jar_name
    except requests.RequestException as e:
        console.print(f"[bold red]Error downloading server:[/bold red] {e}")
        return None

def agree_to_eula():
    """Auto-agree to the Mojang EULA."""
    console.print("[yellow]Auto-agreeing to EULA...[/yellow]")
    with open("eula.txt", "w") as f:
        f.write("eula=true\n")
    console.print("[green]EULA agreed.[/green]")

def check_java():
    """Check for Java installation."""
    console.print(Panel("Checking Java Runtime Environment", style="bold blue"))
    try:
        result = subprocess.run(["java", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[green]Java is installed:[/green]\n{result.stderr.strip()}")
            return True
        else:
            console.print("[bold red]Java command failed. Please ensure Java is installed and in your PATH.[/bold red]")
            return False
    except FileNotFoundError:
        console.print("[bold red]Java executable not found. Please install Java.[/bold red]")
        return False

def create_start_script(jar_name, ram=None):
    """Create a start.sh script with Aikar's flags."""
    content = "#!/bin/sh\n" + AIKARS_FLAGS.format(ram=ram, jar_name=jar_name)
    
    try:
        with open("start.sh", "w") as f:
            f.write(content)
        # Make executable
        st = os.stat("start.sh")
        os.chmod("start.sh", st.st_mode | 0o111)
        console.print("[green]Created start.sh with Aikar's flags.[/green]")
        return True
    except IOError as e:
        console.print(f"[bold red]Error creating start script:[/bold red] {e}")
        return False

def start_server(jar_name, ram=None, use_script=False):
    """Start the Minecraft server."""
    
    if use_script:
        console.print(Panel(f"Starting Server via start.sh", style="bold green"))
        cmd = ["./start.sh"]
    else:
        console.print(Panel(f"Starting Server: {jar_name}", style="bold green"))
        
        if not ram:
            ram_q = [
                inquirer.Text("ram", message="Enter amount of RAM to allocate (e.g., 2G, 4G)", default="2G")
            ]
            ram_ans = inquirer.prompt(ram_q)
            if not ram_ans: return
            ram = ram_ans["ram"]

        cmd = ["java", f"-Xms{ram}", f"-Xmx{ram}", "-jar", jar_name, "nogui"]
    
    console.print(f"[dim]Running command: {' '.join(cmd)}[/dim]")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped.[/yellow]")

def main():
    console.print(Panel.fit("Minecraft Server Setup Utility", style="bold magenta"))

    # 1. Select Software
    software_q = [
        inquirer.List("software",
                      message="Select Server Software",
                      choices=["Paper", "Purpur"],
                      carousel=True)
    ]
    software_ans = inquirer.prompt(software_q)
    if not software_ans: return
    software = software_ans["software"]

    # 2. Select Version
    versions = get_versions(software)
    versions.reverse()
    
    version_q = [
        inquirer.List("version",
                      message=f"Select {software} Version",
                      choices=versions,
                      carousel=True)
    ]
    version_ans = inquirer.prompt(version_q)
    if not version_ans: return
    selected_version = version_ans["version"]

    # 3. Select Build
    builds = get_builds(software, selected_version)
    latest_build = builds[-1]
    
    console.print(f"[blue]Latest build for {software} {selected_version} is {latest_build}.[/blue]")
    
    confirm = [inquirer.Confirm("download", message=f"Download {software} {selected_version} build {latest_build}?", default=True)]
    if not inquirer.prompt(confirm)["download"]:
        console.print("[yellow]Aborted.[/yellow]")
        return

    # 4. Download
    jar_file = download_server(software, selected_version, latest_build)
    if not jar_file:
        return

    # 5. EULA
    if not os.path.exists("eula.txt"):
        eula_q = [inquirer.Confirm("eula", message="Do you agree to the Mojang EULA?", default=True)]
        if inquirer.prompt(eula_q)["eula"]:
            agree_to_eula()
        else:
            console.print("[red]You must agree to the EULA to run the server.[/red]")
            return
    else:
        console.print("[dim]eula.txt already exists.[/dim]")

    # 6. Check Java
    check_q = [inquirer.Confirm("check_java", message="Check Java Runtime?", default=True)]
    if inquirer.prompt(check_q)["check_java"]:
        if not check_java():
            console.print("[yellow]Warning: Java check failed. Server might not start.[/yellow]")

    # 7. Create Start Script
    script_created = False
    ram_allocated = None
    
    script_q = [inquirer.Confirm("create_script", message="Create start.sh with Aikar's flags?", default=True)]
    if inquirer.prompt(script_q)["create_script"]:
        ram_q = [inquirer.Text("ram", message="Enter amount of RAM to allocate (e.g., 2G, 4G)", default="4G")]
        ram_ans = inquirer.prompt(ram_q)
        if ram_ans:
            ram_allocated = ram_ans["ram"]
            if create_start_script(jar_file, ram_allocated):
                script_created = True

    # 8. Start Server
    start_q = [inquirer.Confirm("start", message="Start the server now?", default=True)]
    if inquirer.prompt(start_q)["start"]:
        start_server(jar_file, ram=ram_allocated, use_script=script_created)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting...[/bold red]")
