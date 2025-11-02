<<<<<<< HEAD
from .viewer import viewer_task
from .lover import lover_task
from .worker import run_worker
from utils.logger import log_message

def hybrid_task(cl, config):
    
    log_message("--- Running Viewer Task (Hybrid) ---")
    viewer_task(cl, config)
    log_message("--- Running Lover Task (Hybrid) ---")
    lover_task(cl, config)
    log_message("--- Hybrid Task Cycle Complete ---")

def run_hybrid(config):
    log_message("HYBRID MODE: View + Love")
    run_worker(config, hybrid_task)
=======
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
>>>>>>> 328ddc985d31dd6fa23c6463835628e2a959e950
