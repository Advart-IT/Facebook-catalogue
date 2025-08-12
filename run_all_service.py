# run_all_service.py
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+
import run_all  # imports run_once()

IST = ZoneInfo("Asia/Kolkata")
RUN_HOUR = 0    # 00:01 IST daily
RUN_MIN  = 1

def seconds_until_next_run(now_ist: datetime) -> float:
    today_run = now_ist.replace(hour=RUN_HOUR, minute=RUN_MIN, second=0, microsecond=0)
    next_run = today_run if now_ist < today_run else (today_run + timedelta(days=1))
    return (next_run - now_ist).total_seconds()

def main():
    print("run_all_service: starting scheduler (12:01 IST daily)")
    while True:
        now_ist = datetime.now(IST)
        sleep_s = max(1, int(seconds_until_next_run(now_ist)))
        print(f"Sleeping {sleep_s}s until next run at 12:01 IST...")
        time.sleep(sleep_s)
        try:
            print("Running run_all.run_once() ...")
            failed = run_all.run_once()
            print(f"run_all finished. failed={failed}")
        except Exception as e:
            print(f"run_all crashed: {e}")

if __name__ == "__main__":
    main()
