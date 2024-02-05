import os
import sys
import shlex
import select
import asyncio
import argparse
import subprocess

from functools import wraps
from threading import Thread, Event

from starlette.responses import JSONResponse
from starlette.routing import WebSocketRoute, Route
from starlette.websockets import WebSocketState, WebSocket

from starlette.applications import Starlette

__version__ = "0.0.2"

tasks = []


def get_event_loop():
  try:
    loop = asyncio.get_running_loop()
  except RuntimeError:
    loop = asyncio.new_event_loop()
  return loop


def force_sync(fn):

  @wraps(fn)
  def wrapper(*args, **kwargs):
    res = fn(*args, **kwargs)
    if asyncio.iscoroutine(res):
      return get_event_loop().run_until_complete(res)
    return res

  return wrapper


def task(func, handler=Thread, *targs, **tkwargs):

  @wraps(func)
  def wrapper(*args, **kwargs):
    tkwargs['daemon'] = True
    event = Event()
    event.set()

    thread = handler(*targs,
                     target=force_sync(func),
                     args=(event, *args),
                     kwargs=kwargs,
                     **tkwargs)
    thread.start()
    return event

  return wrapper


class TermConnection:

  def __init__(self, socket, config=None):
    self.socket = socket
    self.running = Event()
    self.config = config or {'fd': None, 'child_pid': None}
    self.proc = None

  async def forward_output(self):
    max_read_bytes = 1024 * 200
    chunk = ""
    should_read = True

    try:
      while self.running.is_set():
        if self.socket.client_state == WebSocketState.DISCONNECTED:
          break

        if self.config.get("fd"):
          timeout_sec = 0
          (data_ready, _, _) = select.select(
            [self.config["fd"]], [], [], timeout_sec
          )
          if data_ready:
            output = os.read(
              self.config["fd"],
              max_read_bytes
            ).decode(errors="ignore")
            await self.socket.send_text(output)

            # while should_read:

            #                 if len(output) <= 1:
            #                                 should_read = False
            #                 else:
            #                                 chunk = chunk + output

            # await self.socket.send_text(
            #                 str(len(chunk)) + ":;:" + chunk)
            # chunk = ""
            # should_read = True

        await asyncio.sleep(0.1)
    except Exception as e:
      print(repr(e))
    finally:
      self.running.clear()

  def pty_input(self, data):
    """
    Write to the child pty. The pty sees this as if you are typing in a real terminal.
    """
    if self.config.get("fd"):
      os.write(self.config["fd"], data.encode())

  def resize(self, data):
    if self.config.get("fd"):
      set_winsize(self.config["fd"], data["rows"], data["cols"])

  def connect(self, term_id):
    import pty

    if self.config.get("child_pid"):
      # already started child process, don't start another
      return

    # create child process attached to a pty we can read from and write to
    (child_pid, fd) = pty.fork()
    if child_pid == 0:
      cmd = self.config.get("cmd")
      shell = self.config.get("shell")

      subprocess.run(cmd, shell=shell)

      config['terms'].pop(term_id)
      asyncio.set_event_loop(get_event_loop())
    else:
      self.config["fd"] = fd
      self.config["child_pid"] = child_pid

      set_winsize(fd, 50, 50)
      return True

  def terminate(self):
    self.running.clear()

  async def listener(self):
    while self.running.is_set():
      await asyncio.sleep(0.1)
      if (self.socket.client_state == WebSocketState.DISCONNECTED):
        break

      try:
        message = await self.socket.receive_text()
      except Exception:
        return self.running.clear()

      if message:
        self.pty_input(message)
      else:
        return self.running.clear()


config = {'terms': {}}
# logging.getLogger("werkzeug").setLevel(logging.ERROR)


def set_winsize(fd, row, col, xpix=0, ypix=0):
  import termios
  import fcntl
  import struct

  # logging.debug("setting window size with termios")
  winsize = struct.pack("HHHH", row, col, xpix, ypix)
  fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


