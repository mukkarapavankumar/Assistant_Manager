"""
Enhanced Assistant Agent with improved workflow orchestration and error handling.
Optimized for local LLM usage with simple, reliable tool patterns.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.tools import BaseTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage

from app.tools.email_tools import EmailTools
from app.tools.kanban_tools import KanbanTools
from app.tools.analysis_tools import AnalysisTools
from app.tools.git_tools import GitTools
from app.services.llm_service import LLMService
from app.models.database import AgentState as AgentStateModel
from app.core.config import settings

logger = logging.getLogger(__name__)

class AgentState:
    """Enhanced state management for the assistant agent."""
    
    def __init__(self):
        self.current_workflow: Optional[str] = None
        self.active_tasks: List[Dict] = []
        self.pending_approvals: List[Dict] = []
        self.last_activity: datetime = datetime.now()
        self.context: Dict[str, Any] = {}
        self.messages: List[BaseMessage] = []
        self.error_count: int = 0
        self.last_error: Optional[str] = None
        self.workflow_step: str = "idle"
    
    def add_error(self, error: str):
        """Track errors for debugging and recovery."""
        self.error_count += 1
        self.last_error = error
        self.last_activity = datetime.now()
        logger.warning(f"Agent error #{self.error_count}: {error}")
    
    def reset_errors(self):
        """Reset error tracking after successful operation."""
        self.error_count = 0
        self.last_error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for persistence."""
        return {
            "current_workflow": self.current_workflow,
            "active_tasks": self.active_tasks,
            "pending_approvals": self.pending_approvals,
            "last_activity": self.last_activity.isoformat(),
            "context": self.context,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "workflow_step": self.workflow_step,
            "messages": [
                {
                    "type": type(msg).__name__,
                    "content": msg.content
                } for msg in self.messages[-10:]  # Keep only last 10 messages
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentState':
        """Create state from dictionary."""
        state = cls()
        state.current_workflow = data.get("current_workflow")
        state.active_tasks = data.get("active_tasks", [])
        state.pending_approvals = data.get("pending_approvals", [])
        state.last_activity = datetime.fromisoformat(data.get("last_activity", datetime.now().isoformat()))
        state.context = data.get("context", {})
        state.error_count = data.get("error_count", 0)
        state.last_error = data.get("last_error")
        state.workflow_step = data.get("workflow_step", "idle")
        
        # Reconstruct messages
        messages_data = data.get("messages", [])
        state.messages = []
        for msg_data in messages_data:
            if msg_data["type"] == "HumanMessage":
                state.messages.append(HumanMessage(content=msg_data["content"]))
            elif msg_data["type"] == "AIMessage":
                state.messages.append(AIMessage(content=msg_data["content"]))
        
        return state

class AssistantAgent:
    """
    Enhanced Assistant Agent with improved error handling and workflow orchestration.
    Optimized for local LLM usage with simple, reliable operations.
    """
    
    def __init__(self):
        self.llm_service = LLMService()
        self.email_tools = EmailTools()
        self.kanban_tools = KanbanTools()
        self.analysis_tools = AnalysisTools()
        self.git_tools = GitTools()
        
        self.state = AgentState()
        self.is_active = False
        self.graph = None
        self.checkpointer = None
        
        # Simple tool registry for better LLM integration
        self.tool_registry = {}
        
        # Workflow timeout settings
        self.workflow_timeout = 300  # 5 minutes
        self.max_retries = 3
    
    async def initialize(self):
        """Initialize the agent and its components with enhanced error handling."""
        try:
            logger.info("Initializing Assistant Agent...")
            
            # Initialize LLM service first (most critical)
            await self.llm_service.initialize()
            
            # Initialize tools with error handling
            await self._initialize_tools()
            
            # Setup workflow graph
            await self._setup_workflow()
            
            # Load persisted state
            await self._load_state()
            
            self.is_active = True
            logger.info("Assistant Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Assistant Agent: {e}")
            self.is_active = False
            # Don't raise - allow partial functionality
    
    async def _initialize_tools(self):
        """Initialize tools with individual error handling."""
        tools_to_init = [
            ("email_tools", self.email_tools),
            ("kanban_tools", self.kanban_tools),
            ("analysis_tools", self.analysis_tools),
            ("git_tools", self.git_tools)
        ]
        
        for tool_name, tool in tools_to_init:
            try:
                await tool.initialize()
                logger.info(f"Initialized {tool_name}")
            except Exception as e:
                logger.error(f"Failed to initialize {tool_name}: {e}")
                # Continue with other tools
        
        # Register simple tools for LLM usage
        self._register_simple_tools()
    
    def _register_simple_tools(self):
        """Register simplified tools for better LLM integration."""
        self.tool_registry = {
            # Email tools
            "send_update_emails": self._simple_send_emails,
            "check_email_responses": self._simple_check_responses,
            "parse_email": self._simple_parse_email,
            
            # Kanban tools
            "get_board_status": self._simple_board_status,
            "create_task": self._simple_create_task,
            "update_task": self._simple_update_task,
            "find_tasks": self._simple_find_tasks,
            
            # Analysis tools
            "analyze_team": self._simple_analyze_team,
            "generate_report": self._simple_generate_report,
            
            # Git tools
            "publish_to_github": self._simple_publish_github,
            "check_github_status": self._simple_github_status,
        }
    
    async def _setup_workflow(self):
        """Setup simplified workflow graph."""
        try:
            # Create checkpointer for state persistence
            self.checkpointer = SqliteSaver.from_conn_string("assistant_agent_checkpoints.db")
            
            # Define simplified workflow
            workflow = StateGraph(AgentState)
            
            # Add workflow nodes
            workflow.add_node("analyze_request", self._analyze_request)
            workflow.add_node("execute_action", self._execute_action)
            workflow.add_node("handle_result", self._handle_result)
            workflow.add_node("update_state", self._update_state)
            
            # Define simple linear flow with error handling
            workflow.add_edge("analyze_request", "execute_action")
            workflow.add_edge("execute_action", "handle_result")
            workflow.add_edge("handle_result", "update_state")
            workflow.add_edge("update_state", END)
            
            # Set entry point
            workflow.set_entry_point("analyze_request")
            
            # Compile graph
            self.graph = workflow.compile(checkpointer=self.checkpointer)
            
            logger.info("Simplified workflow graph setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup workflow: {e}")
            # Create minimal fallback
            self.graph = None
    
    async def _analyze_request(self, state: AgentState) -> AgentState:
        """Analyze incoming requests with simple pattern matching."""
        try:
            state.workflow_step = "analyzing"
            
            if not state.messages:
                state.context["action"] = "status_check"
                return state
            
            latest_message = state.messages[-1].content.lower()
            
            # Simple keyword-based analysis (more reliable than LLM for local models)
            if any(word in latest_message for word in ['email', 'send', 'update', 'request']):
                state.context["action"] = "send_emails"
            elif any(word in latest_message for word in ['response', 'reply', 'check', 'monitor']):
                state.context["action"] = "check_responses"
            elif any(word in latest_message for word in ['task', 'create', 'add']):
                state.context["action"] = "create_task"
            elif any(word in latest_message for word in ['status', 'summary', 'report']):
                state.context["action"] = "generate_report"
            elif any(word in latest_message for word in ['kanban', 'board']):
                state.context["action"] = "board_status"
            elif any(word in latest_message for word in ['github', 'publish', 'sync', 'pages']):
                state.context["action"] = "publish_to_github"
            else:
                state.context["action"] = "general_query"
            
            state.last_activity = datetime.now()
            logger.info(f"Analyzed request: action={state.context['action']}")
            
        except Exception as e:
            state.add_error(f"Error analyzing request: {str(e)}")
            state.context["action"] = "error"
        
        return state
    
    async def _execute_action(self, state: AgentState) -> AgentState:
        """Execute the determined action with error handling."""
        try:
            state.workflow_step = "executing"
            action = state.context.get("action", "status_check")
            
            # Execute action using simple tool registry
            if action in self.tool_registry:
                result = await self.tool_registry[action](state)
                state.context["result"] = result
                state.context["success"] = True
            else:
                # Fallback for unknown actions
                result = await self._handle_general_query(state)
                state.context["result"] = result
                state.context["success"] = True
            
            state.reset_errors()  # Reset error count on success
            
        except Exception as e:
            error_msg = f"Error executing action '{action}': {str(e)}"
            state.add_error(error_msg)
            state.context["result"] = f"Failed to execute action: {str(e)}"
            state.context["success"] = False
        
        return state
    
    async def _handle_result(self, state: AgentState) -> AgentState:
        """Handle the result of action execution."""
        try:
            state.workflow_step = "handling_result"
            
            result = state.context.get("result", "No result")
            success = state.context.get("success", False)
            
            if success:
                # Create AI response message
                response_msg = AIMessage(content=result)
                state.messages.append(response_msg)
                
                # Update activity tracking
                state.active_tasks.append({
                    "type": "action_completed",
                    "action": state.context.get("action"),
                    "timestamp": datetime.now().isoformat(),
                    "result": result[:200]  # Truncate for storage
                })
            else:
                # Handle error case
                error_response = f"I encountered an issue: {result}"
                response_msg = AIMessage(content=error_response)
                state.messages.append(response_msg)
            
        except Exception as e:
            state.add_error(f"Error handling result: {str(e)}")
        
        return state
    
    async def _update_state(self, state: AgentState) -> AgentState:
        """Update final state and persist."""
        try:
            state.workflow_step = "completed"
            state.last_activity = datetime.now()
            
            # Save state to database
            await self._save_state()
            
        except Exception as e:
            state.add_error(f"Error updating state: {str(e)}")
        
        return state
    
    # Simple tool implementations for better LLM integration
    
    async def _simple_send_emails(self, state: AgentState) -> str:
        """Simple email sending tool."""
        try:
            team_members = await self.email_tools.get_active_team_members()
            if not team_members:
                return "No active team members found to send emails to."
            
            emails = [member['email'] for member in team_members]
            result = await self.email_tools.send_team_update_request.ainvoke({
                "team_members": emails,
                "template": "weekly_update",
                "subject": f"Weekly Update Request - {datetime.now().strftime('%B %d, %Y')}"
            })
            
            return f"Sent update requests to {len(emails)} team members: {result}"
            
        except Exception as e:
            return f"Error sending emails: {str(e)}"
    
    async def _simple_check_responses(self, state: AgentState) -> str:
        """Simple response checking tool."""
        try:
            since_time = datetime.now() - timedelta(hours=24)
            responses = await self.email_tools.monitor_inbox_responses.ainvoke({
                "since_timestamp": since_time
            })
            
            if not responses:
                return "No new email responses found in the last 24 hours."
            
            # Process responses
            processed_count = 0
            for response in responses:
                try:
                    parsed_data = await self.email_tools.parse_email_content.ainvoke({
                        "email_content": response["content"]
                    })
                    
                    if parsed_data and parsed_data.get('task_title'):
                        processed_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing response: {e}")
                    continue
            
            return f"Found {len(responses)} new responses, processed {processed_count} successfully."
            
        except Exception as e:
            return f"Error checking responses: {str(e)}"
    
    async def _simple_parse_email(self, state: AgentState) -> str:
        """Simple email parsing tool."""
        try:
            # This would be called with specific email content
            # For now, return a status message
            return "Email parsing functionality is available."
        except Exception as e:
            return f"Error in email parsing: {str(e)}"
    
    async def _simple_board_status(self, state: AgentState) -> str:
        """Simple board status tool."""
        try:
            result = await self.kanban_tools.get_board_summary.ainvoke({})
            return result
        except Exception as e:
            return f"Error getting board status: {str(e)}"
    
    async def _simple_create_task(self, state: AgentState) -> str:
        """Simple task creation tool."""
        try:
            # Extract task info from message if possible
            message = state.messages[-1].content if state.messages else ""
            
            # For now, return instruction for manual task creation
            return "To create a task, please use the kanban board interface or provide specific task details."
        except Exception as e:
            return f"Error creating task: {str(e)}"
    
    async def _simple_update_task(self, state: AgentState) -> str:
        """Simple task update tool."""
        try:
            return "Task update functionality is available through the kanban board."
        except Exception as e:
            return f"Error updating task: {str(e)}"
    
    async def _simple_find_tasks(self, state: AgentState) -> str:
        """Simple task finding tool."""
        try:
            result = await self.kanban_tools.find_tasks.ainvoke({
                "search_term": state.messages[-1].content if state.messages else ""
            })
            return result
        except Exception as e:
            return f"Error finding tasks: {str(e)}"
    
    async def _simple_analyze_team(self, state: AgentState) -> str:
        """Simple team analysis tool."""
        try:
            team_members = await self.email_tools.get_active_team_members()
            active_count = len(team_members)
            
            # Get basic stats
            total_response_rate = sum(member.get('response_rate', 0) for member in team_members)
            avg_response_rate = total_response_rate / active_count if active_count > 0 else 0
            
            return f"Team Analysis: {active_count} active members, average response rate: {avg_response_rate:.1f}%"
            
        except Exception as e:
            return f"Error analyzing team: {str(e)}"
    
    async def _simple_generate_report(self, state: AgentState) -> str:
        """Simple report generation tool."""
        try:
            # Get board summary
            board_summary = await self.kanban_tools.get_board_summary.ainvoke({})
            
            # Get team info
            team_info = await self._simple_analyze_team(state)
            
            # Combine into simple report
            report = f"Status Report:\n\n{board_summary}\n\n{team_info}"
            
            return report
            
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    async def _simple_publish_github(self, state: AgentState) -> str:
        """Simple GitHub publishing tool."""
        try:
            result = await self.git_tools.publish_kanban_to_github.ainvoke({})
            return result
        except Exception as e:
            return f"Error publishing to GitHub: {str(e)}"
    
    async def _simple_github_status(self, state: AgentState) -> str:
        """Simple GitHub status check tool."""
        try:
            result = await self.git_tools.get_github_status.ainvoke({})
            return result
        except Exception as e:
            return f"Error checking GitHub status: {str(e)}"
    
    async def _handle_general_query(self, state: AgentState) -> str:
        """Handle general queries with LLM if available."""
        try:
            if not state.messages:
                return "Hello! I'm your Assistant Manager. How can I help you today?"
            
            query = state.messages[-1].content
            
            # Try to use LLM for general queries
            if self.llm_service.is_available:
                context_info = {
                    "active_tasks": len(state.active_tasks),
                    "pending_approvals": len(state.pending_approvals),
                    "last_activity": state.last_activity.isoformat()
                }
                
                prompt = f"""You are an assistant manager AI. Answer this query briefly and helpfully:

Query: {query}

Context: {json.dumps(context_info)}

Response:"""
                
                response = await self.llm_service.generate_simple_response(prompt, max_tokens=200)
                return response
            else:
                # Fallback response
                return "I understand your query. The LLM service is currently unavailable, but I can help with email management, kanban board updates, team status queries, and GitHub publishing."
                
        except Exception as e:
            return f"I encountered an issue processing your query: {str(e)}"
    
    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process a message through the simplified agent workflow."""
        try:
            # Add message to state
            self.state.messages.append(HumanMessage(content=message))
            
            if context:
                self.state.context.update(context)
            
            # Execute workflow with timeout
            if self.graph:
                config = {"configurable": {"thread_id": "main"}}
                
                # Use asyncio.wait_for for timeout
                result = await asyncio.wait_for(
                    self.graph.ainvoke(self.state, config=config),
                    timeout=self.workflow_timeout
                )
                
                # Return the last AI message
                if result.messages and isinstance(result.messages[-1], AIMessage):
                    return result.messages[-1].content
                else:
                    return "Workflow completed successfully"
            else:
                # Fallback processing without graph
                return await self._fallback_processing(message)
                
        except asyncio.TimeoutError:
            error_msg = "Workflow timed out. Please try again."
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    async def _fallback_processing(self, message: str) -> str:
        """Fallback message processing when workflow graph is unavailable."""
        try:
            # Simple keyword-based processing
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['status', 'summary']):
                return await self._simple_generate_report(self.state)
            elif any(word in message_lower for word in ['email', 'send']):
                return await self._simple_send_emails(self.state)
            elif any(word in message_lower for word in ['kanban', 'board']):
                return await self._simple_board_status(self.state)
            elif any(word in message_lower for word in ['github', 'publish', 'sync']):
                return await self._simple_publish_github(self.state)
            else:
                return "I'm operating in fallback mode. I can help with status reports, sending emails, kanban board updates, and GitHub publishing."
                
        except Exception as e:
            return f"Error in fallback processing: {str(e)}"
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status with health information."""
        try:
            # Get LLM health
            llm_health = await self.llm_service.health_check()
            
            return {
                "is_active": self.is_active,
                "current_workflow": self.state.current_workflow,
                "workflow_step": self.state.workflow_step,
                "active_tasks": len(self.state.active_tasks),
                "pending_approvals": len(self.state.pending_approvals),
                "last_activity": self.state.last_activity.isoformat(),
                "error_count": self.state.error_count,
                "last_error": self.state.last_error,
                "llm_status": llm_health["status"],
                "context": self.state.context
            }
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return {
                "is_active": False,
                "error": str(e)
            }
    
    async def _save_state(self):
        """Save agent state to database with error handling."""
        try:
            state_data = self.state.to_dict()
            
            # Update or create state record
            AgentStateModel.replace(
                state_key="main_agent_state",
                state_data=json.dumps(state_data)
            ).execute()
            
        except Exception as e:
            logger.error(f"Error saving agent state: {e}")
    
    async def _load_state(self):
        """Load agent state from database with error handling."""
        try:
            state_record = AgentStateModel.get_or_none(
                AgentStateModel.state_key == "main_agent_state"
            )
            
            if state_record:
                state_data = json.loads(state_record.state_data)
                self.state = AgentState.from_dict(state_data)
                logger.info("Agent state loaded from database")
            else:
                logger.info("No previous agent state found, starting fresh")
                
        except Exception as e:
            logger.error(f"Error loading agent state: {e}")
            # Continue with fresh state
    
    async def cleanup(self):
        """Cleanup agent resources."""
        try:
            await self._save_state()
            await self.llm_service.cleanup()
            
            # Cleanup tools
            if hasattr(self.email_tools, 'cleanup'):
                await self.email_tools.cleanup()
            
            self.is_active = False
            logger.info("Assistant Agent cleanup completed")
        except Exception as e:
            logger.error(f"Error during agent cleanup: {e}")