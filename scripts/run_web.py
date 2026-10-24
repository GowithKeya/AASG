import os
import sys
import time
import subprocess

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)

    print("==================================================")
    print("       AASG / CY-03 Agent Firewall Launcher       ")
    print("==================================================")
    print(f"Working Directory: {base_dir}")

    # Initialize DB tables if not present
    try:
        from shared.db import init_db
        init_db()
        print("[INIT] Database initialized successfully.")
    except Exception as e:
        print(f"[WARN] Database init warning: {e}")

    python_exe = sys.executable

    print("\n[1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    api_proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "guard.api:app", "--host", "127.0.0.1", "--port", "8000"]
    )
    time.sleep(2)

    print("[2/2] Starting Streamlit Security Dashboard on http://localhost:8501 ...")
    dashboard_proc = subprocess.Popen(
        [python_exe, "-m", "streamlit", "run", "dashboard/app.py", "--server.port", "8501", "--server.headless", "true"]
    )

    print("\n" + "="*50)
    print("  [SUCCESS] AASG Services are running:")
    print("   - Web Dashboard: http://localhost:8501")
    print("   - API Docs:      http://127.0.0.1:8000/docs")
    print("   - API Endpoints: http://127.0.0.1:8000")
    print("="*50)
    print("Press Ctrl+C to stop both services.\n")

    try:
        api_proc.wait()
        dashboard_proc.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        api_proc.terminate()
        dashboard_proc.terminate()
        api_proc.wait()
        dashboard_proc.wait()
        print("AASG services cleanly stopped.")

if __name__ == "__main__":
    main()
