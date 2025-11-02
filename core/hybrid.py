from core.viewer import run_viewer
from core.lover import run_lover
import threading, time
from utils.logger import log_message

def run_hybrid(config):
    log_message("HYBRID MODE: View + Love")

    def start_viewer():
        run_viewer(config)

    def start_lover():
        run_lover(config)

    t1 = threading.Thread(target=start_viewer, daemon=True)
    t2 = threading.Thread(target=start_lover, daemon=True)
    t1.start(); t2.start()
    t1.join(); t2.join()
