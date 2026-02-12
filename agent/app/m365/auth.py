import os
import json
from pathlib import Path
import msal

SCOPES = ["User.Read", "Mail.Send", "Mail.Read"]

class TokenStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text(encoding="utf-8"))
        return {}

    def save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data), encoding="utf-8")


class M365Auth:
    def __init__(self):
        self.client_id = os.getenv("M365_CLIENT_ID", "")
        if not self.client_id:
            raise RuntimeError("M365_CLIENT_ID env var is missing")

        tenant = os.getenv("M365_TENANT_ID", "common")
        self.authority = f"https://login.microsoftonline.com/{tenant}"

        store_path = os.getenv("TOKEN_CACHE_PATH", "./data/token_cache.json")
        self.store = TokenStore(store_path)

        self.cache = msal.SerializableTokenCache()
        self.cache.deserialize(json.dumps(self.store.load() or {}))

        self.app = msal.PublicClientApplication(
            client_id=self.client_id,
            authority=self.authority,
            token_cache=self.cache,
        )

    def _persist(self):
        if self.cache.has_state_changed:
            self.store.save(json.loads(self.cache.serialize()))

    def acquire_token_silent(self):
        accts = self.app.get_accounts()
        if not accts:
            return None
        token = self.app.acquire_token_silent(SCOPES, account=accts[0])
        self._persist()
        return token

    def start_device_flow(self):
        flow = self.app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise RuntimeError(f"Device flow init failed: {flow}")
        # Persist cache state even though this may not change it yet
        self._persist()
        return flow

    def complete_device_flow(self, flow: dict):
        token = self.app.acquire_token_by_device_flow(flow)
        self._persist()
        return token
