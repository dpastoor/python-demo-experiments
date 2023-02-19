from fastapi import FastAPI, Request
import subprocess
import os
import uvicorn
import json
app = FastAPI()


def get_credentials(req):
    """
    Returns a dict containing "user" and "groups" information populated by
    the incoming request header "RStudio-Connect-Credentials".
    """
    is_dev = req.headers.get("x-rstudio-virtual-path")
    if is_dev:
        return {"user": os.environ['USER']}
    credential_header = req.headers.get("RStudio-Connect-Credentials")
    if not credential_header:
        return {}
    return json.loads(credential_header)

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World", "root_path": request.scope.get("root_path")}

@app.get("/whoami")
async def whoami(request: Request):
    user_metadata = get_credentials(request)
    username = user_metadata.get("user")
    if username is None:
        return {"message": "Howdy, stranger."}
    return {"message": f"So nice to see you, {username}."}



if __name__ == '__main__':
    path, port = '', 8000
    if 'RS_SERVER_URL' in os.environ and os.environ['RS_SERVER_URL']:
        import socketserver
        with socketserver.TCPServer(("localhost", 0), None) as s:
            port = s.server_address[1]
        path = subprocess.run(f'echo $(/usr/lib/rstudio-server/bin/rserver-url -l {port})',
    # going to be lazy and not write a regex. The issue with a simple replace is // --> / will also replace https:// to https:/ so
    # lets add an extra / there so then when we remove all // it'll go back to https://
                             stdout=subprocess.PIPE, shell=True).stdout.decode().strip().replace("://", ":///").replace("//", "/")
        # give some space from the printing of the command in the terminal
        print("")
        print(f"\033[96mserver proxy URL:\033[0m     \033[1m{path}\033[0m")
        print("")
    uvicorn.run(app, port = port, root_path = path)