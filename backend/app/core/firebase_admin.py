import json
import logging
from typing import Optional
from pathlib import Path

import firebase_admin
from firebase_admin import auth, credentials

from .config import settings

logger = logging.getLogger(__name__)


_initialized = False


def _initialize_firebase() -> bool:
    global _initialized
    if _initialized:
        return True

    if firebase_admin._apps:
        _initialized = True
        return True

    try:
        if settings.FIREBASE_CREDENTIALS_JSON:
            cred_dict = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
            cred = credentials.Certificate(cred_dict)
        elif settings.FIREBASE_CREDENTIALS_PATH:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        else:
            # Convenience fallback: detect service-account key in project root
            candidates = list(Path.cwd().glob("*firebase-adminsdk*.json"))
            if not candidates:
                candidates = list(Path.cwd().parent.glob("*firebase-adminsdk*.json"))
            if not candidates:
                logger.info("Firebase Admin is not configured. Skipping Firebase sync.")
                return False
            cred = credentials.Certificate(str(candidates[0]))
            logger.info("Using Firebase credentials from detected file: %s", candidates[0].name)

        firebase_admin.initialize_app(cred)
        _initialized = True
        logger.info("Firebase Admin initialized.")
        return True
    except Exception as exc:
        logger.exception("Failed to initialize Firebase Admin: %s", exc)
        return False


def ensure_firebase_user(email: str, uid: Optional[str] = None, email_verified: bool = False) -> bool:
    """
    Ensure a user exists in Firebase Authentication.
    Returns True when user exists/created, False when sync is unavailable or failed.
    """
    if not _initialize_firebase():
        return False

    try:
        auth.get_user_by_email(email)
        return True
    except auth.UserNotFoundError:
        try:
            create_kwargs = {
                "email": email,
                "email_verified": email_verified,
            }
            if uid:
                create_kwargs["uid"] = uid
            auth.create_user(**create_kwargs)
            logger.info("Created Firebase Auth user for %s", email)
            return True
        except Exception as exc:
            logger.exception("Failed to create Firebase user for %s: %s", email, exc)
            return False
    except Exception as exc:
        logger.exception("Failed Firebase lookup for %s: %s", email, exc)
        return False
