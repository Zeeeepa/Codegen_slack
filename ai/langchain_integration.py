"""
LangChain integration for bolt-chat.

This module provides integration with LangChain and LangGraph for building
more sophisticated agent workflows.
"""

import logging
import os
from typing import Dict, Any, List, Optional, Union, Callable

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import langgraph.graph as lg
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)

class LangChainManager:
    """
    Manager for LangChain and LangGraph integration.
    
    This class provides methods for creating and managing LangChain and LangGraph
    components for use in bolt-chat agents.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize a new LangChain manager.
        
        Args:
            config: Optional configuration parameters
        """
        self.config = config or {}
        self._llms = {}
        self._chains = {}
        self._graphs = {}
        
    def get_llm(self, 
                provider: str = "openai", 
                model_name: Optional[str] = None,
                temperature: float = 0.7,
                api_key: Optional[str] = None) -> Any:
        """
        Get a LangChain LLM instance.
        
        Args:
            provider: The provider name (openai, anthropic)
            model_name: The model name
            temperature: The temperature for generation
            api_key: Optional API key
            
        Returns:
            A LangChain LLM instance
        """
        # Use default model if not specified
        if not model_name:
            if provider == "openai":
                model_name = "gpt-4o"
            elif provider == "anthropic":
                model_name = "claude-3-opus-20240229"
            else:
                raise ValueError(f"Unknown provider: {provider}")
        
        # Create a cache key
        cache_key = f"{provider}_{model_name}_{temperature}"
        
        # Return cached LLM if available
        if cache_key in self._llms:
            return self._llms[cache_key]
        
        # Create a new LLM
        if provider == "openai":
            llm = ChatOpenAI(
                model=model_name,
                temperature=temperature,
                api_key=api_key or os.environ.get("OPENAI_API_KEY")
            )
        elif provider == "anthropic":
            llm = ChatAnthropic(
                model=model_name,
                temperature=temperature,
                api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Cache and return the LLM
        self._llms[cache_key] = llm
        return llm
    
    def create_chain(self, 
                    chain_id: str,
                    system_prompt: str,
                    human_prompt: str,
                    provider: str = "openai",
                    model_name: Optional[str] = None,
                    temperature: float = 0.7) -> Any:
        """
        Create a LangChain chain.
        
        Args:
            chain_id: A unique identifier for the chain
            system_prompt: The system prompt template
            human_prompt: The human prompt template
            provider: The provider name
            model_name: The model name
            temperature: The temperature for generation
            
        Returns:
            A LangChain chain
        """
        # Get the LLM
        llm = self.get_llm(provider, model_name, temperature)
        
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
        
        # Create the chain
        chain = prompt | llm | StrOutputParser()
        
        # Cache and return the chain
        self._chains[chain_id] = chain
        return chain
    
    def get_chain(self, chain_id: str) -> Optional[Any]:
        """
        Get a chain by its identifier.
        
        Args:
            chain_id: The chain identifier
            
        Returns:
            The chain, or None if not found
        """
        return self._chains.get(chain_id)
    
    def create_graph(self, 
                    graph_id: str,
                    nodes: Dict[str, Callable],
                    edges: Dict[str, Dict[str, str]]) -> Any:
        """
        Create a LangGraph workflow.
        
        Args:
            graph_id: A unique identifier for the graph
            nodes: A dictionary mapping node names to node functions
            edges: A dictionary mapping source nodes to target nodes
            
        Returns:
            A LangGraph workflow
        """
        # Create the graph
        workflow = StateGraph(nodes=nodes)
        
        # Add edges
        for source, targets in edges.items():
            for condition, target in targets.items():
                if condition == "default":
                    workflow.add_edge(source, target)
                else:
                    workflow.add_conditional_edges(
                        source,
                        lambda state, condition=condition, target=target: condition(state),
                        {True: target, False: END}
                    )
        
        # Compile the graph
        compiled_graph = workflow.compile()
        
        # Cache and return the graph
        self._graphs[graph_id] = compiled_graph
        return compiled_graph
    
    def get_graph(self, graph_id: str) -> Optional[Any]:
        """
        Get a graph by its identifier.
        
        Args:
            graph_id: The graph identifier
            
        Returns:
            The graph, or None if not found
        """
        return self._graphs.get(graph_id)
    
    def run_chain(self, 
                 chain_id: str, 
                 inputs: Dict[str, Any]) -> str:
        """
        Run a chain with the given inputs.
        
        Args:
            chain_id: The chain identifier
            inputs: The input data
            
        Returns:
            The chain output
        """
        chain = self.get_chain(chain_id)
        if not chain:
            raise ValueError(f"Unknown chain: {chain_id}")
        
        return chain.invoke(inputs)
    
    def run_graph(self, 
                 graph_id: str, 
                 inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a graph with the given inputs.
        
        Args:
            graph_id: The graph identifier
            inputs: The input data
            
        Returns:
            The graph output
        """
        graph = self.get_graph(graph_id)
        if not graph:
            raise ValueError(f"Unknown graph: {graph_id}")
        
        return graph.invoke(inputs)