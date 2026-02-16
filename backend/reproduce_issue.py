import asyncio
import sys
import os

# Add backend directory to sys.path
sys.path.append(os.getcwd())

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.document import Conversation
from sqlalchemy import select

async def main():
    print("Starting reproduction script...")
    async with AsyncSessionLocal() as session:
        print("Session created.")
        
        print("--- Testing User Query ---")
        try:
            result = await session.execute(select(User))
            users = result.scalars().all()
            print(f"Users found: {len(users)}")
            for u in users:
                print(f"User: {u.id} - {u.email}")
        except Exception as e:
            print(f"User Query Failed: {e}")
            import traceback
            traceback.print_exc()

        print("\n--- Testing Conversation Query ---")
        try:
            result = await session.execute(select(Conversation))
            convs = result.scalars().all()
            print(f"Conversations found: {len(convs)}")
        except Exception as e:
            print(f"Conversation Query Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
