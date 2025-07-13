# Red Hat Subscription Management MCP

MCP (ModelContextProtocol) Server for Red Hat Subscription Management

Getting started with Red Hat APIs: https://access.redhat.com/articles/3626371

## Running with Podman or Docker

You can run the rhsm-mcp server in a container using Podman or Docker. Make sure you have a valid Offline token, which you can obtain by logging into https://access.redhat.com/management/api:

Example configuration for running with Podman:

```json
{
  "mcpServers": {
    "rhsm": {
      "command": "podman",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "ACCESS_TOKEN_URL",
        "-e", "ACCESS_TOKEN_CLIENT_ID",
        "-e", "OFFLINE_TOKEN",
        "-e", "MCP_TRANSPORT",
        "quay.io/redhat-ai-tools/rhsm-mcp"
      ],
      "env": {
        "ACCESS_TOKEN_URL": "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token",
        "ACCESS_TOKEN_CLIENT_ID": "rhsm-api",
        "OFFLINE_TOKEN": "REDACTED",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

## Running with non-stdio transport

To run the server with a non-stdio transport (such as SSE), set the `MCP_TRANSPORT` environment variable to a value other than `stdio` (e.g., `sse`).

Example configuration to connect to a non-stdio MCP server:

```json
{
  "mcpServers": {
    "rhsm": {
      "url": "https://rhsm-mcp.example.com/sse",
      "headers": {
        "Offline-Token": "REDACTED"
      }
    }
  }
}
```

Replace `REDACTED` with the value from https://console.redhat.com/openshift/token.
