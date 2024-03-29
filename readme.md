# Acode Terminal Plugin

Terminal plugin for acode

> **Note**
> If the terminal is open but not prompting or when you type nothing is being
inputed, simply pressing enter should fix it.

> **Server Updates**
> If you use `Acode Terminal` server, ensure to update server whenever you update the plugin

<img src="https://raw.githubusercontent.com/7HR4IZ3/acode-terminal-plugin/main/img/screenshot.jpg" />

---------
Whats new
---------
<details>
  <summary><em>v 1.0.304</em></summary>
  <ul>
    <li>You can now hold the arrow buttons down.</li>
  </ul>
</details>


---------

Features 🔥
----------

- Create and manage multiple terminals using tabs.
- `State management`: terminals are recreated if you close acode while the
terminal is still open (if the server is still active when you reopen acode, you
can continue exactly where you stopped)
- `Terminal Actions`: These are actions provided by backends or developers and are
available throught the right options button on the plugin page header.
Default actions are ("Go to directory", "Create terminal", "close terminal", "clear
terminal"), `reconnect to server` is added by `WebsocketBackend` (and it's
inheriting backends), "kill program" is added by `ExecutorBackend`.
- Customizable: You can change the terminal theme, fontsize, cursor style etc
from the settings page.
- Works out-the-box with `AcodeX Server`
- Use backends standalone (see examples below)

**Keyboard Bindings**

- Use `ctrl++` to increase font size.
- Use `ctrl+-` to decrease font size.
- Use `ctrl+shift+q` to close the active terminal.
- Use `ctrl+shift+n` to create new terminal.
- Use `ctrl+shift+v` to paste copied text.
- Use `ctrl+shift+left` to go to the previous terminal
- Use `ctrl+shift+right` to go to the next terminal

---------
Video tutorial
---------

<a href="https://youtube.com/shorts/bzxbtBPac6w?si=CoeYKX33m-MRsJO9">Server Setup</a>

<a href="https://youtu.be/ZzGpksYvWcc?feature=shared">Usage</a>

## Requirements

