from django.conf import settings

from .models import Token

from datetime import timedelta, datetime, timezone
import jwt, uuid

ALGORITHM = "HS256"


def create_token(scope: dict, aud: str, ttl=timedelta(hours=12)):

    now = datetime.now(timezone.utc)
    payload = {
        "aud": aud,
        "iat": now,
        "exp": now + ttl,
        "jti": str(uuid.uuid4()),
        "scope": dict,
    }

    jwt = jwt.encode(payload, settings.CUSTOM_JWT_KEY, algorithm=ALGORITHM)

    token = Token.objects.create(
        token=jwt,
    )
