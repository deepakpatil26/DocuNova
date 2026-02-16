from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.routes.conversations import _build_share_token, _parse_share_token


def test_share_token_roundtrip():
    conversation_id = uuid4()
    owner_id = uuid4()

    token = _build_share_token(conversation_id, owner_id)
    parsed_conversation_id, parsed_owner_id = _parse_share_token(token)

    assert parsed_conversation_id == conversation_id
    assert parsed_owner_id == owner_id


def test_share_token_tamper_raises():
    conversation_id = uuid4()
    owner_id = uuid4()
    token = _build_share_token(conversation_id, owner_id)
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")

    with pytest.raises(HTTPException) as exc_info:
        _parse_share_token(tampered)

    assert exc_info.value.status_code == 400
