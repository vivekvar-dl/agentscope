"""
AgentScope Backend API - FastAPI
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import json
import uuid

app = FastAPI(
    title="AgentScope API",
    description="Real-time AI Agent Monitoring API",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class AgentConfig(BaseModel):
    model: str = Field(..., example="gpt-3.5-turbo")
    task: str = Field(..., example="Research AI agents")
    max_tokens: int = Field(2000, ge=100, le=100000)
    temperature: float = Field(0.7, ge=0, le=2)
    tools: List[str] = Field(default_factory=list)

class ExecutionStep(BaseModel):
    timestamp: datetime
    type: str
    content: str
    tokens: int = 0
    cost: float = 0.0
    duration_ms: int = 0
    metadata: Dict[str, Any] = {}

class AgentMetrics(BaseModel):
    execution_id: str
    status: str
    duration_seconds: float
    total_tokens: int
    total_cost: float
    tool_calls: int
    decisions: int
    steps: List[ExecutionStep]

class ExecutionRequest(BaseModel):
    config: AgentConfig
    stream: bool = True

# In-memory storage (use Redis/DB in production)
active_executions: Dict[str, AgentMetrics] = {}

# Pricing (per 1M tokens)
MODEL_PRICING = {
    "gpt-4": {"prompt": 30.0, "completion": 60.0},
    "gpt-3.5-turbo": {"prompt": 0.5, "completion": 1.5},
    "claude-3-opus": {"prompt": 15.0, "completion": 75.0},
    "claude-3-sonnet": {"prompt": 3.0, "completion": 15.0},
    "gemini-pro": {"prompt": 0.5, "completion": 1.5},
}

def calculate_cost(model: str, tokens: int) -> float:
    """Calculate cost for model."""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-3.5-turbo"])
    return (tokens / 1_000_000) * pricing["prompt"]

@app.get("/")
async def root():
    """API health check."""
    return {
        "service": "AgentScope API",
        "version": "0.1.0",
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/api/models")
async def get_models():
    """Get available models."""
    return {
        "models": [
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "provider": "OpenAI",
                "cost_per_1k": "$0.03"
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "provider": "OpenAI",
                "cost_per_1k": "$0.0005"
            },
            {
                "id": "claude-3-opus",
                "name": "Claude 3 Opus",
                "provider": "Anthropic",
                "cost_per_1k": "$0.015"
            },
            {
                "id": "claude-3-sonnet",
                "name": "Claude 3 Sonnet",
                "provider": "Anthropic",
                "cost_per_1k": "$0.003"
            },
            {
                "id": "gemini-pro",
                "name": "Gemini Pro",
                "provider": "Google",
                "cost_per_1k": "$0.0005"
            }
        ]
    }

@app.post("/api/execute")
async def execute_agent(request: ExecutionRequest):
    """Execute agent and return metrics."""
    execution_id = str(uuid.uuid4())
    
    # Simulate agent execution
    steps = await simulate_execution(
        request.config.model,
        request.config.task,
        request.config.max_tokens
    )
    
    total_tokens = sum(step.tokens for step in steps)
    total_cost = calculate_cost(request.config.model, total_tokens)
    duration = sum(step.duration_ms for step in steps) / 1000.0
    
    metrics = AgentMetrics(
        execution_id=execution_id,
        status="completed",
        duration_seconds=duration,
        total_tokens=total_tokens,
        total_cost=total_cost,
        tool_calls=sum(1 for s in steps if s.type == "tool_call"),
        decisions=sum(1 for s in steps if s.type == "decision"),
        steps=steps
    )
    
    active_executions[execution_id] = metrics
    
    return metrics

@app.get("/api/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get execution metrics by ID."""
    if execution_id not in active_executions:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return active_executions[execution_id]

