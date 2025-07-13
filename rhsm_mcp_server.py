import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("rhsm")

RHSM_API_BASE = os.environ.get("RHSM_API_BASE", "https://api.access.redhat.com")
MCP_TRANSPORT = os.environ.get("MCP_TRANSPORT", "stdio")


async def get_access_token(client: httpx.AsyncClient) -> str:
    access_token_url = os.environ.get(
        "ACCESS_TOKEN_URL",
        "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token",
    )
    client_id = os.environ.get("ACCESS_TOKEN_CLIENT_ID", "rhsm-api")
    offline_token = (
        os.environ["OFFLINE_TOKEN"]
        if MCP_TRANSPORT == "stdio"
        else mcp.get_context().request_context.request.headers["Offline-Token"]
    )
    data = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "refresh_token": offline_token,
    }
    response = await client.post(access_token_url, data=data, timeout=30.0)
    response.raise_for_status()
    return response.json()["access_token"]


async def make_request(
    url: str, method: str = "GET", data: dict[str, Any] = None
) -> dict[str, Any] | None:
    async with httpx.AsyncClient() as client:
        token = await get_access_token(client)
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        if method.upper() == "GET":
            response = await client.request(method, url, headers=headers, params=data)
        else:
            response = await client.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def account_management_list_accounts():
    """List Account Information from Red Hat Subscription Management - Account management"""
    url = f"{RHSM_API_BASE}/account/v1/accounts"
    response = await make_request(url)
    return response


@mcp.tool()
async def account_management_list_users(account_id: str):
    """List all the users under the account from Red Hat Subscription Management - Account management"""
    url = f"{RHSM_API_BASE}/account/v1/accounts/{account_id}/users"
    response = await make_request(url)
    return response


@mcp.tool()
async def account_management_get_user(account_id: str, user_id: str):
    """Get User Details under the account from Red Hat Subscription Management - Account management"""
    url = f"{RHSM_API_BASE}/account/v1/accounts/{account_id}/users/{user_id}"
    response = await make_request(url)
    return response


@mcp.tool()
async def account_management_get_user_roles(account_id: str, user_id: str):
    """Get Roles Associated under the account from Red Hat Subscription Management - Account management"""
    url = f"{RHSM_API_BASE}/account/v1/accounts/{account_id}/users/{user_id}/roles"
    response = await make_request(url)
    return response


@mcp.tool()
async def account_management_get_user_status(account_id: str, user_id: str):
    """Get User Status under the account from Red Hat Subscription Management - Account management"""
    url = f"{RHSM_API_BASE}/account/v1/accounts/{account_id}/users/{user_id}/status"
    response = await make_request(url)
    return response


@mcp.tool()
async def account_management_whoami():
    """Get Current User's Personal Information from Red Hat Subscription Management - Account management"""
    url = f"{RHSM_API_BASE}/account/v1/user"
    response = await make_request(url)
    return response


@mcp.tool()
async def subscription_management_list_systems():
    """List all systems for a user from Red Hat Subscription Management - Subscription Management"""
    url = f"{RHSM_API_BASE}/management/systems"
    response = await make_request(url)
    return response


if __name__ == "__main__":
    mcp.run(transport=os.environ.get("MCP_TRANSPORT", "stdio"))
