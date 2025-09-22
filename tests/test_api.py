"""
Test cases for API endpoints
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Import the FastAPI app
from main import app
from database.database import DatabaseManager


class TestAPI:
    """Test cases for API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        db_url = f"sqlite:///{temp_file.name}"
        
        with patch('main.db_manager') as mock_db:
            mock_db_instance = DatabaseManager(db_url)
            mock_db.return_value = mock_db_instance
            yield mock_db_instance
        
        # Cleanup
        os.unlink(temp_file.name)
    
    def test_home_page(self, client):
        """Test home page endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_create_plan_valid(self, client):
        """Test creating a plan with valid data"""
        with patch('main.agent') as mock_agent:
            mock_agent.create_plan.return_value = {
                "id": None,
                "goal": "Test plan",
                "total_steps": 1,
                "steps": []
            }
            
            with patch('main.db_manager') as mock_db:
                mock_db.save_plan.return_value = 1
                
                response = client.post("/create-plan", data={"goal": "Test plan for Jaipur"})
                assert response.status_code == 303  # Redirect
                assert "/plan/1" in response.headers["location"]
    
    def test_create_plan_invalid_goal(self, client):
        """Test creating a plan with invalid goal"""
        # Empty goal
        response = client.post("/create-plan", data={"goal": ""})
        assert response.status_code == 400
        
        # Too short goal
        response = client.post("/create-plan", data={"goal": "Hi"})
        assert response.status_code == 400
        
        # Goal with dangerous content
        response = client.post("/create-plan", data={"goal": "<script>alert('test')</script>"})
        assert response.status_code == 400
    
    def test_view_plan_valid(self, client):
        """Test viewing a valid plan"""
        mock_plan = {
            "id": 1,
            "goal": "Test plan",
            "plan_data": {"steps": []},
            "created_at": "2023-01-01T00:00:00"
        }
        
        with patch('main.db_manager') as mock_db:
            mock_db.get_plan_by_id.return_value = mock_plan
            
            response = client.get("/plan/1")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]
    
    def test_view_plan_not_found(self, client):
        """Test viewing non-existent plan"""
        with patch('main.db_manager') as mock_db:
            mock_db.get_plan_by_id.return_value = None
            
            response = client.get("/plan/999")
            assert response.status_code == 404
    
    def test_view_plan_invalid_id(self, client):
        """Test viewing plan with invalid ID"""
        response = client.get("/plan/0")
        assert response.status_code == 400
        
        response = client.get("/plan/-1")
        assert response.status_code == 400
    
    def test_list_plans(self, client):
        """Test listing plans"""
        mock_plans = [
            {
                "id": 1,
                "goal": "Test plan 1",
                "created_at": "2023-01-01T00:00:00",
                "total_steps": 2
            },
            {
                "id": 2,
                "goal": "Test plan 2",
                "created_at": "2023-01-02T00:00:00",
                "total_steps": 3
            }
        ]
        
        with patch('main.db_manager') as mock_db:
            mock_db.get_all_plans.return_value = mock_plans
            
            response = client.get("/plans")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]
    
    def test_search_plans(self, client):
        """Test searching plans"""
        mock_results = [
            {
                "id": 1,
                "goal": "Jaipur trip plan",
                "created_at": "2023-01-01T00:00:00",
                "total_steps": 2
            }
        ]
        
        with patch('main.db_manager') as mock_db:
            mock_db.search_plans.return_value = mock_results
            
            response = client.get("/plans?search=Jaipur")
            assert response.status_code == 200
    
    def test_api_get_plan(self, client):
        """Test API endpoint for getting plan"""
        mock_plan = {
            "id": 1,
            "goal": "Test plan",
            "plan_data": {"steps": []},
            "created_at": "2023-01-01T00:00:00"
        }
        
        with patch('main.db_manager') as mock_db:
            mock_db.get_plan_by_id.return_value = mock_plan
            
            response = client.get("/api/plans/1")
            assert response.status_code == 200
            assert response.json() == mock_plan
    
    def test_api_list_plans(self, client):
        """Test API endpoint for listing plans"""
        mock_plans = [
            {"id": 1, "goal": "Test plan 1"},
            {"id": 2, "goal": "Test plan 2"}
        ]
        
        with patch('main.db_manager') as mock_db:
            mock_db.get_all_plans.return_value = mock_plans
            
            response = client.get("/api/plans")
            assert response.status_code == 200
            data = response.json()
            assert "plans" in data
            assert len(data["plans"]) == 2
    
    def test_api_delete_plan(self, client):
        """Test API endpoint for deleting plan"""
        with patch('main.db_manager') as mock_db:
            mock_db.delete_plan.return_value = True
            
            response = client.delete("/api/plans/1")
            assert response.status_code == 200
            assert response.json()["message"] == "Plan deleted successfully"
    
    def test_api_delete_plan_not_found(self, client):
        """Test deleting non-existent plan via API"""
        with patch('main.db_manager') as mock_db:
            mock_db.delete_plan.return_value = False
            
            response = client.delete("/api/plans/999")
            assert response.status_code == 404
    
    def test_api_update_plan(self, client):
        """Test API endpoint for updating plan"""
        mock_plan = {
            "id": 1,
            "goal": "Updated test plan",
            "plan_data": {"steps": []}
        }
        
        with patch('main.db_manager') as mock_db:
            mock_db.get_plan_by_id.return_value = mock_plan
            mock_db.update_plan.return_value = True
            
            update_data = {"goal": "Updated test plan"}
            response = client.put("/api/plans/1", json=update_data)
            assert response.status_code == 200
    
    def test_api_stats(self, client):
        """Test API stats endpoint"""
        mock_stats = {
            "total_plans": 5,
            "total_steps": 15,
            "recent_plans": 2
        }
        
        with patch('main.db_manager') as mock_db:
            mock_db.get_plan_statistics.return_value = mock_stats
            
            response = client.get("/api/stats")
            assert response.status_code == 200
            assert response.json() == mock_stats
    
    def test_pagination_parameters(self, client):
        """Test pagination parameters"""
        with patch('main.db_manager') as mock_db:
            mock_db.get_all_plans.return_value = []
            
            # Test valid pagination
            response = client.get("/plans?page=2&limit=10")
            assert response.status_code == 200
            
            # Test invalid pagination (should be corrected)
            response = client.get("/plans?page=0&limit=1000")
            assert response.status_code == 200
    
    def test_error_handling(self, client):
        """Test error handling for various scenarios"""
        with patch('main.db_manager') as mock_db:
            # Simulate database error
            mock_db.get_plan_by_id.side_effect = Exception("Database error")
            
            response = client.get("/plan/1")
            assert response.status_code == 500