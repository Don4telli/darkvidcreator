import os
import sys
import json
import subprocess

def lambda_handler(event, context):
    # Get Python environment info
    env_info = {
        "python_version": sys.version,
        "executable": sys.executable,
        "path": sys.path,
        "cwd": os.getcwd(),
        "files_in_cwd": os.listdir('.'),
        "env_vars": {k: v for k, v in os.environ.items()}
    }
    
    # Try to list installed packages
    try:
        env_info["installed_packages"] = subprocess.check_output(
            [sys.executable, '-m', 'pip', 'freeze'],
            stderr=subprocess.STDOUT
        ).decode('utf-8')
    except Exception as e:
        env_info["pip_freeze_error"] = str(e)
    
    # Try to import moviepy
    try:
        import moviepy
        env_info["moviepy"] = {
            "version": moviepy.__version__,
            "path": os.path.dirname(moviepy.__file__)
        }
    except Exception as e:
        env_info["moviepy_error"] = str(e)
        env_info["moviepy_traceback"] = str(sys.exc_info())
    
    # Try to import moviepy.editor directly
    try:
        from moviepy import editor
        env_info["moviepy_editor"] = {"success": True}
    except Exception as e:
        env_info["moviepy_editor_error"] = str(e)
        env_info["moviepy_editor_traceback"] = str(sys.exc_info())
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        },
        'body': json.dumps(env_info, indent=2, default=str)
    }
