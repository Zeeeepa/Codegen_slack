"""
Agent orchestrator for coordinating multiple agents.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple

from agents.base_agent import BaseAgent
from agents.agent_factory import AgentFactory

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Orchestrator for coordinating multiple agents.
    
    This class manages a collection of agents and coordinates their interactions
    to solve complex tasks that require multiple agents working together.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new orchestrator.
        
        Args:
            config: Optional configuration parameters
        """
        self.config = config or {}
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, Dict[str, Any]] = {}
        
    async def add_agent(self, agent_id: str, agent: BaseAgent) -> None:
        """
        Add an agent to the orchestrator.
        
        Args:
            agent_id: A unique identifier for the agent
            agent: The agent instance to add
        """
        self.agents[agent_id] = agent
        await agent.initialize()
        logger.info(f"Added agent: {agent_id} ({agent.name})")
        
    async def remove_agent(self, agent_id: str) -> None:
        """
        Remove an agent from the orchestrator.
        
        Args:
            agent_id: The identifier of the agent to remove
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            await agent.cleanup()
            del self.agents[agent_id]
            logger.info(f"Removed agent: {agent_id}")
        
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by its identifier.
        
        Args:
            agent_id: The agent identifier
            
        Returns:
            The agent instance, or None if not found
        """
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> Dict[str, BaseAgent]:
        """
        Get all registered agents.
        
        Returns:
            A dictionary mapping agent IDs to agent instances
        """
        return self.agents
    
    async def process_task(self, 
                          task_data: Dict[str, Any], 
                          workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a task using a workflow of agents.
        
        Args:
            task_data: The task data to process
            workflow_id: Optional workflow identifier to use
            
        Returns:
            The processing result
        """
        if workflow_id and workflow_id in self.workflows:
            return await self._execute_workflow(workflow_id, task_data)
        
        # If no workflow specified, use the default agent (if any)
        if "default_agent" in self.config:
            default_agent_id = self.config["default_agent"]
            if default_agent_id in self.agents:
                agent = self.agents[default_agent_id]
                return await agent.process(task_data)
        
        raise ValueError("No workflow or default agent specified")
    
    async def _execute_workflow(self, workflow_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow with the given task data.
        
        Args:
            workflow_id: The workflow identifier
            task_data: The task data to process
            
        Returns:
            The workflow result
        """
        workflow = self.workflows[workflow_id]
        steps = workflow.get("steps", [])
        context = {"input": task_data, "workflow_id": workflow_id}
        
        for step in steps:
            step_type = step.get("type")
            
            if step_type == "agent":
                agent_id = step.get("agent_id")
                if agent_id not in self.agents:
                    raise ValueError(f"Unknown agent: {agent_id}")
                
                agent = self.agents[agent_id]
                input_mapping = step.get("input_mapping", {})
                
                # Map inputs from context to agent input
                agent_input = {}
                for agent_key, context_key in input_mapping.items():
                    if context_key in context:
                        agent_input[agent_key] = context[context_key]
                
                # Process with the agent
                result = await agent.process(agent_input, context)
                
                # Update context with the result
                output_mapping = step.get("output_mapping", {})
                for context_key, result_key in output_mapping.items():
                    if result_key in result:
                        context[context_key] = result[result_key]
            
            elif step_type == "condition":
                condition = step.get("condition")
                if_steps = step.get("if_steps", [])
                else_steps = step.get("else_steps", [])
                
                # Evaluate the condition
                condition_met = self._evaluate_condition(condition, context)
                
                # Execute the appropriate steps
                if condition_met:
                    for if_step in if_steps:
                        # Recursive execution of substeps
                        pass
                else:
                    for else_step in else_steps:
                        # Recursive execution of substeps
                        pass
        
        # Return the final context as the result
        return context
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition against the current context.
        
        Args:
            condition: The condition to evaluate
            context: The current context
            
        Returns:
            True if the condition is met, False otherwise
        """
        # Simple condition evaluation logic
        operator = condition.get("operator", "eq")
        left = condition.get("left")
        right = condition.get("right")
        
        # Resolve variables from context
        if isinstance(left, str) and left.startswith("$"):
            var_name = left[1:]
            left = context.get(var_name)
        
        if isinstance(right, str) and right.startswith("$"):
            var_name = right[1:]
            right = context.get(var_name)
        
        # Evaluate the condition
        if operator == "eq":
            return left == right
        elif operator == "neq":
            return left != right
        elif operator == "gt":
            return left > right
        elif operator == "lt":
            return left < right
        elif operator == "contains":
            return right in left
        
        return False
    
    def register_workflow(self, workflow_id: str, workflow: Dict[str, Any]) -> None:
        """
        Register a workflow with the orchestrator.
        
        Args:
            workflow_id: A unique identifier for the workflow
            workflow: The workflow definition
        """
        self.workflows[workflow_id] = workflow
        logger.info(f"Registered workflow: {workflow_id}")
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a workflow by its identifier.
        
        Args:
            workflow_id: The workflow identifier
            
        Returns:
            The workflow definition, or None if not found
        """
        return self.workflows.get(workflow_id)
    
    def get_all_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered workflows.
        
        Returns:
            A dictionary mapping workflow IDs to workflow definitions
        """
        return self.workflows