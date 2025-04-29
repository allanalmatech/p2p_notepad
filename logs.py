
import datetime

def log_event(event: str):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("p2p_log.txt", "a") as log_file:
        log_file.write(f"[{timestamp}] {event}\n")