async def resize(request):
  term_id = request.path_params['term_id']
  term = (config['terms'].get(term_id))

  if term:
    term.resize(await request.json())
  return JSONResponse({'success': True})


async def terminate_executor(request):
  term_id = request.path_params['term_id']
  exec = (config['terms'].get(term_id))

  if exec: exec.terminate()
  return JSONResponse({'success': True, 'code': 1})


async def handler(websocket):
  term_id = websocket.path_params['term_id']
  cmd = websocket.query_params.get('cmd') or config.get('cmd')
  shell = websocket.query_params.get("shell") != None
  await websocket.accept()

  cmd = ([cmd] if shell else shlex.split(cmd)) if isinstance(cmd, str) else cmd

  term = config['terms'].get(term_id)

  if not term:
    term = TermConnection(websocket, {'cmd': cmd, "shell": shell})
    config['terms'][term_id] = term
    term.running.set()

    term.connect(term_id)
  else:
    term.socket = websocket
    term.running.set()

  # print(f'Connected to term: {term_id} > {cmd[0]}')

  try:
    task1 = asyncio.create_task(term.listener())
    task2 = asyncio.create_task(term.forward_output())
    await asyncio.gather(task1, task2)
  except Exception as e:
    pass

  term.running.clear()

  # if shell:
  # config['terms'].pop(term_id)
  # del term

  try:
    await websocket.close()
  except Exception:
    pass


async def executor(websocket: WebSocket):
  '''
                Executor function to handle execution of termux programs.
                '''

  cmd = websocket.query_params.get('cmd')
  await websocket.accept()

  if not cmd:
    return await websocket.close()

  data = {}

  proc = await asyncio.create_subprocess_shell(cmd,
                                               stdout=asyncio.subprocess.PIPE,
                                               stderr=asyncio.subprocess.PIPE)

  stdout, stderr = await proc.communicate()

  if stdout:
    data["stdout"] = stdout.decode()

  if stderr:
    data["stderr"] = stderr.decode()

  await websocket.send_json({"code": proc.returncode, **data})
  return await websocket.close()


app = Starlette(routes=[
  WebSocketRoute('/execute', endpoint=executor),
  WebSocketRoute('/terminal/{term_id}', endpoint=handler),
  Route('/resize/{term_id}', endpoint=resize, methods=['POST']),
  Route('/terminate/{term_id}', endpoint=terminate_executor, methods=['POST'])
])

if __name__ == "__main__":
  # from aiohttp import web
  # from aiohttp_asgi import ASGIResource
  # from aiohttp.web_runner import GracefulExit
  import uvicorn

  parser = argparse.ArgumentParser(
    description=("A fully functional terminal in your browser. "),
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  )
  parser.add_argument("-p",
                      "--port",
                      default=9001,
                      help="port to run server on",
                      type=int)
  parser.add_argument(
    "--host",
    default="127.0.0.1",
    help="host to run server on (use 0.0.0.0 to allow access from other hosts)",
  )
  # parser.add_argument(
  #                 "--debug", action="store_true",
  #                 help="debug the server"
  # )
  parser.add_argument("-v",
                      "--version",
                      action="store_true",
                      help="print version and exit")
  parser.add_argument("-c",
                      "--command",
                      default="bash",
                      help="Command to run in the terminal")

  args = parser.parse_args()
  if args.version:
    print(__version__)
    sys.exit(0)

  config["cmd"] = shlex.split(args.command)

  # aiohttp_app = web.Application()
  # asgi_resource = ASGIResource(app, root_path="/")
  # aiohttp_app.router.register_resource(asgi_resource)
  # asgi_resource.lifespan_mount(aiohttp_app)

  uvicorn.run(app, host=args.host, port=args.port)
  # try:
  # web.run_app(
  #                 aiohttp_app, host=args.host, port=args.port,
  #                 reuse_port=True
  # )
  # except KeyboardInterrupt:
  # raise GracefulExit()
