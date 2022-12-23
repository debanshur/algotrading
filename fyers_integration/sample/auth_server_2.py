import multiprocessing
from werkzeug import Request, Response, run_simple

from fyers_integration.sample.auth import get_json_value, update_json_key

q = []

def get_token() -> None:
    global q
    @Request.application
    def app(request: Request) -> Response:
        global q
        q = request.args
        return Response("", 204)

    run_simple("localhost", 27070, app)

if __name__ == "__main__":
    p = multiprocessing.Process(target=get_token, args=())
    p.start()
    print("waiting")
    token = q
    print(token)
    #wait till token updated -> maybe logged out
    #p.terminate()

    local_state = get_json_value('state')
    if(token['state'] == local_state):
        update_json_key('auth_code',token['auth_code'])
        p.terminate()


    #