"""
Bank API Tests
"""

import pytest
from httpx import AsyncClient


class TestBankRegistration:
    """Tests for bank registration endpoint."""
    
    @pytest.mark.asyncio
    async def test_register_bank_success(
        self, client: AsyncClient, sample_bank_data, sample_admin_data
    ):
        """Test successful bank registration."""
        response = await client.post(
            "/api/v1/banks/register",
            json={**sample_bank_data, **sample_admin_data}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["slug"] == "test-bank"
        assert data["status"] == "pending"
        assert "api_key" in data
    
    @pytest.mark.asyncio
    async def test_register_bank_duplicate_slug(
        self, client: AsyncClient, sample_bank_data, sample_admin_data
    ):
        """Test duplicate slug rejection."""
        # First registration
        await client.post(
            "/api/v1/banks/register",
            json={**sample_bank_data, **sample_admin_data}
        )
        
        # Second registration with same slug
        response = await client.post(
            "/api/v1/banks/register",
            json={**sample_bank_data, **sample_admin_data}
        )
        
        assert response.status_code == 409
    
    @pytest.mark.asyncio
    async def test_register_bank_invalid_country(
        self, client: AsyncClient, sample_bank_data, sample_admin_data
    ):
        """Test invalid country rejection."""
        sample_bank_data["country"] = "US"
        
        response = await client.post(
            "/api/v1/banks/register",
            json={**sample_bank_data, **sample_admin_data}
        )
        
        assert response.status_code == 422


class TestHealthCheck:
    """Tests for health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint."""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "GCC Wealth" in data["app"]
