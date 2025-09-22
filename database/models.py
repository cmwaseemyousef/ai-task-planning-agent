"""
Database models for storing plans and related data
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

Base = declarative_base()

class Plan(Base):
    """Plan model for storing user goals and generated plans"""
    
    __tablename__ = 'plans'
    
    id = Column(Integer, primary_key=True, index=True)
    goal = Column(Text, nullable=False, index=True)
    plan_data = Column(JSON, nullable=False)  # Store the complete plan as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert plan to dictionary"""
        return {
            'id': self.id,
            'goal': self.goal,
            'plan_data': self.plan_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PlanStep(Base):
    """Individual step within a plan (for easier querying if needed)"""
    
    __tablename__ = 'plan_steps'
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, nullable=False, index=True)
    step_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    estimated_duration = Column(String(100))
    step_data = Column(JSON)  # Store additional step data (research, weather, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert step to dictionary"""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'step_number': self.step_number,
            'title': self.title,
            'description': self.description,
            'estimated_duration': self.estimated_duration,
            'step_data': self.step_data,
            'created_at': self.created_at.isoformat()
        }