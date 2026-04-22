# run_all.py
import os, sys, subprocess, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(ROOT, "logs")

# Use correct package names (match folder case; important on Linux!)
MODULES = [
    ("bee_facebook_csv",         "Beelittle.bee_facebook_csv"),
    ("bee_google_csv",           "Beelittle.bee_google_csv"),
    ("zing_facebook_csv",        "zing.zing_facebook_csv"),
    ("zing_google_csv",          "zing.zig_google_csv"),
    ("prathiksham_facebook_csv", "Prathiksham.pkm_facebook_csv"),
    ("prathiksham_google_csv",   "Prathiksham.pkm_google_csv"),
]

def run_once() -> int:
    os.makedirs(LOG_DIR, exist_ok=True)
    procs = []
    for log_name, module in MODULES:
        log_path = os.path.join(LOG_DIR, f"{log_name}.log")
        log = open(log_path, "a", encoding="utf-8")
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(f"\n=== {stamp} start -m {module} ===\n"); log.flush()

        p = subprocess.Popen(
            [sys.executable, "-m", module],
            cwd=ROOT,
            stdout=log,
            stderr=log,
            env={**os.environ, "PYTHONUTF8": "1"},
        )
        procs.append((log_name, p, log))

    failed = 0
    for name, p, log in procs:
        rc = p.wait()
        log.write(f"=== exit {rc} ===\n"); log.close()
        print(f"{name}: {'OK' if rc == 0 else f'FAILED ({rc})'}")
        if rc != 0:
            failed += 1
    return failed

if __name__ == "__main__":
    # still works as a one-shot runner
    sys.exit(run_once())
