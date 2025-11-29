import subprocess
import sys
from pathlib import Path

YELLOW = "\033[1;33m"
RESET = "\033[0m"

TOOLS = {
    "1": Path("CAPyle_releaseV2/release/main.py"),
    "2": Path("CAPyle_releaseV2/release/wind_dir_effect.py")
}

def main():
    print("Welcome to the COM3524 Tool Runner!")
    print(f"{YELLOW}⚠️WARNING: Any changes to files in this container WILL be reflected in host files (i.e. repo contents) due to mounting.{RESET}")
    while True:
        print("\nSelect a tool to run:")
        print("1. Team 13 CAPyle Tool")
        print("2. Wind Direction Effect Test")
        print("3. Exit")

        choice = input("Choose from the above options: ").strip()
        print(f"You entered: {choice}")

        if choice == "3":
            print("Exiting program.")
            sys.exit(0)

        script = TOOLS.get(choice)

        if not script or not script.exists():
            print("Invalid selection or script not found.")
            continue

        try:
            subprocess.run([sys.executable, str(script)], check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the script: {e}")
        except KeyboardInterrupt:
            print("\nExecution interrupted by user. Returning to menu.")
            continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user. Goodbye!")
        sys.exit(0)
