import pytest
from app.services.llm_router import route_request

@pytest.mark.asyncio
async def test_router():

    response = await route_request(
        "hello"
    )

    assert response is not None