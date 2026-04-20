import asyncio  
import json  
import uuid  
import logging  
import os  
from typing import Optional, Dict, Any, Callable  
from datetime import datetime  
import websockets  
from websockets.client import WebSocketClientProtocol  
  
# Configure logging  
logging.basicConfig(level=logging.INFO)  
logger = logging.getLogger("openclaw-client")  
  
class OpenClawGatewayClient:  
    """Python WebSocket client for OpenClaw Gateway"""  
      
    PROTOCOL_VERSION = 3  
      
    def __init__(  
        self,  
        url: str = "ws://127.0.0.1:18789",  
        token: Optional[str] = None,  
        password: Optional[str] = None,  
        client_id: str = "gateway-client",  
        client_mode: str = "backend",  
        client_version: str = "1.0.0"  
    ):  
        self.url = url  
        self.token = token  
        self.password = password  
        self.client_id = client_id  
        self.client_mode = client_mode  
        self.client_version = client_version  
          
        self.ws: Optional[WebSocketClientProtocol] = None  
        self.pending_requests: Dict[str, asyncio.Future] = {}  
        self.connected = False  
        self.last_seq: Optional[int] = None  
        self.connect_nonce: Optional[str] = None  
          
        # Event handlers  
        self.on_chat_delta: Optional[Callable[[str, str], None]] = None  
        self.on_chat_final: Optional[Callable[[str, str], None]] = None  
        self.on_chat_error: Optional[Callable[[str, str], None]] = None  
        self.on_agent_event: Optional[Callable[[Dict[str, Any]], None]] = None  
        self.on_connected: Optional[Callable[[], None]] = None  
        self.on_disconnected: Optional[Callable[[str], None]] = None  
          
    async def connect(self):  
        """Connect to Gateway and perform handshake"""  
        try:  
            self.ws = await websockets.connect(  
                self.url,  
                max_size=25 * 1024 * 1024,  # 25MB max payload  
            )  
              
            # Start message handler  
            asyncio.create_task(self._message_handler())  
              
            # Wait for connect challenge  
            await asyncio.wait_for(self._wait_for_challenge(), timeout=5.0)  
              
            # Send connect request  
            await self._send_connect()  
              
            # Wait for hello-ok response  
            await asyncio.wait_for(self._wait_for_hello_ok(), timeout=5.0)  
              
            self.connected = True  
            logger.info("Connected to OpenClaw Gateway")  
            if self.on_connected:  
                self.on_connected()  
                  
        except Exception as e:  
            logger.error(f"Failed to connect: {e}")  
            if self.on_disconnected:  
                self.on_disconnected(str(e))  
            raise  
      
    async def disconnect(self):  
        """Disconnect from Gateway"""  
        self.connected = False  
        if self.ws:  
            await self.ws.close()  
            self.ws = None  
        logger.info("Disconnected from Gateway")  
        if self.on_disconnected:  
            self.on_disconnected("Client disconnect")  
      
    async def send_chat(  
        self,  
        session_key: str,  
        message: str,  
        thinking: Optional[str] = None,  
        deliver: bool = False,  
        timeout_ms: Optional[int] = None,  
        run_id: Optional[str] = None  
    ) -> str:  
        """Send a chat message to the agent"""  
        if not self.connected:  
            raise RuntimeError("Not connected to Gateway")  
          
        run_id = run_id or str(uuid.uuid4())  
          
        params = {  
            "sessionKey": session_key,  
            "message": message,  
            "deliver": deliver,  
            "idempotencyKey": run_id,  
        }  
          
        if thinking:  
            params["thinking"] = thinking  
        if timeout_ms:  
            params["timeoutMs"] = timeout_ms  
          
        response = await self._request("chat.send", params)  
        return response.get("runId", run_id)  
      
    async def _request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:  
        """Send a request and wait for response"""  
        if not self.ws:  
            raise RuntimeError("WebSocket not connected")  
          
        request_id = str(uuid.uuid4())  
        message = {  
            "type": "req",  
            "id": request_id,  
            "method": method,  
            "params": params  
        }  
          
        # Create future for response  
        future = asyncio.Future()  
        self.pending_requests[request_id] = future  
          
        try:  
            await self.ws.send(json.dumps(message))  
            response = await asyncio.wait_for(future, timeout=30.0)  
            return response  
        finally:  
            self.pending_requests.pop(request_id, None)  
      
    async def _send_connect(self):  
        """Send connect request"""  
        params = {  
            "minProtocol": self.PROTOCOL_VERSION,  
            "maxProtocol": self.PROTOCOL_VERSION,  
            "client": {  
                "id": self.client_id,  
                "displayName": "Python Client",  
                "version": self.client_version,  
                "platform": "python",  
                "mode": self.client_mode,  
                "instanceId": str(uuid.uuid4()),  
            },  
            "role": "operator",  
            "scopes": ["operator.read", "operator.write"],  
            "caps": [],  
            "commands": [],  
            "permissions": {},  
            "locale": "en-US",  
            "userAgent": f"openclaw-python/{self.client_version}"  
        }  
          
        # Add authentication if provided  
        if self.token or self.password:  
            auth = {}  
            if self.token:  
                auth["token"] = self.token  
            if self.password:  
                auth["password"] = self.password  
            params["auth"] = auth  
          
        connect_message = {  
            "type": "req",  
            "id": str(uuid.uuid4()),  
            "method": "connect",  
            "params": params  
        }  
          
        await self.ws.send(json.dumps(connect_message))  
      
    async def _wait_for_challenge(self):  
        """Wait for connect.challenge event"""  
        future = asyncio.Future()  
        self._challenge_future = future  
        await future  
      
    async def _wait_for_hello_ok(self):  
        """Wait for hello-ok response"""  
        future = asyncio.Future()  
        self._hello_ok_future = future  
        await future  
      
    async def _message_handler(self):  
        """Handle incoming WebSocket messages"""  
        if not self.ws:  
            return  
          
        try:  
            async for message in self.ws:  
                try:  
                    data = json.loads(message)  
                    await self._handle_message(data)  
                except json.JSONDecodeError as e:  
                    logger.error(f"Failed to parse message: {e}")  
        except websockets.exceptions.ConnectionClosed:  
            self.connected = False  
            logger.info("Connection closed")  
            if self.on_disconnected:  
                self.on_disconnected("Connection closed")  
        except Exception as e:  
            logger.error(f"Message handler error: {e}")  
      
    async def _handle_message(self, data: Dict[str, Any]):  
        """Handle a single message"""  
        msg_type = data.get("type")  
          
        if msg_type == "event":  
            await self._handle_event(data)  
        elif msg_type == "res":  
            await self._handle_response(data)  
        else:  
            logger.warning(f"Unknown message type: {msg_type}")  
      
    async def _handle_event(self, event: Dict[str, Any]):  
        """Handle event message"""  
        event_name = event.get("event")  
        payload = event.get("payload", {})  
        seq = event.get("seq")  
          
        # Track sequence numbers  
        if seq is not None:  
            if self.last_seq is not None and seq > self.last_seq + 1:  
                logger.warning(f"Sequence gap: expected {self.last_seq + 1}, got {seq}")  
            self.last_seq = seq  
          
        if event_name == "connect.challenge":  
            nonce = payload.get("nonce")  
            if nonce:  
                self.connect_nonce = nonce  
                if hasattr(self, '_challenge_future'):  
                    self._challenge_future.set_result(True)  
          
        elif event_name == "chat":  
            await self._handle_chat_event(payload)  
          
        elif event_name == "agent":  
            if self.on_agent_event:  
                self.on_agent_event(payload)  
          
        elif event_name == "tick":  
            # Tick events for connection health  
            pass  
          
        elif event_name == "shutdown":  
            logger.warning(f"Gateway shutting down: {payload.get('reason')}")  
            await self.disconnect()  
      
    async def _handle_chat_event(self, payload: Dict[str, Any]):  
        """Handle chat event"""  
        run_id = payload.get("runId")  
        session_key = payload.get("sessionKey")  
        state = payload.get("state")  
        message = payload.get("message")  
        error_message = payload.get("errorMessage")  
          
        if state == "delta":  
            # Streaming response  
            if message and isinstance(message, dict):  
                content = message.get("content", [])  
                if content and isinstance(content, list):  
                    text = content[0].get("text", "")  
                    if self.on_chat_delta:  
                        self.on_chat_delta(run_id, text)  
          
        elif state == "final":  
            # Final response  
            if message and isinstance(message, dict):  
                content = message.get("content", [])  
                if content and isinstance(content, list):  
                    text = content[0].get("text", "")  
                    if self.on_chat_final:  
                        self.on_chat_final(run_id, text)  
          
        elif state == "error":  
            if self.on_chat_error:  
                self.on_chat_error(run_id, error_message or "Unknown error")  
          
        elif state == "aborted":  
            logger.info(f"Chat run {run_id} aborted")  
      
    async def _handle_response(self, response: Dict[str, Any]):  
        """Handle response message"""  
        response_id = response.get("id")  
        ok = response.get("ok", False)  
        payload = response.get("payload")  
        error = response.get("error")  
          
        # Check if this is hello-ok response  
        if payload and isinstance(payload, dict) and payload.get("type") == "hello-ok":  
            if hasattr(self, '_hello_ok_future'):  
                self._hello_ok_future.set_result(payload)  
            return  
          
        # Handle pending request  
        if response_id in self.pending_requests:  
            future = self.pending_requests[response_id]  
            if ok:  
                future.set_result(payload or {})  
            else:  
                error_msg = error.get("message", "Unknown error") if error else "Request failed"  
                future.set_exception(Exception(error_msg))  
  
  
