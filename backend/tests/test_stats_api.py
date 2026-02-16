import asyncio
import uuid
from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.core.auth import current_active_user
from app.core.database import AsyncSessionLocal, Base, engine
from app.models.document import Conversation, Document, Message
from app.models.user import User


TEST_USER_ID = uuid.uuid4()


async def _reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _seed_data():
    async with AsyncSessionLocal() as db:
        user = User(
            id=TEST_USER_ID,
            email="stats@example.com",
            hashed_password="",
            is_active=True,
            is_superuser=False,
            is_verified=True,
        )
        db.add(user)

        doc = Document(
            id=uuid.uuid4(),
            user_id=TEST_USER_ID,
            filename="a.txt",
            original_filename="a.txt",
            file_size=100,
            file_type=".txt",
            processing_status="completed",
            chunk_count=1,
        )
        conv = Conversation(
            id=uuid.uuid4(),
            user_id=TEST_USER_ID,
            title="Stats Conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(doc)
        db.add(conv)
        db.add(Message(conversation_id=conv.id, role="user", content="hello"))
        db.add(Message(conversation_id=conv.id, role="assistant", content="hi"))
        await db.commit()


def _override_user():
    return User(
        id=TEST_USER_ID,
        email="stats@example.com",
        hashed_password="",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )


def test_stats_endpoint_counts_user_entities():
    asyncio.run(_reset_db())
    asyncio.run(_seed_data())

    app.dependency_overrides[current_active_user] = _override_user
    with TestClient(app) as client:
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["documents"] == 1
        assert data["conversations"] == 1
        assert data["messages"] == 2
    app.dependency_overrides.clear()