@app.websocket("/ws/execute")
async def websocket_execute(websocket: WebSocket):
    """WebSocket endpoint for real-time execution streaming."""
    await websocket.accept()
    
    try:
        # Receive config
        data = await websocket.receive_json()
        config = AgentConfig(**data)
        
        execution_id = str(uuid.uuid4())
        
        # Send execution started
        await websocket.send_json({
            "type": "started",
            "execution_id": execution_id
        })
        
        # Simulate execution with real-time updates
        steps = []
        total_tokens = 0
        total_cost = 0.0
        
        # Step 1: Planning
        await asyncio.sleep(0.5)
        step = ExecutionStep(
            timestamp=datetime.now(),
            type="thought",
            content="Analyzing task and planning approach",
            tokens=150,
            cost=calculate_cost(config.model, 150),
            duration_ms=500
        )
        steps.append(step)
        total_tokens += step.tokens
        total_cost += step.cost
        
        await websocket.send_json({
            "type": "step",
            "step": step.dict(),
            "metrics": {
                "total_tokens": total_tokens,
                "total_cost": total_cost
            }
        })
        
        # Step 2: Tool call
        await asyncio.sleep(0.8)
        step = ExecutionStep(
            timestamp=datetime.now(),
            type="tool_call",
            content="web_search('AI agents 2024')",
            tokens=200,
            cost=calculate_cost(config.model, 200),
            duration_ms=800,
            metadata={"tool": "web_search", "success": True}
        )
        steps.append(step)
        total_tokens += step.tokens
        total_cost += step.cost
        
        await websocket.send_json({
            "type": "step",
            "step": step.dict(),
            "metrics": {
                "total_tokens": total_tokens,
                "total_cost": total_cost
            }
        })
        
        # Step 3: Processing
        await asyncio.sleep(0.6)
        step = ExecutionStep(
            timestamp=datetime.now(),
            type="thought",
            content="Analyzing search results",
            tokens=300,
            cost=calculate_cost(config.model, 300),
            duration_ms=600
        )
        steps.append(step)
        total_tokens += step.tokens
        total_cost += step.cost
        
        await websocket.send_json({
            "type": "step",
            "step": step.dict(),
            "metrics": {
                "total_tokens": total_tokens,
                "total_cost": total_cost
            }
        })
        
        # Step 4: Decision
        await asyncio.sleep(0.5)
        step = ExecutionStep(
            timestamp=datetime.now(),
            type="decision",
            content="Formulating final response",
            tokens=250,
            cost=calculate_cost(config.model, 250),
            duration_ms=500
        )
        steps.append(step)
        total_tokens += step.tokens
        total_cost += step.cost
        
        await websocket.send_json({
            "type": "step",
            "step": step.dict(),
            "metrics": {
                "total_tokens": total_tokens,
                "total_cost": total_cost
            }
        })
        
        # Send completion
        metrics = AgentMetrics(
            execution_id=execution_id,
            status="completed",
            duration_seconds=2.4,
            total_tokens=total_tokens,
            total_cost=total_cost,
            tool_calls=1,
            decisions=1,
            steps=steps
        )
        
        await websocket.send_json({
            "type": "completed",
            "metrics": metrics.dict()
        })
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

async def simulate_execution(model: str, task: str, max_tokens: int) -> List[ExecutionStep]:
    """Simulate agent execution."""
    steps = []
    
    # Planning
    steps.append(ExecutionStep(
        timestamp=datetime.now(),
        type="thought",
        content="Planning approach",
        tokens=150,
        cost=calculate_cost(model, 150),
        duration_ms=500
    ))
    
    # Tool calls
    steps.append(ExecutionStep(
        timestamp=datetime.now(),
        type="tool_call",
        content="web_search(query)",
        tokens=200,
        cost=calculate_cost(model, 200),
        duration_ms=800,
        metadata={"tool": "web_search"}
    ))
    
    # Processing
    steps.append(ExecutionStep(
        timestamp=datetime.now(),
        type="thought",
        content="Analyzing results",
        tokens=300,
        cost=calculate_cost(model, 300),
        duration_ms=600
    ))
    
    # Decision
    steps.append(ExecutionStep(
        timestamp=datetime.now(),
        type="decision",
        content="Final response",
        tokens=250,
        cost=calculate_cost(model, 250),
        duration_ms=500
    ))
    
    return steps

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
