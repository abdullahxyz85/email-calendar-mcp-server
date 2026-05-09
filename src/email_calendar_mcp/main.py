"""Main MCP Server implementation"""

import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools.email_tools import EmailTools, get_email_tools_definitions
from .tools.calendar_tools import CalendarTools, get_calendar_tools_definitions
from .utils.config import settings
from .utils.logger import get_logger, setup_logging

# Setup logging
setup_logging()
logger = get_logger(__name__)


class EmailCalendarMCPServer:
    """Email & Calendar Manager MCP Server"""

    def __init__(self):
        """Initialize the MCP server"""
        self.server = Server("email-calendar-mcp")
        self.email_tools = EmailTools()
        self.calendar_tools = CalendarTools()

        # Register handlers
        self._register_handlers()
        logger.info("Email & Calendar MCP Server initialized")

    def _register_handlers(self) -> None:
        """Register MCP handlers"""
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools"""
            logger.info("Listing available tools")
            email_tools = get_email_tools_definitions()
            calendar_tools = get_calendar_tools_definitions()

            tools = []
            for tool_def in email_tools + calendar_tools:
                tools.append(
                    Tool(
                        name=tool_def["name"],
                        description=tool_def["description"],
                        inputSchema=tool_def["inputSchema"],
                    )
                )

            logger.debug("Tools listed", count=len(tools))
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Execute a tool call"""
            logger.info("Tool called", tool_name=name, arguments=arguments)

            try:
                result = await self._execute_tool(name, arguments)
                logger.debug("Tool executed successfully", tool_name=name)
                return [TextContent(type="text", text=str(result))]
            except Exception as e:
                logger.error("Tool execution failed", tool_name=name, error=str(e), exc_info=True)
                return [TextContent(type="text", text=f"Error executing tool: {str(e)}")]

    async def _execute_tool(self, name: str, arguments: dict) -> Any:
        """
        Execute a tool by name

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result
        """
        # Email tools
        if name == "fetch_emails":
            return self.email_tools.fetch_emails(**arguments)
        elif name == "send_email":
            return self.email_tools.send_email(**arguments)
        elif name == "search_emails":
            return self.email_tools.search_emails(**arguments)
        elif name == "mark_as_read":
            return self.email_tools.mark_as_read(**arguments)
        elif name == "delete_email":
            return self.email_tools.delete_email(**arguments)

        # Calendar tools
        elif name == "schedule_meeting":
            return self.calendar_tools.schedule_meeting(**arguments)
        elif name == "get_calendar_availability":
            return self.calendar_tools.get_calendar_availability(**arguments)
        elif name == "get_events":
            return self.calendar_tools.get_events(**arguments)
        elif name == "set_reminder":
            return self.calendar_tools.set_reminder(**arguments)
        elif name == "update_event":
            return self.calendar_tools.update_event(**arguments)
        elif name == "delete_event":
            return self.calendar_tools.delete_event(**arguments)

        else:
            raise ValueError(f"Unknown tool: {name}")

    async def run(self) -> None:
        """Run the MCP server"""
        logger.info("Starting Email & Calendar MCP Server")
        logger.info(
            "Server configuration",
            host=settings.server_host,
            port=settings.server_port,
            debug=settings.debug,
        )

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream, None)


async def main() -> None:
    """Main entry point"""
    try:
        logger.info("Initializing Email & Calendar MCP Server")
        server = EmailCalendarMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error("Server error", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    logger.info("Starting Email & Calendar MCP Server")
    asyncio.run(main())
