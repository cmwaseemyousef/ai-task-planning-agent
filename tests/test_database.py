"""
Test cases for database operations
"""

import pytest
import tempfile
import os
from datetime import datetime

from database.database import DatabaseManager
from database.models import Plan, PlanStep


class TestDatabaseManager:
    """Test cases for DatabaseManager"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        db_url = f"sqlite:///{temp_file.name}"
        db_manager = DatabaseManager(db_url)
        
        yield db_manager
        
        # Cleanup
        os.unlink(temp_file.name)
    
    @pytest.fixture
    def sample_plan_data(self):
        """Sample plan data for testing"""
        return {
            "goal": "Test plan for visiting Jaipur",
            "created_at": datetime.now().isoformat(),
            "total_steps": 2,
            "estimated_total_duration": "1 day",
            "steps": [
                {
                    "step_number": 1,
                    "title": "Visit Amber Fort",
                    "description": "Explore the historic Amber Fort",
                    "estimated_duration": "3 hours",
                    "requires_research": True,
                    "research_topics": ["Amber Fort", "Jaipur history"]
                },
                {
                    "step_number": 2,
                    "title": "Local Food Tour",
                    "description": "Try traditional Rajasthani cuisine",
                    "estimated_duration": "2 hours",
                    "requires_research": True,
                    "research_topics": ["Rajasthani food", "Jaipur restaurants"]
                }
            ],
            "metadata": {
                "has_weather_info": False,
                "has_web_research": True,
                "research_topics": ["Amber Fort", "Jaipur history", "Rajasthani food"]
            }
        }
    
    def test_save_plan(self, temp_db, sample_plan_data):
        """Test saving a plan"""
        plan_id = temp_db.save_plan(sample_plan_data)
        
        assert plan_id is not None
        assert isinstance(plan_id, int)
        assert plan_id > 0
    
    def test_save_invalid_plan(self, temp_db):
        """Test saving invalid plan data"""
        # Test with empty data
        plan_id = temp_db.save_plan({})
        assert plan_id is None
        
        # Test with missing goal
        plan_id = temp_db.save_plan({"steps": []})
        assert plan_id is None
    
    def test_get_plan_by_id(self, temp_db, sample_plan_data):
        """Test retrieving a plan by ID"""
        plan_id = temp_db.save_plan(sample_plan_data)
        retrieved_plan = temp_db.get_plan_by_id(plan_id)
        
        assert retrieved_plan is not None
        assert retrieved_plan['id'] == plan_id
        assert retrieved_plan['goal'] == sample_plan_data['goal']
        assert retrieved_plan['plan_data']['total_steps'] == 2
    
    def test_get_nonexistent_plan(self, temp_db):
        """Test retrieving non-existent plan"""
        plan = temp_db.get_plan_by_id(999)
        assert plan is None
    
    def test_get_all_plans(self, temp_db, sample_plan_data):
        """Test retrieving all plans"""
        # Save multiple plans
        plan1_data = sample_plan_data.copy()
        plan1_data['goal'] = "First test plan"
        plan1_id = temp_db.save_plan(plan1_data)
        
        plan2_data = sample_plan_data.copy()
        plan2_data['goal'] = "Second test plan"
        plan2_id = temp_db.save_plan(plan2_data)
        
        all_plans = temp_db.get_all_plans()
        
        assert len(all_plans) == 2
        assert any(p['id'] == plan1_id for p in all_plans)
        assert any(p['id'] == plan2_id for p in all_plans)
    
    def test_search_plans(self, temp_db, sample_plan_data):
        """Test searching plans"""
        # Save plans with different goals
        jaipur_plan = sample_plan_data.copy()
        jaipur_plan['goal'] = "Visit Jaipur and see palaces"
        jaipur_id = temp_db.save_plan(jaipur_plan)
        
        mumbai_plan = sample_plan_data.copy()
        mumbai_plan['goal'] = "Explore Mumbai beaches"
        mumbai_id = temp_db.save_plan(mumbai_plan)
        
        # Search for Jaipur
        jaipur_results = temp_db.search_plans("Jaipur")
        assert len(jaipur_results) == 1
        assert jaipur_results[0]['id'] == jaipur_id
        
        # Search for Mumbai
        mumbai_results = temp_db.search_plans("Mumbai")
        assert len(mumbai_results) == 1
        assert mumbai_results[0]['id'] == mumbai_id
        
        # Search for non-existent term
        no_results = temp_db.search_plans("nonexistent")
        assert len(no_results) == 0
    
    def test_delete_plan(self, temp_db, sample_plan_data):
        """Test deleting a plan"""
        plan_id = temp_db.save_plan(sample_plan_data)
        
        # Verify plan exists
        plan = temp_db.get_plan_by_id(plan_id)
        assert plan is not None
        
        # Delete plan
        deleted = temp_db.delete_plan(plan_id)
        assert deleted is True
        
        # Verify plan no longer exists
        plan = temp_db.get_plan_by_id(plan_id)
        assert plan is None
    
    def test_delete_nonexistent_plan(self, temp_db):
        """Test deleting non-existent plan"""
        deleted = temp_db.delete_plan(999)
        assert deleted is False
    
    def test_update_plan(self, temp_db, sample_plan_data):
        """Test updating a plan"""
        plan_id = temp_db.save_plan(sample_plan_data)
        
        # Update the plan
        update_data = {"goal": "Updated goal for Jaipur trip"}
        updated = temp_db.update_plan(plan_id, update_data)
        assert updated is True
        
        # Verify update
        plan = temp_db.get_plan_by_id(plan_id)
        assert plan['goal'] == "Updated goal for Jaipur trip"
        assert plan['plan_data']['goal'] == "Updated goal for Jaipur trip"
    
    def test_get_plan_statistics(self, temp_db, sample_plan_data):
        """Test getting plan statistics"""
        # Initially no plans
        stats = temp_db.get_plan_statistics()
        assert stats['total_plans'] == 0
        
        # Add some plans
        temp_db.save_plan(sample_plan_data)
        temp_db.save_plan(sample_plan_data)
        
        stats = temp_db.get_plan_statistics()
        assert stats['total_plans'] == 2
        assert 'total_steps' in stats
        assert 'recent_plans' in stats
    
    def test_pagination(self, temp_db, sample_plan_data):
        """Test pagination functionality"""
        # Create multiple plans
        for i in range(5):
            plan_data = sample_plan_data.copy()
            plan_data['goal'] = f"Test plan {i}"
            temp_db.save_plan(plan_data)
        
        # Test pagination
        page1 = temp_db.get_all_plans(limit=2, offset=0)
        assert len(page1) == 2
        
        page2 = temp_db.get_all_plans(limit=2, offset=2)
        assert len(page2) == 2
        
        # Verify different plans
        page1_ids = [p['id'] for p in page1]
        page2_ids = [p['id'] for p in page2]
        assert set(page1_ids).isdisjoint(set(page2_ids))