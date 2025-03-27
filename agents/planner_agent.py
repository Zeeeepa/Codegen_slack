"""
Planner agent for creating structured plans.
"""

import logging
import os
import json
from typing import Dict, Any, List, Optional, Union

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    """
    Agent for creating structured plans.
    
    This agent can break down complex tasks into manageable steps,
    create timelines, and organize work for efficient execution.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new planner agent.
        
        Args:
            config: Optional configuration parameters
        """
        super().__init__(
            name="Planner",
            description="Creates structured plans for complex tasks",
            config=config
        )
        
        # Initialize planning tools based on config
        self.planning_methods = config.get("planning_methods", ["sequential", "hierarchical"]) if config else ["sequential", "hierarchical"]
        self.max_steps = config.get("max_steps", 10) if config else 10
        
        # Initialize state
        self.state = {
            "plan_history": [],
            "current_plan": None,
            "plans": {}
        }
    
    async def process(self, 
                     input_data: Dict[str, Any], 
                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a planning request.
        
        Args:
            input_data: The input data containing planning parameters
            context: Optional context information
            
        Returns:
            A dictionary containing the planning results
        """
        logger.info("Processing planning request")
        
        # Extract planning parameters
        task = input_data.get("task")
        planning_method = input_data.get("planning_method", "sequential")
        constraints = input_data.get("constraints", [])
        resources = input_data.get("resources", [])
        max_steps = input_data.get("max_steps", self.max_steps)
        
        # Validate input
        if not task:
            raise ValueError("Task description must be provided")
        
        # Update state
        self.state["current_plan"] = {
            "task": task,
            "planning_method": planning_method,
            "constraints": constraints,
            "resources": resources,
            "max_steps": max_steps,
            "status": "in_progress"
        }
        
        # Add to plan history
        self.state["plan_history"].append(task)
        
        # Create plan
        try:
            plan = await self._create_plan(task, planning_method, constraints, resources, max_steps)
            
            # Update state
            self.state["current_plan"]["status"] = "completed"
            self.state["plans"][task] = plan
            
            return {
                "success": True,
                "task": task,
                "plan": plan,
                "planning_method": planning_method,
                "step_count": len(plan.get("steps", [])),
                "estimated_duration": plan.get("estimated_duration", "")
            }
        except Exception as e:
            logger.error(f"Error creating plan: {str(e)}")
            
            # Update state
            self.state["current_plan"]["status"] = "failed"
            self.state["current_plan"]["error"] = str(e)
            
            return {
                "success": False,
                "error": str(e),
                "task": task,
                "planning_method": planning_method
            }
    
    async def _create_plan(self, 
                         task: str, 
                         planning_method: str, 
                         constraints: List[str], 
                         resources: List[str], 
                         max_steps: int) -> Dict[str, Any]:
        """
        Create a plan for a task using the specified method.
        
        Args:
            task: The task description
            planning_method: The planning method to use
            constraints: List of constraints to consider
            resources: List of available resources
            max_steps: Maximum number of steps in the plan
            
        Returns:
            A dictionary containing the plan
        """
        if planning_method == "sequential":
            return await self._create_sequential_plan(task, constraints, resources, max_steps)
        elif planning_method == "hierarchical":
            return await self._create_hierarchical_plan(task, constraints, resources, max_steps)
        else:
            raise ValueError(f"Unsupported planning method: {planning_method}")
    
    async def _create_sequential_plan(self, 
                                    task: str, 
                                    constraints: List[str], 
                                    resources: List[str], 
                                    max_steps: int) -> Dict[str, Any]:
        """
        Create a sequential plan for a task.
        
        Args:
            task: The task description
            constraints: List of constraints to consider
            resources: List of available resources
            max_steps: Maximum number of steps in the plan
            
        Returns:
            A dictionary containing the sequential plan
        """
        # This would typically use an LLM to generate a plan
        # For now, return a placeholder plan
        steps = []
        for i in range(min(5, max_steps)):
            steps.append({
                "step_number": i + 1,
                "description": f"Step {i + 1} for task: {task}",
                "estimated_duration": "1 hour",
                "resources_needed": resources[:1] if resources else [],
                "dependencies": [i] if i > 0 else []
            })
        
        return {
            "task": task,
            "type": "sequential",
            "steps": steps,
            "constraints_addressed": constraints,
            "resources_required": resources,
            "estimated_duration": f"{len(steps)} hours",
            "success_criteria": f"Completion of all steps for: {task}"
        }
    
    async def _create_hierarchical_plan(self, 
                                      task: str, 
                                      constraints: List[str], 
                                      resources: List[str], 
                                      max_steps: int) -> Dict[str, Any]:
        """
        Create a hierarchical plan for a task.
        
        Args:
            task: The task description
            constraints: List of constraints to consider
            resources: List of available resources
            max_steps: Maximum number of steps in the plan
            
        Returns:
            A dictionary containing the hierarchical plan
        """
        # This would typically use an LLM to generate a hierarchical plan
        # For now, return a placeholder plan
        main_steps = []
        for i in range(min(3, max_steps)):
            substeps = []
            for j in range(2):
                substeps.append({
                    "step_number": j + 1,
                    "description": f"Substep {j + 1} for main step {i + 1}: {task}",
                    "estimated_duration": "30 minutes",
                    "resources_needed": resources[:1] if resources else [],
                    "dependencies": [j] if j > 0 else []
                })
            
            main_steps.append({
                "step_number": i + 1,
                "description": f"Main step {i + 1} for task: {task}",
                "estimated_duration": "1 hour",
                "resources_needed": resources[:1] if resources else [],
                "dependencies": [i] if i > 0 else [],
                "substeps": substeps
            })
        
        return {
            "task": task,
            "type": "hierarchical",
            "main_steps": main_steps,
            "constraints_addressed": constraints,
            "resources_required": resources,
            "estimated_duration": f"{len(main_steps) * 2} hours",
            "success_criteria": f"Completion of all main steps and substeps for: {task}"
        }
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities supported by this agent.
        
        Returns:
            A list of capability names
        """
        return ["planning", "sequential_planning", "hierarchical_planning", "task_breakdown"]