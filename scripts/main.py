# A bridge between BotWave WebSocket and a TCP socket
# https://git.douxx.tech/bw_wtt
# 
# Usage:
# Inside a BotWave local client / server:
# wtt <tcp port (default 9940)>
# In command line:
# python3 wtt.py <WTT_PORT> <REMOTE_CMD> [ADD_NEWLINE(true/*)]

import asyncio
from dlogger import DLogger
import os
import sys
import websockets

if len(sys.argv) < 3:
    print("Usage: python main.py <WTT_PORT> <REMOTE_CMD_PORT> [ADD_NEWLINE(true/false)]")
    sys.exit(1)

try:
    TCP_PORT = int(sys.argv[1])
    WS_PORT = int(sys.argv[2])
except ValueError:
    print(f"Error: Arguments must be valid port numbers")
    sys.exit(1)

ADD_NEWLINE = False
if len(sys.argv) >= 4:
    ADD_NEWLINE = sys.argv[3].lower() == 'true'

Log = DLogger(
    icons={
        'info': 'WTT',
        'error': 'WTT_ERR',
        'warning': 'WTT_WARN',
    },
    styles={
        'info': 'bright_cyan',
        'error': 'bright_red',
        'warning': 'bright_yellow',
    },
    save=True,
    single_file=True,
    save_to="/opt/BotWave/scripts/wtt/logs.txt",
    show_time=True
)

KILLFILE = '/tmp/killwtt'
shutdown_event = asyncio.Event()
 
class BridgeConnection:
    def __init__(self, tcp_reader, tcp_writer):
        self.tcp_reader = tcp_reader
        self.tcp_writer = tcp_writer
        self.ws = None
        self.active = False
    
    async def connect_to_ws(self):
        try:
            self.ws = await websockets.connect(f"ws://localhost:{WS_PORT}")
            self.active = True
            Log.info(f"Connected to WS server at localhost:{WS_PORT}")
            return True
        except Exception as e:
            Log.error(f"Failed to connect to WS server: {e}")
            return False
    
    async def ws_to_tcp(self):
        """Forward WebSocket messages to TCP"""
        try:
            async for message in self.ws:
                if not self.active:
                    break
                
                if isinstance(message, bytes):
                    data = message
                else:
                    data = message.encode()
                
                if ADD_NEWLINE:
                    data += b'\n'
                
                self.tcp_writer.write(data)
                await self.tcp_writer.drain()
        
        except websockets.exceptions.ConnectionClosed:
            Log.info("WS connection closed by server")
        except Exception as e:
            Log.error(f"WS->TCP error: {e}")
        finally:
            self.active = False
    
    async def tcp_to_ws(self):
        """Forward TCP data to WebSocket"""
        try:
            while self.active:
                data = await self.tcp_reader.read(4096)
                if not data:
                    Log.info("TCP connection closed by client")
                    break
                
                # dcd bytes to string for WebSocket
                try:
                    message = data.decode('utf-8')
                except UnicodeDecodeError:
                    Log.warning("Failed to decode TCP data as UTF-8, skipping")
                    continue
                
                if not self.active or not self.ws or self.ws.closed:
                    break

                await self.ws.send(message)
        
        except websockets.exceptions.ConnectionClosed:
            Log.info("TCP->WS: WS connection was already closed")
        except asyncio.IncompleteReadError:
            Log.info("TCP connection closed")
        except Exception as e:
            # Catching generic websocket closed errors without spamming error logs
            if "received 1000" in str(e) or "sent 1000" in str(e):
                Log.info("WS connection closed gracefully")
            else:
                Log.error(f"TCP->WS error: {e}")
        finally:
            self.active = False
    
    async def bridge(self):
        """Run bidirectional bridge"""
        if not await self.connect_to_ws():
            await self.cleanup()
            return
        
        ws_task = asyncio.create_task(self.ws_to_tcp())
        tcp_task = asyncio.create_task(self.tcp_to_ws())
        
        done, pending = await asyncio.wait(
            [ws_task, tcp_task], 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # sdwn the remaining active side
        self.active = False
        for task in pending:
            task.cancel()
            
        await self.cleanup()
    
    async def cleanup(self):
        """Clean up connections gracefully"""
        self.active = False
        
        if self.ws:
            try:
                await self.ws.close()
            except Exception:
                pass
        
        if self.tcp_writer:
            try:
                self.tcp_writer.close()
                await self.tcp_writer.wait_closed()
            except Exception:
                pass
        
        Log.info("Bridge closed")
 
 
async def handle_tcp_client(reader, writer):
    """Handle incoming TCP connection"""
    addr = writer.get_extra_info('peername')
    Log.info(f"TCP client connected from {addr}")
    
    bridge = BridgeConnection(reader, writer)
    await bridge.bridge()
    
    Log.info(f"TCP client disconnected from {addr}")
 
 
async def start_tcp_server():
    """Start TCP server"""
    server = await asyncio.start_server(handle_tcp_client, '0.0.0.0', TCP_PORT)
    Log.info(f"TCP server listening on 0.0.0.0:{TCP_PORT}")
    async with server:
        await shutdown_event.wait()
 
 
async def watch_killfile():
    """Watch for /tmp/killwtt and shut down if it appears"""
    while not shutdown_event.is_set():
        if os.path.exists(KILLFILE):
            Log.info(f"Found {KILLFILE}, shutting down")
            try:
                os.remove(KILLFILE)
            except:
                pass
            shutdown_event.set()
            break
        await asyncio.sleep(1)
 
 
async def main():
    """Start TCP server and killfile watcher"""
    try:
        await asyncio.gather(start_tcp_server(), watch_killfile())
    except KeyboardInterrupt:
        Log.info("Shutting down (Ctrl+C)...")
        shutdown_event.set()
    except Exception as e:
        Log.error(f"Fatal error: {e}")
        raise
    finally:
        try:
            if os.path.exists(KILLFILE):
                os.remove(KILLFILE)
        except:
            pass
        Log.info("Bridge stopped")
 
 
if __name__ == '__main__':
    asyncio.run(main())