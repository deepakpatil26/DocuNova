import logging
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from .database import AsyncSessionLocal, get_db
from .firebase_admin import _initialize_firebase
from .firebase_admin import auth as firebase_auth
from .config import settings

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


def _verify_firebase_token(id_token: str) -> Dict[str, Any]:
    if not _initialize_firebase():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firebase Admin is not configured on backend.",
        )

    try:
        return firebase_auth.verify_id_token(id_token)
    except Exception as exc:
        logger.warning("Invalid Firebase token: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase token.",
        ) from exc


async def _get_or_create_user_from_claims(db: AsyncSession, claims: Dict[str, Any]) -> User:
    email = claims.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token does not contain an email.",
        )

    result = await db.execute(select(User).filter(User.email == email))
    user = result.unique().scalar_one_or_none()

    email_verified = bool(claims.get("email_verified", False))
    if user is None:
        is_admin = email.lower() in settings.admin_emails
        user = User(
            email=email,
            hashed_password="",
            is_active=True,
            is_superuser=is_admin,
            is_verified=email_verified,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    updated = False
    if not user.is_active:
        user.is_active = True
        updated = True
    if email_verified and not user.is_verified:
        user.is_verified = True
        updated = True

    if updated:
        await db.commit()
        await db.refresh(user)

    return user


async def current_active_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )

    claims = _verify_firebase_token(credentials.credentials)
    return await _get_or_create_user_from_claims(db, claims)


async def current_token_claims(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Dict[str, Any]:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )
    return _verify_firebase_token(credentials.credentials)


async def seed_admin():
    """
    No-op for Firebase-primary auth.
    Admin elevation should be done by updating user flags in DB or via a future admin policy route.
    """
    async with AsyncSessionLocal():
        return
