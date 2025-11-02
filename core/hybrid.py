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