# Example usage  
def _resolve_token() -> str:  
    token = os.environ.get("OPENCLAW_GATEWAY_TOKEN") or os.environ.get("CLAWDBOT_GATEWAY_TOKEN")  
    if not token:  
        raise SystemExit("Set OPENCLAW_GATEWAY_TOKEN (or pass token into OpenClawGatewayClient).")  
    return token  
  
  
def _default_session_key(agent_id: str = "main") -> str:  
    return f"agent:{agent_id}:main"  
  
  
async def main():  
    client = OpenClawGatewayClient(  
        url="ws://127.0.0.1:18789",  
        token=_resolve_token(),  
    )  
      
    # Set up event handlers  
    full_response = ""  
      
    def on_delta(run_id: str, text: str):  
        nonlocal full_response  
        full_response += text  
        print(f"\r[Streaming] {text}", end="", flush=True)  
      
    def on_final(run_id: str, text: str):  
        print(f"\n\n[Complete] Run ID: {run_id}")  
        print(f"Response: {text}")  
      
    def on_error(run_id: str, error: str):  
        print(f"\n[Error] Run ID: {run_id}, Error: {error}")  
      
    client.on_chat_delta = on_delta  
    client.on_chat_final = on_final  
    client.on_chat_error = on_error  
      
    try:  
        # Connect to Gateway  
        await client.connect()  
          
        # Send a chat message  
        session_key = _default_session_key()  
        message = "Hello, can you help me write a Python function?"  
          
        print(f"Sending message: {message}")  
        run_id = await client.send_chat(session_key, message)  
        print(f"Message sent, Run ID: {run_id}")  
          
        # Wait for response  
        await asyncio.sleep(10)  
          
    except Exception as e:  
        logger.error(f"Error: {e}")  
    finally:  
        await client.disconnect()  
  
  
if __name__ == "__main__":  
    asyncio.run(main())
