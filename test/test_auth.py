import pytest

from src.auth import PresenceTokenVerifier


@pytest.fixture
def verifier():
    return PresenceTokenVerifier()


@pytest.mark.asyncio
async def test_valid_token(verifier):
    result = await verifier.verify_token("abc123")
    assert result is not None
    assert result.token == "abc123"
    assert result.client_id == "user"
    assert result.scopes == []


@pytest.mark.asyncio
async def test_empty_token(verifier):
    result = await verifier.verify_token("")
    assert result is None


@pytest.mark.asyncio
async def test_whitespace_token(verifier):
    result = await verifier.verify_token("   ")
    assert result is None
