"""
Database operations for managing plans
"""

from sqlalchemy import create_engine, desc, func, or_
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional, Dict, Any
import os
import logging
from datetime import datetime

from .models import Base, Plan, PlanStep

class DatabaseManager:
    """Manages database operations for plans"""
    
    def __init__(self, database_url: str = None):
        """Initialize database manager"""
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///./plans.db")
        
        self.logger = logging.getLogger(__name__)
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        try:
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("Database tables created successfully")
        except Exception as e:
            self.logger.error(f"Error creating database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session with error handling"""
        try:
            return self.SessionLocal()
        except Exception as e:
            self.logger.error(f"Error creating database session: {e}")
            raise
    
    def save_plan(self, plan_data: Dict) -> Optional[int]:
        """
        Save a plan to the database
        
        Args:
            plan_data (Dict): Complete plan data from the agent
            
        Returns:
            Optional[int]: Plan ID or None if failed
        """
        if not plan_data or 'goal' not in plan_data:
            self.logger.error("Invalid plan data provided")
            return None
            
        with self.get_session() as session:
            try:
                # Create main plan record
                plan = Plan(
                    goal=plan_data['goal'],
                    plan_data=plan_data
                )
                
                session.add(plan)
                session.flush()  # Get the ID without committing
                
                plan_id = plan.id
                
                # Create individual step records for easier querying
                for step in plan_data.get('steps', []):
                    plan_step = PlanStep(
                        plan_id=plan_id,
                        step_number=step.get('step_number', 1),
                        title=step.get('title', 'Untitled Step'),
                        description=step.get('description', ''),
                        estimated_duration=step.get('estimated_duration', ''),
                        step_data=step
                    )
                    session.add(plan_step)
                
                session.commit()
                self.logger.info(f"Plan saved with ID: {plan_id}")
                return plan_id
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Error saving plan: {e}")
                return None
    
    def get_plan_by_id(self, plan_id: int) -> Optional[Dict]:
        """
        Get a plan by its ID
        
        Args:
            plan_id (int): Plan ID
            
        Returns:
            Dict: Plan data or None if not found
        """
        with self.get_session() as session:
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
            if plan:
                return plan.to_dict()
            return None
    
    def get_all_plans(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Get all plans ordered by creation date (newest first)
        
        Args:
            limit (int): Maximum number of plans to return
            offset (int): Number of plans to skip
            
        Returns:
            List[Dict]: List of plan summaries
        """
        with self.get_session() as session:
            try:
                plans = session.query(Plan).order_by(desc(Plan.created_at)).limit(limit).offset(offset).all()
                return [self._plan_to_summary(plan) for plan in plans]
            except Exception as e:
                self.logger.error(f"Error getting all plans: {e}")
                return []
    
    def search_plans(self, query: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        """
        Search plans by goal text with enhanced search capabilities
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results
            offset (int): Number of results to skip
            
        Returns:
            List[Dict]: Matching plan summaries
        """
        with self.get_session() as session:
            try:
                # Enhanced search: look in both goal and plan data
                search_terms = query.split()
                filters = []
                
                for term in search_terms:
                    filters.append(Plan.goal.contains(term))
                
                # Combine filters with OR logic for broader search
                if filters:
                    combined_filter = or_(*filters)
                    plans = session.query(Plan).filter(
                        combined_filter
                    ).order_by(desc(Plan.created_at)).limit(limit).offset(offset).all()
                else:
                    plans = []
                
                return [self._plan_to_summary(plan) for plan in plans]
            except Exception as e:
                self.logger.error(f"Error searching plans: {e}")
                return []
    
    def delete_plan(self, plan_id: int) -> bool:
        """
        Delete a plan and its steps
        
        Args:
            plan_id (int): Plan ID to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        with self.get_session() as session:
            try:
                # Delete steps first
                deleted_steps = session.query(PlanStep).filter(PlanStep.plan_id == plan_id).delete()
                
                # Delete main plan
                plan = session.query(Plan).filter(Plan.id == plan_id).first()
                if plan:
                    session.delete(plan)
                    session.commit()
                    self.logger.info(f"Plan {plan_id} and {deleted_steps} steps deleted")
                    return True
                else:
                    self.logger.warning(f"Plan {plan_id} not found for deletion")
                    return False
                    
            except Exception as e:
                session.rollback()
                self.logger.error(f"Error deleting plan {plan_id}: {e}")
                return False
    
    def update_plan(self, plan_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update a plan's data
        
        Args:
            plan_id (int): Plan ID to update
            update_data (Dict): Data to update
            
        Returns:
            bool: True if updated, False if not found
        """
        with self.get_session() as session:
            try:
                plan = session.query(Plan).filter(Plan.id == plan_id).first()
                if not plan:
                    return False
                
                # Update goal if provided
                if 'goal' in update_data:
                    plan.goal = update_data['goal']
                    # Also update the goal in plan_data
                    plan.plan_data['goal'] = update_data['goal']
                
                plan.updated_at = datetime.utcnow()
                session.commit()
                self.logger.info(f"Plan {plan_id} updated successfully")
                return True
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Error updating plan {plan_id}: {e}")
                return False
    
    def get_plan_statistics(self) -> Dict:
        """Get enhanced database statistics"""
        with self.get_session() as session:
            try:
                total_plans = session.query(Plan).count()
                total_steps = session.query(PlanStep).count()
                
                # Get recent activity (plans created in last 7 days)
                from datetime import timedelta
                week_ago = datetime.utcnow() - timedelta(days=7)
                recent_plans = session.query(Plan).filter(Plan.created_at >= week_ago).count()
                
                # Get average steps per plan
                avg_steps = session.query(func.avg(func.json_extract(Plan.plan_data, '$.total_steps'))).scalar() or 0
                
                return {
                    'total_plans': total_plans,
                    'total_steps': total_steps,
                    'recent_plans': recent_plans,
                    'average_steps_per_plan': round(float(avg_steps), 2),
                    'database_url': str(self.engine.url).replace('////', '///')
                }
            except Exception as e:
                self.logger.error(f"Error getting statistics: {e}")
                return {'error': 'Failed to get statistics'}
    
    def _plan_to_summary(self, plan: Plan) -> Dict:
        """Convert plan to summary format for listings"""
        try:
            plan_data = plan.plan_data if plan.plan_data else {}
            
            return {
                'id': plan.id,
                'goal': plan.goal,
                'created_at': plan.created_at.isoformat(),
                'updated_at': plan.updated_at.isoformat() if plan.updated_at else plan.created_at.isoformat(),
                'total_steps': plan_data.get('total_steps', 0),
                'estimated_duration': plan_data.get('estimated_total_duration', 'Unknown'),
                'has_weather_info': plan_data.get('metadata', {}).get('has_weather_info', False),
                'has_web_research': plan_data.get('metadata', {}).get('has_web_research', False),
                'preview': plan.goal[:100] + '...' if len(plan.goal) > 100 else plan.goal,
                'ai_provider': plan_data.get('metadata', {}).get('ai_provider', 'unknown')
            }
        except Exception as e:
            self.logger.error(f"Error creating plan summary: {e}")
            return {
                'id': plan.id,
                'goal': plan.goal or 'Unknown Goal',
                'created_at': plan.created_at.isoformat(),
                'error': 'Failed to load plan details'
            }