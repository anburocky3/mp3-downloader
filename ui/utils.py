import os
import sys
from rich.console import Console

console = Console()

def clear_screen():
    if sys.platform.startswith('win'):
        os.system('cls')
    else:
        console.clear()
