import asyncio
import uuid
from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.core.auth import current_active_user
from app.core.database import AsyncSessionLocal, Base, engine
from app.models.document import Conversation, Message
from app.models.user import User
from app.api.routes import conversations as conversations_routes


TEST_USER_ID = uuid.uuid4()


async def _reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def _seed_user():
    async with AsyncSessionLocal() as db:
        user = User(
            id=TEST_USER_ID,
            email="tester@example.com",
            hashed_password="",
            is_active=True,
            is_superuser=False,
            is_verified=True,
        )
        db.add(user)
        await db.commit()


async def _seed_conversation(title: str = "Project Notes"):
    conv_id = uuid.uuid4()
    async with AsyncSessionLocal() as db:
        conv = Conversation(
            id=conv_id,
            user_id=TEST_USER_ID,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(conv)
        db.add(
            Message(
                conversation_id=conv_id,
                role="user",
                content="What is in this conversation?",
                sources=[],
            )
        )
        await db.commit()
    return conv_id


def _override_user():
    return User(
        id=TEST_USER_ID,
        email="tester@example.com",
        hashed_password="",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )


def test_conversations_list_search_export_share_and_send_message(monkeypatch):
    asyncio.run(_reset_db())
    asyncio.run(_seed_user())
    conv_id = asyncio.run(_seed_conversation())

    async def fake_rag_query(question, document_ids=None, conversation_history=None, user_id=None):
        return {
            "answer": f"Echo: {question}",
            "sources": [
                {
                    "document_id": "doc-1",
                    "filename": "spec.pdf",
                    "page": 4,
                    "chunk_text": "Relevant snippet",
                    "relevance_score": 0.88,
                }
            ],
            "context_used": "mock-context",
        }

    monkeypatch.setattr(conversations_routes.rag_service, "query", fake_rag_query)
    app.dependency_overrides[current_active_user] = _override_user

    with TestClient(app) as client:
        list_resp = client.get("/api/v1/conversations")
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1

        search_resp = client.get("/api/v1/conversations", params={"q": "Project"})
        assert search_resp.status_code == 200
        assert len(search_resp.json()) == 1

        send_resp = client.post(
            f"/api/v1/conversations/{conv_id}/messages",
            json={"question": "Give summary", "document_ids": []},
        )
        assert send_resp.status_code == 200
        send_data = send_resp.json()
        assert send_data["answer"] == "Echo: Give summary"
        assert send_data["conversation_id"] == str(conv_id)

        export_resp = client.get(f"/api/v1/conversations/{conv_id}/export", params={"format": "md"})
        assert export_resp.status_code == 200
        assert "text/plain" in export_resp.headers["content-type"]
        assert "Project Notes" in export_resp.text

        share_resp = client.post(f"/api/v1/conversations/{conv_id}/share")
        assert share_resp.status_code == 200
        token = share_resp.json()["share_token"]
        assert token

        shared_resp = client.get(f"/api/v1/conversations/shared/{token}")
        assert shared_resp.status_code == 200
        shared_data = shared_resp.json()
        assert str(shared_data["id"]) == str(conv_id)
        assert len(shared_data["messages"]) >= 1

    app.dependency_overrides.clear()
