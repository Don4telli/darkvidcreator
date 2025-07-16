import os
import sys
import json

def test_moviepy():
    result = {
        "python_version": sys.version,
        "python_path": sys.path,
        "cwd": os.getcwd(),
        "files_in_cwd": os.listdir('.'),
        "moviepy_imported": False,
        "error": None
    }
    
    try:
        import moviepy.editor
        result["moviepy_imported"] = True
        result["moviepy_version"] = moviepy.__version__
        result["moviepy_path"] = moviepy.__file__
    except Exception as e:
        result["error"] = str(e)
        import traceback
        result["traceback"] = traceback.format_exc()
    
    return result

def lambda_handler(event, context):
    result = test_moviepy()
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        },
        'body': json.dumps(result, indent=2)
    }
