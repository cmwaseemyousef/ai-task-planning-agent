"""
FastAPI web application for the AI Task Planning Agent
"""

from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
import uvicorn
import os
import logging
import re
from typing import Optional
from pydantic import BaseModel, Field, validator

from agent.task_planner import TaskPlanningAgent
from agent.mock_agent import MockTaskPlanningAgent
from database.database import DatabaseManager
from tools.export import plan_exporter

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.getenv("LOG_FILE", "app.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Task Planning Agent", 
    description="""An intelligent AI agent that helps users transform natural language goals into actionable, structured plans with external information enrichment.
    
    ## Features
    
    * **Natural Language Processing**: Convert goals into structured plans
    * **External Data Integration**: Web search and weather information
    * **Plan Storage**: SQLite database with full plan history
    * **Web Interface**: User-friendly interface for plan creation and management
    * **REST API**: Complete API for programmatic access
    
    ## Example Goals
    
    * "Plan a 3-day trip to Jaipur with cultural highlights and good food"
    * "Organise a 5-step daily study routine for learning Python"
    * "Create a weekend plan in Vizag with beach, hiking, and seafood"
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "AI Task Planning Agent",
        "email": "cmwaseemyousef@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    tags_metadata=[
        {
            "name": "Web Interface",
            "description": "HTML pages for web interface",
        },
        {
            "name": "Plans",
            "description": "Operations with plans. Create, read, update and delete plans.",
        },
        {
            "name": "Statistics",
            "description": "Database and usage statistics",
        },
        {
            "name": "Export",
            "description": "Export plans to various formats (JSON, CSV, Markdown)",
        },
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize templates
templates = Jinja2Templates(directory="web/templates")

# Mount static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Pydantic models for API documentation
class GoalInput(BaseModel):
    """Input model for creating plans"""
    goal: str = Field(
        ..., 
        min_length=5, 
        max_length=500, 
        description="Natural language description of the goal to be planned",
        example="Plan a 3-day trip to Jaipur with cultural highlights and good food"
    )
    
    @validator('goal')
    def validate_goal(cls, v):
        if not v.strip():
            raise ValueError('Goal cannot be empty or just whitespace')
        
        # Basic security check for potential injection
        dangerous_patterns = ['<script', 'javascript:', 'eval(', 'exec(']
        if any(pattern in v.lower() for pattern in dangerous_patterns):
            raise ValueError('Goal contains potentially dangerous content')
        
        return v.strip()

class PlanUpdateInput(BaseModel):
    """Input model for updating plans"""
    goal: Optional[str] = Field(
        None, 
        min_length=5, 
        max_length=500,
        description="Updated goal description",
        example="Updated plan for a 4-day trip to Jaipur"
    )

class PlanResponse(BaseModel):
    """Response model for plan data"""
    id: int = Field(description="Unique plan identifier")
    goal: str = Field(description="The original goal")
    plan_data: dict = Field(description="Complete plan data with steps and metadata")
    created_at: str = Field(description="Creation timestamp (ISO format)")
    updated_at: str = Field(description="Last update timestamp (ISO format)")

class PlanSummary(BaseModel):
    """Summary model for plan listings"""
    id: int = Field(description="Unique plan identifier")
    goal: str = Field(description="The original goal")
    created_at: str = Field(description="Creation timestamp (ISO format)")
    updated_at: str = Field(description="Last update timestamp (ISO format)")
    total_steps: int = Field(description="Number of steps in the plan")
    estimated_duration: str = Field(description="Estimated total duration")
    has_weather_info: bool = Field(description="Whether plan includes weather information")
    has_web_research: bool = Field(description="Whether plan includes web research")
    preview: str = Field(description="Preview of the goal (truncated)")
    ai_provider: str = Field(description="AI provider used (openai/mock)")

class PlansListResponse(BaseModel):
    """Response model for plan listings"""
    plans: list[PlanSummary] = Field(description="List of plan summaries")
    limit: int = Field(description="Number of plans per page")
    offset: int = Field(description="Number of plans skipped")
    search_query: Optional[str] = Field(description="Search query used (if any)")

class StatisticsResponse(BaseModel):
    """Response model for statistics"""
    total_plans: int = Field(description="Total number of plans in database")
    total_steps: int = Field(description="Total number of steps across all plans")
    recent_plans: int = Field(description="Number of plans created in last 7 days")
    average_steps_per_plan: float = Field(description="Average number of steps per plan")
    database_url: str = Field(description="Database connection URL (sanitized)")

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str = Field(description="Response message")
    
# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception for {request.url}: {str(exc)}")
    return await http_exception_handler(request, HTTPException(
        status_code=500, 
        detail="An internal server error occurred"
    ))

# Initialize components with fallback to mock agent
def create_agent():
    """Create agent with fallback to mock version if OpenAI fails"""
    try:
        agent = TaskPlanningAgent()
        # Test the agent with a simple call
        from openai import OpenAI
        client = OpenAI()
        client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        logger.info("✅ Using real OpenAI agent")
        return agent
    except Exception as e:
        logger.warning(f"⚠️  OpenAI not available ({str(e)[:50]}...), using mock agent for demo")
        return MockTaskPlanningAgent()

agent = create_agent()
db_manager = DatabaseManager()

@app.get("/", response_class=HTMLResponse, tags=["Web Interface"])
async def home(request: Request):
    """Home page with goal input form"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/create-plan", tags=["Web Interface"])
