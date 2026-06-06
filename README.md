# bw_wtt (WS To TCP)

A [BotWave](https://github.com/dpipstudio/botwave) plugin that bridges the remote command WebSocket port to a local TCP socket, allowing lower-level tools and scripts to send BotWave commands without needing a WebSocket client.

## What it does

BotWave exposes a WebSocket interface for remote management (`--rc <port>`). WTT sits in the middle: it opens a TCP server on a port you choose, and whenever something connects to it, it forwards the data back and forth to BotWave's WebSocket port.

This is useful when your automation tooling (bash scripts, netcat, socat, serial bridges, etc.) speaks raw TCP but needs to talk to BotWave's remote command interface.

## Requirements

- BotWave installed at `/opt/BotWave`
- BotWave started with `--rc <port>` (sets `REMOTE_CMD_PORT`)
- Python >= 3.9
- `websockets` and `dlogger` Python packages (available in BotWave's venv)

## Installation

Run as root from the repo root:

```bash
sudo bash install.sh
```

The installer will:
- Copy scripts to `/opt/BotWave/scripts/wtt/`
- Copy handlers to `/opt/BotWave/handlers/`
- Ask if you want WTT to auto-start when BotWave is ready

## Usage

### From the BotWave shell

```
botwave> wtt       # starts the bridge on the default port (9940)
botwave> wtt 9950  # starts the bridge on a custom port
botwave> wtt-stop  # stops the bridge
```

### From the command line (manual)

```bash
python3 /opt/BotWave/scripts/wtt/main.py <TCP_PORT> <REMOTE_CMD_PORT> [ADD_NEWLINE]
```

| Argument | Description |
|---|---|
| `TCP_PORT` | Port WTT will listen on for incoming TCP connections |
| `REMOTE_CMD_PORT` | BotWave's `--rc` port (set automatically via `REMOTE_CMD_PORT` env var when using the BotWave shell) |
| `ADD_NEWLINE` | Optional. `true` to append `\n` to every message forwarded to TCP. Default: `false` |

### Connecting to WTT

Once running, any TCP client can connect and send BotWave commands:

```bash
# with netcat
nc localhost 9940

# with socat
socat - TCP:localhost:9940
```

Commands sent are the same as what you'd type in the BotWave shell (e.g. `start ss.wav 88`, `stop`, `help`).

## Configuration

| Environment variable | Description |
|---|---|
| `REMOTE_CMD_PORT` | BotWave's remote command port. **Required.** Set automatically by BotWave when using the `wtt` handler. |
| `WTT_PORT` | TCP port to listen on. Falls back to the first argument, then defaults to `9940`. |
| `WTT_NEWLINE` | Set to `true` to enable newline appending. |

## Auto-start

During installation, you can opt in to auto-start. If enabled, WTT will start automatically whenever BotWave is ready (both local client and server modes).

You can also add or remove this manually by creating/deleting these handler files in `/opt/BotWave/handlers/`:

- `l_onready_wtt_start.shdl`
- `s_onready_wtt_start.shdl`

Their sole content is `wtt`

WTT also registers `onexit` handlers for both modes, so it always stops cleanly when BotWave shuts down.

## Stopping

From the BotWave shell:
```
botwave> wtt-stop
```

Or directly:
```bash
bash /opt/BotWave/scripts/wtt/stop.sh
```

The stop script signals the bridge via `/tmp/killwtt` and the process shuts down gracefully.

## License

Licensed under [GPLv3.0](LICENSE)