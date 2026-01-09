import sys
import asyncio
from contextlib import AsyncExitStack
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # Load environment variables


class MCPClientWorker(QObject):
    """Asynchronous task worker that runs the event loop in a separate thread."""
    response_ready = pyqtSignal(str)  # Signal when response is ready
    error_occurred = pyqtSignal(str)  # Signal for errors
    tools_listed = pyqtSignal(list)  # Signal for listed tools

    def __init__(self, server_script_path: str):
        super().__init__()
        self.server_script_path = server_script_path
        self.loop = asyncio.new_event_loop()
        self.session: Optional[ClientSession] = None
        self.anthropic = Anthropic()

    @pyqtSlot()
    def start_connection(self):
        """Start asynchronous connection (called in worker thread)."""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._connect_to_server())
        except Exception as e:
            self.error_occurred.emit(f"Connection error: {str(e)}")

    async def _connect_to_server(self):
        """Establish connection to the server."""
        is_python = self.server_script_path.endswith('.py')
        is_js = self.server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[self.server_script_path],
            env=None
        )

        async with AsyncExitStack() as exit_stack:
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            self.session = await exit_stack.enter_async_context(ClientSession(stdio, write))
            await self.session.initialize()

            # Get available tools and emit signal
            response = await self.session.list_tools()
            self.tools_listed.emit([tool.name for tool in response.tools])

    @pyqtSlot(str)
    def process_query(self, query: str):
        """Process user query (thread-safe entry point)."""
        future = asyncio.run_coroutine_threadsafe(
            self._process_query_async(query),
            self.loop
        )
        future.add_done_callback(self._handle_query_result)

    async def _process_query_async(self, query: str) -> str:
        """Core logic for asynchronously processing the query."""
        try:
            # Initial tool call to get alerts
            tool_name = "get_alerts"
            tool_args = {"state": "CA"}
            tool_result = await self.session.call_tool(tool_name, tool_args)

            # Create messages for the Claude API call
            messages = [{"role": "user", "content": query}]

            # Get available tools definition
            tools_response = await self.session.list_tools()
            available_tools = [{
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema
            } for t in tools_response.tools]

            # Call Claude API
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=messages,
                tools=available_tools
            )

            # Process the response and return the content
            return "\n".join(
                content.text for content in response.content
                if content.type == 'text'
            )
        except Exception as e:
            return f"Processing error: {str(e)}"

    def _handle_query_result(self, future):
        """Callback to handle the result of the query."""
        try:
            result = future.result()
            self.response_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("MCP Client")
        self.setGeometry(100, 100, 800, 600)

        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Connect button
        self.connect_btn = QPushButton("Connect to Server")
        self.connect_btn.setFixedHeight(40)

        # Status display area
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)

        # Assemble the interface
        layout.addWidget(self.connect_btn)
        layout.addWidget(self.status_display)
        central_widget.setLayout(layout)

    def connect_signals(self):
        """Connect signals and slots."""
        # Button click event
        self.connect_btn.clicked.connect(self.on_connect_clicked)

        # Worker thread signals
        self.worker.response_ready.connect(self.display_response)
        self.worker.error_occurred.connect(self.display_error)
        self.worker.tools_listed.connect(self.display_tools)

    def on_connect_clicked(self):
        """Handle connect button click."""
        self.status_display.append("Connecting to server...")
        self.connect_btn.setEnabled(False)  # Prevent multiple clicks

        # Create worker thread
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)

        # Clean up when thread finishes
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        # Start thread
        self.worker_thread.started.connect(self.worker.start_connection)
        self.worker_thread.start()

    def display_response(self, text):
        """Display API response."""
        self.status_display.append(f"Response: {text}")
        self.connect_btn.setEnabled(True)  # Restore button state

    def display_error(self, error):
        """Display error information."""
        self.status_display.append(f"Error: {error}")
        self.connect_btn.setEnabled(True)  # Restore button state

    def display_tools(self, tools):
        """Display available tools list."""
        self.status_display.append("Available Tools:")
        for tool in tools:
            self.status_display.append(f"- {tool}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Example: server path from configuration
    server_path = "server.py"

    # Create worker and main window
    worker = MCPClientWorker(server_path)
    window = MainWindow(worker)
    window.show()

    sys.exit(app.exec())
