import time
import struct
import hmac
import hashlib
import base64
import secrets
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class AgoraService:
    def __init__(self):
        self.app_id = settings.AGORA_APP_ID
        self.app_certificate = settings.AGORA_APP_CERTIFICATE

    def _generate_rtc_token(self, channel_name: str, uid: int = 0, role: int = 1, expire_seconds: int = 3600) -> str:
        if not self.app_id or not self.app_certificate:
            logger.warning("Agora credentials not configured, generating mock token")
            return secrets.token_urlsafe(32)

        token_expiration = int(time.time()) + expire_seconds
        privilege_expiration = token_expiration

        raw_uid = uid
        salt = secrets.randbits(32)

        content = bytearray()
        content.extend(struct.pack("<I", 0))  # service type: RTC
        content.extend(struct.pack("<I", salt))
        content.extend(struct.pack("<I", token_expiration))
        content.extend(struct.pack("<I", 3))  # privilege count: join + publish
        content.extend(struct.pack("<H", 1))  # privilege: join channel
        content.extend(struct.pack("<I", privilege_expiration))
        content.extend(struct.pack("<H", 2))  # privilege: publish audio/video
        content.extend(struct.pack("<I", privilege_expiration))

        version = struct.pack("<H", 1)
        signature = self._generate_signature(channel_name, raw_uid, salt, token_expiration)
        token_data = version + signature + content

        return base64.b64encode(token_data).decode("utf-8")

    def _generate_signature(self, channel_name: str, uid: int, salt: int, ts: int) -> bytes:
        # Agora SDK v3 requires HMAC-SHA256 with app_certificate as the key
        # message = salt(4) + ts(4) + uid(4) + channel_name
        msg = struct.pack("<III", salt, ts, uid) + channel_name.encode("utf-8")
        return hmac.new(self.app_certificate.encode("utf-8"), msg, hashlib.sha256).digest()

    def generate_token(self, channel_name: str, uid: int = 0, role: str = "publisher") -> dict:
        role_map = {"publisher": 1, "subscriber": 2}
        rtc_role = role_map.get(role, 1)
        token = self._generate_rtc_token(channel_name, uid, rtc_role)
        return {
            "token": token,
            "channel_name": channel_name,
            "uid": uid,
            "app_id": self.app_id,
            "expire_seconds": 3600,
        }

    def create_channel(self, subject: str, topic: str | None = None) -> dict:
        channel_name = f"cognora_{int(time.time())}_{secrets.token_hex(4)}"
        uid = secrets.randbelow(2 ** 31 - 1)
        return self.generate_token(channel_name, uid, "publisher")
