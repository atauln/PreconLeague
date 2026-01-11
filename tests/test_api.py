"""Unit tests for API app initialization and configuration"""
import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the api directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))


class TestBuildServersFromEnv:
    """Tests for _build_servers_from_env function"""
    
    def test_build_servers_with_http_url(self):
        """Test server configuration with HTTP URL"""
        import api.api as api_module
        _build_servers_from_env = api_module._build_servers_from_env
        
        with patch.dict(os.environ, {'API_URL': 'http://example.com'}):
            result = _build_servers_from_env()
            
            assert result is not None
            assert len(result) == 1
            assert result[0]['url'] == 'http://example.com'
            assert result[0]['description'] == 'Current API server'
    
    def test_build_servers_with_https_url(self):
        """Test server configuration with HTTPS URL"""
        import api.api as api_module
        _build_servers_from_env = api_module._build_servers_from_env
        
        with patch.dict(os.environ, {'API_URL': 'https://example.com'}):
            result = _build_servers_from_env()
            
            assert result is not None
            assert len(result) == 1
            assert result[0]['url'] == 'https://example.com'
    
    def test_build_servers_with_relative_url(self):
        """Test server configuration with relative URL"""
        import api.api as api_module
        _build_servers_from_env = api_module._build_servers_from_env
        
        with patch.dict(os.environ, {'API_URL': '/api/v1'}):
            result = _build_servers_from_env()
            
            assert result is None
    
    def test_build_servers_with_empty_url(self):
        """Test server configuration with empty URL"""
        import api.api as api_module
        _build_servers_from_env = api_module._build_servers_from_env
        
        with patch.dict(os.environ, {'API_URL': ''}):
            result = _build_servers_from_env()
            
            assert result is None
    
    def test_build_servers_with_no_url(self):
        """Test server configuration with no API_URL set"""
        import api.api as api_module
        _build_servers_from_env = api_module._build_servers_from_env
        
        with patch.dict(os.environ, {}, clear=True):
            result = _build_servers_from_env()
            
            assert result is None


@pytest.mark.asyncio
class TestAppEndpoints:
    """Tests for app endpoints"""
    
    async def test_read_root(self):
        """Test root endpoint returns welcome message"""
        import api.api as api_module
        read_root = api_module.read_root
        
        result = await read_root()
        
        assert result is not None
        assert 'message' in result
        assert 'Precon League API' in result['message']
        assert '@atauln' in result['message']


class TestAppInitialization:
    """Tests for FastAPI app initialization"""
    
    def test_app_exists(self):
        """Test that app is created"""
        import api.api as api_module
        app = api_module.app
        
        assert app is not None
        assert app.title == "Precon League API"
        assert app.version == "1.0.0"
    
    def test_app_routers_included(self):
        """Test that all routers are included"""
        import api.api as api_module
        app = api_module.app
        
        # Check that routers are included by checking the routes
        routes = [route.path for route in app.routes]
        
        # Expect routes from users, decks, snapshots, and cards routers
        assert any('/users' in route for route in routes)
        assert any('/decks' in route for route in routes)
        assert any('/snapshots' in route for route in routes)
        assert any('/cards' in route for route in routes)
