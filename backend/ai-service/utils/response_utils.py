def success_response(mode, data):

    return {

        "success": True,

        "mode": mode,

        "data": data

    }


def error_response(message):

    return {

        "success": False,

        "error": message

    }