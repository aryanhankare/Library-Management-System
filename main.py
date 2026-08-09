import schedule
import time
from datetime import datetime

from reminder import run_reminder_check


def main():
    # Print a startup banner so you know the service is running
    print("=" * 50)
    print("  SLiMS Automated Reminder Service")
    print("=" * 50)
    print(f"  Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Schedule: Daily at 08:00")
    print("  Press Ctrl+C to stop")
    print("=" * 50)

    # Schedule the reminder check to run every day at 08:00
    schedule.every().day.at("08:00").do(run_reminder_check)

    # Run one check immediately so you can verify without waiting
    print("\n  Running initial check now...")
    run_reminder_check()

    # Keep the script alive, checking every 60 seconds for pending jobs
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()