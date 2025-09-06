"""
Travel Agent - LangChain Implementation with Chain-of-Thought Reasoning

A sophisticated travel assistant that uses:
- Gemini 2.5 Flash with function calling and grounding
- Chain-of-thought prompting for multi-step reasoning
- Weather and search tools integration
- Natural conversation flow with context awareness
"""

import os
import asyncio
from typing import Dict, Any, List
import requests
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.runnables import RunnableConfig

# Import Google AI Tool for grounding
try:
    from google.ai.generativelanguage_v1beta.types import Tool as GenAITool
except ImportError:
    GenAITool = None
from app.prompts.travel_prompts import (
    TRAVEL_AGENT_SYSTEM_PROMPT,
    ERROR_MESSAGES,
    CONVERSATION_STARTERS
)
from app.tools.weather_info import WEATHER_TOOLS

class TravelAgent:
    """
    Advanced Travel Assistant powered by LangChain and Gemini 2.5 Flash
    
    Features:
    - Chain-of-thought reasoning for complex travel planning
    - Real-time weather data integration
    - Intelligent conversation memory management
    - Natural language tool calling
    - Context-aware recommendations
    """
    
    def __init__(self):
        # Initialize Gemini 2.5 Flash with optimized settings and Google Search grounding
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7,  # Balanced creativity and consistency
            max_tokens=4000,  # Allow for detailed responses
            top_p=0.9       # Good diversity
        )
        
        # Use weather tool from the separate tools module
        self.tools = WEATHER_TOOLS
        
        # Prepare Google Search grounding tools for enhanced information retrieval
        self.grounding_tools = []
        if GenAITool:
            try:
                # Add Google Search grounding capability
                self.grounding_tools = [GenAITool(google_search={})]
                print("✅ Google Search grounding enabled")
            except Exception as e:
                print(f"⚠️ Google Search grounding not available: {e}")
        
        # Bind tools to the model for function calling
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Create the agent with chain-of-thought prompt
        self.agent = self._create_agent()
    
    def _create_agent(self):
        """Create the LangChain agent with chain-of-thought prompting"""
        
        # Use the sophisticated system prompt from the prompts module
        system_prompt = TRAVEL_AGENT_SYSTEM_PROMPT

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ])
        
        # Create the tool-calling agent
        agent = create_tool_calling_agent(self.llm_with_tools, self.tools, prompt)
        
        # Create agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
        )
        
        return agent_executor
    
    async def process_message(self, message: str, memory: ConversationSummaryBufferMemory, session_id: str) -> str:
        """
        Process a user message through the travel agent with Google Search grounding
        
        Args:
            message: User's message
            memory: Conversation memory for the session
            session_id: Session identifier
            
        Returns:
            Agent's response
        """
        try:
            # Get chat history from memory
            chat_history = memory.chat_memory.messages
            
            # Check if this query might benefit from Google Search grounding
            search_keywords = ["current", "latest", "recent", "news", "events", "2025", "2024", 
                             "what happened", "when is", "where is", "who won", "best places",
                             "attractions", "restaurants", "hotels", "flights"]
            
            needs_grounding = any(keyword.lower() in message.lower() for keyword in search_keywords)
            
            if needs_grounding and self.grounding_tools:
                # Use direct LLM call with grounding for current information queries
                try:
                    response = await asyncio.to_thread(
                        self.llm.invoke,
                        [
                            SystemMessage(content=TRAVEL_AGENT_SYSTEM_PROMPT),
                            *chat_history,
                            HumanMessage(content=message)
                        ],
                        tools=self.grounding_tools
                    )
                    agent_response = response.content
                except Exception as grounding_error:
                    print(f"Grounding failed, falling back to agent: {grounding_error}")
                    # Fallback to regular agent execution
                    response = await asyncio.to_thread(
                        self.agent.invoke,
                        {
                            "input": message,
                            "chat_history": chat_history
                        }
                    )
                    agent_response = response.get("output", "I apologize, but I encountered an issue processing your request.")
            else:
                # Use regular agent execution for other queries
                response = await asyncio.to_thread(
                    self.agent.invoke,
                    {
                        "input": message,
                        "chat_history": chat_history
                    }
                )
                agent_response = response.get("output", "I apologize, but I encountered an issue processing your request.")
            
            # Add messages to memory
            memory.chat_memory.add_user_message(message)
            memory.chat_memory.add_ai_message(agent_response)
            
            return agent_response
            
        except Exception as e:
            # Use sophisticated error messaging from prompts
            error_type = "general_error"
            if "weather" in str(e).lower():
                error_type = "weather_api_error"
            elif "search" in str(e).lower():
                error_type = "search_api_error"
            
            error_message = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["general_error"])
            error_message += f"\n\nTechnical details (for debugging): {str(e)}"
            
            # Still add to memory to maintain conversation flow
            memory.chat_memory.add_user_message(message)
            memory.chat_memory.add_ai_message(error_message)
            
            return error_message
