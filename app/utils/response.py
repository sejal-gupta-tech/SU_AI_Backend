from typing import Any, Dict, Optional

def success_response(message: str, data: Optional[Any] = None) -> Dict[str, Any]:
    response = {
        "success": True,
        "message": message,
    }
    if data is not None:
        response["data"] = data
    else:
        response["data"] = {}
    return response


def error_response(message: str, error_code: str, details: Optional[Any] = None) -> Dict[str, Any]:
    response = {
        "success": False,
        "message": message,
        "error": {
            "code": error_code
        }
    }
    if details is not None:
        response["error"]["details"] = details
    return response