async def create_plan(
    goal: str = Form(
        ..., 
        description="Goal description",
        example="Plan a weekend trip to Goa"
    )
):
    """Create a new plan from a goal"""
    try:
        # Validate input
        goal_input = GoalInput(goal=goal)
        logger.info(f"Creating plan for goal: {goal_input.goal[:50]}...")
        
        # Generate plan using the AI agent
        plan_data = agent.create_plan(goal_input.goal)
        
        if not plan_data or not isinstance(plan_data, dict):
            raise HTTPException(status_code=500, detail="Failed to generate valid plan")
        
        # Save to database
        plan_id = db_manager.save_plan(plan_data)
        
        if not plan_id:
            raise HTTPException(status_code=500, detail="Failed to save plan")
        
        logger.info(f"Plan created successfully with ID: {plan_id}")
        # Redirect to view the plan
        return RedirectResponse(url=f"/plan/{plan_id}", status_code=303)
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to create plan")

@app.get("/plan/{plan_id}", response_class=HTMLResponse, tags=["Web Interface"])
async def view_plan(
    request: Request, 
    plan_id: int
):
    """View a specific plan"""
    try:
        if plan_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid plan ID")
        
        plan = db_manager.get_plan_by_id(plan_id)
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return templates.TemplateResponse("plan_detail.html", {
            "request": request,
            "plan": plan
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error viewing plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving plan")

@app.get("/plans", response_class=HTMLResponse, tags=["Web Interface"])
async def list_plans(
    request: Request, 
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """List all plans with optional search and pagination"""
    try:
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 20
        
        # Validate search query
        if search:
            search = search.strip()[:100]  # Limit search length
            if len(search) < 2:
                search = None
        
        if search:
            plans = db_manager.search_plans(search, limit, offset=(page-1)*limit)
        else:
            plans = db_manager.get_all_plans(limit, offset=(page-1)*limit)
        
        return templates.TemplateResponse("plan_list.html", {
            "request": request,
            "plans": plans,
            "search_query": search or "",
            "current_page": page,
            "limit": limit
        })
    except Exception as e:
        logger.error(f"Error listing plans: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving plans")

@app.get(
    "/api/plans/{plan_id}", 
    response_model=PlanResponse,
    tags=["Plans"],
    summary="Get a plan by ID",
    description="Retrieve detailed information about a specific plan including all steps and metadata."
)
async def get_plan_api(
    plan_id: int
):
    """API endpoint to get plan data as JSON"""
    try:
        if plan_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid plan ID")
        
        plan = db_manager.get_plan_by_id(plan_id)
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        return plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving plan")

@app.get(
    "/api/plans", 
    response_model=PlansListResponse,
    tags=["Plans"],
    summary="List all plans",
    description="Retrieve a paginated list of all plans with optional search functionality."
)
async def list_plans_api(
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """API endpoint to list plans as JSON"""
    try:
        # Validate parameters
        limit = max(1, min(limit, 100))  # Between 1 and 100
        offset = max(0, offset)
        
        if search:
            search = search.strip()[:100]
            if len(search) < 2:
                search = None
        
        if search:
            plans = db_manager.search_plans(search, limit, offset)
        else:
            plans = db_manager.get_all_plans(limit, offset)
        
        return {
            "plans": plans,
            "limit": limit,
            "offset": offset,
            "search_query": search
        }
    except Exception as e:
        logger.error(f"Error listing plans API: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving plans")

@app.delete(
    "/api/plans/{plan_id}", 
    response_model=MessageResponse,
    tags=["Plans"],
    summary="Delete a plan",
    description="Permanently delete a plan and all its associated data."
)
async def delete_plan_api(
    plan_id: int
):
    """API endpoint to delete a plan"""
    try:
        if plan_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid plan ID")
        
        deleted = db_manager.delete_plan(plan_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        logger.info(f"Plan {plan_id} deleted successfully")
        return {"message": "Plan deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting plan")

@app.get(
    "/api/stats", 
    response_model=StatisticsResponse,
    tags=["Statistics"],
    summary="Get database statistics",
    description="Retrieve comprehensive statistics about plans, steps, and database usage."
)
async def get_stats():
    """API endpoint for database statistics"""
    try:
        return db_manager.get_plan_statistics()
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")

# Add plan update endpoint
@app.put(
    "/api/plans/{plan_id}", 
    response_model=PlanResponse,
    tags=["Plans"],
    summary="Update a plan",
    description="Update an existing plan's goal or other metadata."
)
async def update_plan_api(
    plan_id: int,
    plan_update: PlanUpdateInput
):
    """API endpoint to update a plan"""
    try:
        if plan_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid plan ID")
        
        # Check if plan exists
        existing_plan = db_manager.get_plan_by_id(plan_id)
        if not existing_plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Update plan
        updated = db_manager.update_plan(plan_id, plan_update.dict(exclude_unset=True))
        
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update plan")
        
        logger.info(f"Plan {plan_id} updated successfully")
        return db_manager.get_plan_by_id(plan_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating plan")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "localhost")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
# Export endpoints
@app.get(
    "/api/plans/{plan_id}/export/{format_type}",
    tags=["Export"],
    summary="Export a single plan",
    description="Export a specific plan to JSON, CSV, or Markdown format."
)
async def export_single_plan(
    plan_id: int,
    format_type: str
):
    """Export a single plan in the specified format"""
    try:
        if plan_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid plan ID")
        
        plan = db_manager.get_plan_by_id(plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        plans = [plan]
        
        if format_type == "json":
            content = plan_exporter.export_to_json(plans)
        elif format_type == "csv":
            content = plan_exporter.export_to_csv(plans)
        elif format_type == "markdown":
            content = plan_exporter.export_to_markdown(plans)
        else:
            raise HTTPException(status_code=400, detail="Invalid format type")
        
        filename = plan_exporter.get_export_filename(format_type, 1)
        content_type = plan_exporter.get_content_type(format_type)
        
        return plan_exporter.create_streaming_response(content, filename, content_type)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting plan {plan_id}: {e}")
        raise HTTPException(status_code=500, detail="Error exporting plan")

@app.get(
    "/api/plans/export/{format_type}",
    tags=["Export"],
    summary="Export multiple plans",
    description="Export multiple plans with optional filtering to JSON, CSV, or Markdown format."
)
async def export_multiple_plans(
    format_type: str,
    search: Optional[str] = None,
    limit: int = 50,
    include_steps: bool = True
):
    """Export multiple plans in the specified format"""
    try:
        # Get plans based on search criteria
        if search:
            plans_summary = db_manager.search_plans(search, limit)
        else:
            plans_summary = db_manager.get_all_plans(limit)
        
        if not plans_summary:
            raise HTTPException(status_code=404, detail="No plans found")
        
        # Get full plan data if needed
        if include_steps:
            plans = []
            for plan_summary in plans_summary:
                full_plan = db_manager.get_plan_by_id(plan_summary['id'])
                if full_plan:
                    plans.append(full_plan)
        else:
            # Use summary data
            plans = plans_summary
        
        if format_type == "json":
            content = plan_exporter.export_to_json(plans)
        elif format_type == "csv":
            content = plan_exporter.export_to_csv(plans)
        elif format_type == "markdown":
            content = plan_exporter.export_to_markdown(plans)
        else:
            raise HTTPException(status_code=400, detail="Invalid format type")
        
        filename = plan_exporter.get_export_filename(format_type, len(plans))
        content_type = plan_exporter.get_content_type(format_type)
        
        return plan_exporter.create_streaming_response(content, filename, content_type)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting plans: {e}")
        raise HTTPException(status_code=500, detail="Error exporting plans")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "localhost")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=debug)