This plugin, requires the [Termux](https://termux.dev/en/) app.

A `pty-server` server is needed to use this plugin.

You can use the following pty-servers

- AcodeX Server
- Acode Terminal Server

---------
Installation
---------

> **NOTE**
> You can skip this if you already have `AcodeX Server` and want to use that instead.

### Acode Terminal Server

1. Install the plugin on Acode App.
2. Install Python3 and Python3 PIP.
3. Download the server python script.
4. Install server requirements.

**For termux**:

```bash
pkg update && pkg upgrade -y
pkg install python python-pip -y
```

**For other linux distro (like ubuntu)**

```bash
apt update && sudo apt upgrade -y
sudo apt install python python-pip -y
```

**Download server script**

```bash
curl -sL https://raw.githubusercontent.com/7HR4IZ3/acode-terminal-plugin/main/termServer.py > termServer.py 
```

**Install requirements**

```bash
pip install starlette uvicorn websockets
```

**Or at once**

```bash
pkg update && pkg upgrade -y
pkg install python python-pip -y

curl -sL https://raw.githubusercontent.com/7HR4IZ3/acode-terminal-plugin/main/termServer.py > termServer.py
pip install starlette uvicorn websockets
```

> **NOTE**
> `Acode Terminal` server is a python asgi web application so you
need a ASGI server like `uvicorn` to run it.

---------
How To Use
---------

<details>
  <summary>
    <em>Acode Terminal Server</em>
  </summary>

  <ul>
    <li>
      Navigate to where you downloaded the server python script.
    </li>
    <li>Run `python &lt;server_file&gt;.py`</li>
  </ul>
</details>

<details>
  <summary>
    <em>AcodeX Server</em>
  </summary>

  <ul>
    <li>open termux and run: `acodex-server`</li>
  </ul>
</details>

**Acode Terminal**

- Start the server in Termux.
- Acode Terminal adds a sidebutton (if your acode version supports it) else it adds a terminal button to the top header.
- Plus `+` icon to create new session
- Plus arrow down icon near the '+' icon to select the backend to use.

> **Note:**

> The `termux` option refers to the `Acode Terminal` server.

> The `acodex` option refers to the `AcodeX` server.

> The `executor` option requires `Acode Terminal` server and allows you to specify the command to run **eg:** ssh connections `ssh user@127.0.0.1:21` or other shell like `zsh`.

> The `acode` option is meant to be a terminal for `Acode` where other plugin
> can expose commands for the users.

- The `✗` button is for closing the terminal.

**Coming Soon**

- Support Split Terminals (Two or more terminals in the same tab).

---------
API
---------

```javascript
const terminal = acode.require("acode.terminal");
```


**The following attributes are exported**

- `.addBackend(backend)`: Add backend to the plugin (Also adds a backend
option in the terminal ui)
- `.removeBackend(backend)`: Remove backend from the plugin.

- `.addTerminal(terminal)`: Add terminal to the plugin.
- `.removeTerminal(terminal)`: Remove terminal from the plugin.

- `.createTerminal(container, { terminal, backend, termId, termData, backendConfig })`:
Creates a new terminal object (if `terminal` is a string it finds the
Terminal in the plugin terminals with the `.name` or `.alias` equaling
`terminal`, `backendConfig` is passed to the `backend` constructor if it is a string).
(if `backend` is a string it finds the
Backends in the plugin backends with the `.name` or `.alias` equaling
`backend`). Returns a new `Terminal` object.
- `.newTerminal(terminalConfig)`: Creates a new tab and calls
`.createTerminal` with the tab container and `terminalConfig`.
- `async .execute(command, { signal })` Execute `command` and return output
`signal` (`AbortController.signal`) is optional and can be used to abort
command. Returns object `{ stdout, stderr }` where `stdout` is the program
output and `stderr` is any error that occured.
- `.run(command, onstdout)` Run `command` and call `onstdout` when something is
logged. Return a `ExecutorBackend` instance so you can send input using the
`.send` method (check examples)
- `.show()` Show the terminal is not visible.

##### Backends

> Handles communication between the terminal and the server

The following `Backends` are also exported:

- `TerminalBackend` (Base Backend)
- `WebsocketBackend` [extends `TerminalBackend`] (Base Backend for websockets
based servers)
- `AcodeBackend` [extends `TerminalBackend`] (Backend for acode)
- `AcodeXBackend` [extends `WebsocketBackend`] (Backend for `AcodeX` server)
- `TermuxBackend` [extends `WebsocketBackend`] (Backend for `Acode Terminal` server)
- `ExecutorBackend` [extends `WebsocketBackend`] (Backend)

</br>
<details>
  <summary>
    <em>Attributes and methods</em>
  </summary>
  
  </br>

  <details>
    <summary>
      <em>TerminalBackend</em>
    </summary>

  <ul>
  <li><em>constructor(config, termId)</em>: <em>termId</em> refers to the id for the
  current terminal (optional)</li>
  <li><em>.setup(terminal)</em>: Called when the backend is attached a terminal.</li>
  <li><em>.send(data)</em>: Called when the user enters an input in the terminal.</li>
  <li><em>.close()</em>: Close backend.</li>
  <li><em>.getState()</em>: Returns an object containing the backend state.</li>
  <li><em>static</em> <em>.fromState(state, cls=TerminalBackend)</em>: Returns an instance of
  <em>cls</em> generated from <em>state</em> object.</li>
  <li><em>static</em> <em>.icon</em>: Backend icon class name.</li>
  <li><em>static</em> <em>.alias</em>: Backend name.</li>
  <li><em>.name</em>: Same as <em>.alias</em>.</li>
  </ul>
  </details>
  
  </br>

  <details>
    <summary>
      <em>WebsocketBackend</em>
    </summary>

  <ul>
  <li><em>constructor({ url }, termId)</em>: <em>termId</em> refers to the id for the
  current terminal (optional), <em>url</em> can be a string or function (async or
  sync) that returns a string, it represents the server url (also optional)</li>
  <li><em>async</em> <em>.init(url)</em>: Manually initialize or reinitialize the backend.</li>
  <li><em>.resize({ rows, cols })</em>: Called when the terminal is resized.</li>
  <li><em>.socket</em>: Websocket connection object to server.</li>

  <li><em>.onmessage(message)</em>: Called when the <em>socket</em> recieves a message.</li>
  <li><em>.onopen()</em>: Called when the <em>socket</em> is opened.</li>
  <li><em>.onclose()</em>: Called when the <em>socket</em> is closed.</li>
  </ul>
  </details>
  
</br>

  <details>
    <summary>
      <em>ExecutorBackend</em>
    </summary>

  <ul>
  <li><em>constructor({ command, ...args })</em>: <em>command</em> if specified refers to
  the command to run else it asks the user for the command (optional).
  <em>args</em> represents <em>WebsocketBackend.constructor</em> arguments</li>
  </ul>
  </details>


</details>
</br>

##### Terminals

> Renders the terminal ui, sends user input to the connected backend

The following `Terminals` are exported:

- `AcodeTerminal` (Base Terminal)

</br>
<details>
  <summary>
    <em>Attributes and methods</em>
  </summary>

  <ul>
    <li><em>constructor({ config, backend, termData, plugin })</em>: Execute the given
      command in the terminal. (<em>config</em> is an object which is passed to
      <em>xtermjs</em>, <em>backend</em> is the backend to connect the terminal to, <em>termData</em>
      is a string to prepopulate the terminal with, all are optional)</li>
    <li><em>.execute(command)</em>: Execute the given command in the terminal.</li>
    <li><em>.color(text, color, background, attributes)</em>: Format <em>text</em> so it is
      colored when printed in the terminal.</li>
    <li><em>.setBackend(backend)</em>: Set or change th4 terminal's backend.</li>
    <li><em>.setup(container, backend)</em>: Mount the terminal to the <em>container</em> and
      calls <em>setBackend</em> on <em>backend</em> if it is specified.</li>
    <li><em>.destroy()</em>: Close and destroy thr terminal, terminal bavkend and
      terminal tab (if available).</li>
    <li><em>.getState()</em>: Returns an object containing the terminal state.</li>
    <li><em>static</em> <em>.fromState(state, cls=AcodeTerminal)</em>: Returns an instance of
      <em>cls</em> generated from <em>state</em> object.</li>
    <li><em>.resize(cols, rows)</em>: Resize the terminal to <em>rows</em> x <em>cols</em>.</li>
    <li><em>.addTermOption(option, handler)</em>: Adds a terminal option (<em>option</em> can
      be a list of [text, icon], <em>handler</em> is the function to be called when the
      option is clicked).</li>
    <li><em>.termOptions</em>: List of options for the terminal.</li>
    <li><em>.termActions</em>: Object of option to handlers.</li>
    <li><em>.term</em>: Returns the <em>xtermjs</em> <em>Terminal</em> object.</li>
  </ul>
</details>
</br>

### Examples

**Create a terminal**
```javascript
const terminal = acode.require("acode.terminal");

// .createTerminal: creates a background terminal if container is null.
// .newTerminal: calls createTerminal then adds the terminal to the ui.

// Use default settings
await terminal.newTerminal();

// Specify backend by alias
await terminal.newTerminal({ backend: "termux", backendConfig: {} });

// Pass backend instance
let backend = new terminal.TermuxBackend({ command: "bash" });
await terminal.newTerminal({ backend });

// Create Terminal and backend seperately
let backend = new terminal.TermuxBackend({ command: "zsh" });
let terminal = await terminal.createTerminal();

// Connect terminal to backend
await terminal.setBackend(backend);
```

**Execute a termux command**
```javascript
// Get and alert the current terminal directory

let terminal = acode.require("acode.terminal");
let backend = new terminal.ExecutorBackend({
  command: `pwd`,
  onmessage(output) {
    acode.alert("Terminal Directory", output);
  }
});

// Or using a shorthand
let terminal = acode.require("acode.terminal");
terminal.execute("pwd").then(({ stdout, stderr }) => {
    console.log("Current directory is:", stdout);
});

```

**Start and interact with a termux program**
```javascript
let terminal = acode.require("acode.terminal");
let backend = new terminal.TermuxBackend({
  command: `node`,
  onmessage(output) {
    acode.alert("Output", output);
  }
});

// Wrap in a function so we can use async/await.
(async function() {
  let exit = false, input;
  
  while (!exit) {
    input = await acode.prompt("Input");

    if (!input) {
      break;
    }
  
    await backend.send(input + "\r");
  }
  backend.close();
})().catch(() => backend.close());

// Or if you want to interact with the program
let conn = terminal.run("node", (stdout) => {
    console.log("output:", stdout)
});
conn.send(`
fetch('http://example.com')
    .then(resp => resp.json())
    .then(resp => console.log(resp))
`);
conn.close();

// Optionally connect to a Terminal
let term = await terminal.newTerminal({ backend: backend || conn });
```

---------
Support
---------

**Drop a 🌟 [here](https://github.com/7HR4IZ3/acode-terminal-plugin)**



---------
Changelog
---------

<details>
  <summary><em>v 1.0.3</em></summary>
  <ul>
    <li>You can now use <em>run</em> and <em>execute</em> functions to run
    commands.</li>
    <li>Updated keyboard bindings.</li>
    <li>Updated server file</li>
  </ul>
</details>
