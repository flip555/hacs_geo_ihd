"""API client for Geo Home IHD."""

import logging

_LOGGER = logging.getLogger(__name__)


class GeoHomeAPIClient:
    """Async HTTP client for the Geo Together API."""

    def __init__(self, username: str, password: str, base_url: str):
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip("/")
        self._session = None
        self._token = None

    async def _ensure_session(self):
        if self._session is None or self._session.closed:
            import aiohttp
            self._session = aiohttp.ClientSession()

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def _request(self, method: str, path: str, **kwargs):
        await self._ensure_session()
        url = f"{self.base_url}{path}"
        async with self._session.request(method, url, **kwargs) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _ensure_token(self):
        if self._token is None:
            self._token = await self.login()
        return self._token

    async def login(self) -> str:
        """Login and return an access token."""
        data = await self._request(
            "POST", "/usersservice/v2/login",
            json={"identity": self.username, "password": self.password},
            headers={"Content-Type": "application/json"},
        )
        return data["accessToken"]

    async def get_device_data(self) -> dict:
        """Get device/system data."""
        token = await self._ensure_token()
        return await self._request(
            "GET", "/api/userapi/v2/user/detail-systems?systemDetails=true",
            headers={"Authorization": f"Bearer {token}"},
        )

    async def get_periodic_meter_data(self, system_id: str) -> dict:
        """Get periodic meter data."""
        token = await self._ensure_token()
        return await self._request(
            "GET", f"/api/userapi/system/smets2-periodic-data/{system_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

    async def get_live_meter_data(self, system_id: str) -> dict:
        """Get live meter data."""
        token = await self._ensure_token()
        return await self._request(
            "GET", f"/api/userapi/system/smets2-live-data/{system_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
