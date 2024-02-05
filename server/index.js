#!/usr/bin/env node

const express = require('express');
const expressWs = require('express-ws');
const pty = require('node-pty');
const commandLineArgs = require('command-line-args');

const optionDefinitions = [
  { name: 'port', alias: 'p', type: Number, defaultValue: 9001 },
  { name: 'shell', alias: 's', type: String, defaultValue: 'bash' },
];

const options = commandLineArgs(optionDefinitions);

const app = express();
const wsInstance = expressWs(app);

// Map to store terminals
const terminals = {};

// WebSocket endpoint for terminals
app.ws('/terminals/:terminalID', (ws, req) => {
  const terminalID = req.params.terminalID;

  // Create or retrieve terminal
  let term = terminals[terminalID];
  if (!term) {
    term = pty.spawn(options.shell, [], {
      name: 'xterm-color',
      cols: 80,
      rows: 24,
      cwd: process.env.HOME,
      env: process.env,
    });

    terminals[terminalID] = term;
  }

  // Handle data from WebSocket to terminal
  ws.on('message', (data) => {
    term.write(data);
  });

  // Handle data from terminal to WebSocket
  term.on('data', (data) => {
    ws.send(data);
  });

  // Handle WebSocket close
  ws.on('close', () => {
    term.kill();
    delete terminals[terminalID];
  });
});

// WebSocket endpoint for command execution
app.ws('/execute', (ws, req) => {
  const { command, commandArgs } = req.query;

  // Create child process
  const term = pty.spawn(command, commandArgs || [], {
    name: 'xterm-color',
    cols: 80,
    rows: 24,
    cwd: process.env.HOME,
    env: process.env,
  });

  // Forward process stdout to WebSocket
  term.on('data', (data) => {
    ws.send(data);
  });

  // Handle data from WebSocket to process stdin
  ws.on('message', (data) => {
    term.write(data);
  });

  // Handle WebSocket close
  ws.on('close', () => {
    term.kill();
  });
});

// Resize endpoint
app.ws('/resize/:terminalID', (ws, req) => {
  const terminalID = req.params.terminalID;
  const term = terminals[terminalID];

  if (term) {
    const { rows, cols } = req.query;
    term.resize(Number(cols), Number(rows));
  }
});

// Serve static files or your frontend

const PORT = options.port;
app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}`);
});
