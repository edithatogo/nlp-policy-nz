"""MCP adapter surface for :mod:`nlp_policy_nz`."""

from __future__ import annotations

from nlp_policy_nz.mcp.server import (
    MCPDependencyError,
    MCP_SERVER_NAME,
    MCP_SERVER_VERSION,
    build_fastmcp_server,
    build_mcp_manifest,
    call_tool,
    main,
    read_resource,
)

__all__ = [
    "MCPDependencyError",
    "MCP_SERVER_NAME",
    "MCP_SERVER_VERSION",
    "build_fastmcp_server",
    "build_mcp_manifest",
    "call_tool",
    "main",
    "read_resource",
]
