from fastapi import Request

def get_resources(request:Request):
    """
    返回lifespan挂载的支援
    :param request:
    :return:
    """
    return request.app.state