from starlette.requests import Request

def get_db(request: Request):
    return request.app.state._db
