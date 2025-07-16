import os
import sys
import json
import subprocess

def lambda_handler(event, context):
    # Get Python environment info
    python_info = {
        "python_version": sys.version,
        "python_path": sys.path,
        "current_working_directory": os.getcwd(),
        "files_in_cwd": os.listdir('.'),
        "installed_packages": str(subprocess.check_output([sys.executable, '-m', 'pip', 'list']).decode('utf-8')),
        "environment_vars": {k: v for k, v in os.environ.items() if 'PYTHON' in k or 'PATH' in k},
        "import_tests": {}
    }

    # Test basic imports
    def test_import(module_name):
        try:
            __import__(module_name)
            return {"success": True, "version": sys.modules[module_name].__version__ if hasattr(sys.modules[module_name], '__version__') else "No version"}
        except Exception as e:
            return {"success": False, "error": str(e), "type": type(e).__name__}

    # Test various imports
    python_info["import_tests"]["os"] = test_import("os")
    python_info["import_tests"]["sys"] = test_import("sys")
    python_info["import_tests"]["numpy"] = test_import("numpy")
    python_info["import_tests"]["PIL"] = test_import("PIL")
    python_info["import_tests"]["imageio"] = test_import("imageio")
    python_info["import_tests"]["moviepy"] = test_import("moviepy")
    
    # Try to import moviepy.editor specifically
    try:
        import moviepy.editor
        python_info["import_tests"]["moviepy.editor"] = {
            "success": True,
            "version": moviepy.__version__,
            "path": os.path.dirname(moviepy.__file__)
        }
    except Exception as e:
        python_info["import_tests"]["moviepy.editor"] = {
            "success": False,
            "error": str(e),
            "type": type(e).__name__,
            "traceback": str(sys.exc_info())
        }

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        },
        'body': json.dumps(python_info, indent=2, default=str)
    }
