from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict

from ...core.auth import current_active_user, current_token_claims
from ...core.config import settings
from ...models.user import User

router = APIRouter()


@router.get("/me")
async def get_current_user_profile(user: User = Depends(current_active_user)):
    return {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified,
    }


@router.get("/debug/token")
async def debug_token_claims(
    claims: Dict[str, Any] = Depends(current_token_claims),
    user: User = Depends(current_active_user),
):
    if not settings.DEBUG and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized for token debugging.")

    firebase_info = claims.get("firebase", {})
    return {
        "uid": claims.get("uid"),
        "email": claims.get("email"),
        "email_verified": claims.get("email_verified"),
        "provider": firebase_info.get("sign_in_provider"),
        "issued_at": claims.get("iat"),
        "expires_at": claims.get("exp"),
        "auth_time": claims.get("auth_time"),
    }
