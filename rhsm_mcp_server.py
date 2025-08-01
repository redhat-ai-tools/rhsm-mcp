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
async def account_management_create_user(
    account_id: str,
    user_email: str,
    user_first_name: str,
    user_last_name: str,
    username: str | None = None,
):
    """Create User under the account from Red Hat Subscription Management - Account management"""
    url = f"{RHSM_API_BASE}/account/v1/accounts/{account_id}/users"
    username = username or user_email.split("@")[0]
    data = {
        "address": {
            "city": "RALEIGH",
            "country": "US",
            "streets": ["100 E. Davie Street"],
            "state": "NC",
            "county": "WAKE",
            "zipCode": "27601",
        },
        "email": user_email,
        "firstName": user_first_name,
        "lastName": user_last_name,
        "roles": [],
        "permissions": [
            "portal_manage_cases",
            "portal_system_management",
            "portal_download",
            "portal_manage_subscriptions",
        ],
        "phone": "18887334281",
        "username": username or user_email.split("@")[0],
    }
    response = await make_request(url, method="POST", data=data)
    return response


@mcp.tool()
async def account_management_invite_user(account_id: str, user_emails: list[str]):
    """Invite Users under the account from Red Hat Subscription Management - Account management"""
    url = f"{RHSM_API_BASE}/account/v1/accounts/{account_id}/users"
    data = {
        "emails": [user_emails],
        "localeCode": "en_US",
        "roles": [],
        "permissions": [
            "portal_manage_cases",
            "portal_system_management",
            "portal_download",
            "portal_manage_subscriptions",
        ],
    }
    response = await make_request(url, method="POST", data=data)
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
async def account_management_grant_user_admin(account_id: str, user_id: str):
    """Assign Organization Administrator Role To User under the account from Red Hat Subscription Management - Account management"""
    url = f"{RHSM_API_BASE}/account/v1/accounts/{account_id}/users/{user_id}/roles"
    data = {"role": "organization_administrator"}
    response = await make_request(url, method="POST", data=data)
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
