import subprocess
import time
import sys
import os


def run_python_code(code: str, input_data: str = "", timeout: int = 2) -> dict:
    temp_filename = "temp_code.py"
    
    with open(temp_filename, "w", encoding="utf-8") as f:
        f.write(code)
    
    start_time = time.time()
    
    try:
        process = subprocess.run(
            [sys.executable, temp_filename],
            input=input_data,    
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        execution_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "success" if process.returncode == 0 else "error",
            "output": process.stdout.strip(),
            "error": process.stderr.strip(),
            "time_ms": execution_time
        }
        
    except subprocess.TimeoutExpired:
        execution_time = round((time.time() - start_time) * 1000, 2)
        return {
            "status": "timeout",
            "output": "",
            "error": f"Time Limit Exceeded. Код выполнялся дольше {timeout} секунд.",
            "time_ms": execution_time
        }
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)