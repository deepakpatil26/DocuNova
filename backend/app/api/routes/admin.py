from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ...core.auth import current_active_user
from ...models.user import User
from ...schemas.user import UserRead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ...core.database import get_db

router = APIRouter()

@router.get("/users", response_model=List[UserRead])
async def list_all_users(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user)
):
    """List all registered users. Restricted to superusers (Owner)."""
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Not authorized. Admin access only.")
        
    result = await db.execute(select(User))
    users = result.scalars().all()
    return list(users)
