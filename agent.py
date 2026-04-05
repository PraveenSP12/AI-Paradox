import os
import asyncio
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.tool_context import ToolContext
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# --- Setup ---
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()
load_dotenv()
model_name = os.getenv("MODEL", "gemini-2.5-flash")

# --- 1. State Management Tool ---
def add_prompt_to_state(tool_context: ToolContext, prompt: str) -> dict[str, str]:
    """Saves the user's initial brain-dump to the state."""
    tool_context.state["PROMPT"] = prompt
    return {"status": "success"}

# --- 2. MCP Client Execution Helper ---
def execute_mcp_tool(tool_name: str, args: dict) -> str:
    """Connects to the local FastMCP server and executes a tool."""
    async def run():
        server_params = StdioServerParameters(command="python", args=["nexus_mcp.py"])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments=args)
                # MCP results are lists of text contents, we extract the text
                return str(result.content[0].text)
    return asyncio.run(run())

# --- 3. ADK Tools (Wrappers for MCP) ---
def mcp_task_tool(description: str, priority: str) -> str:
    """Use this tool to add a task to the task manager. Priority must be High, Medium, or Low."""
    return execute_mcp_tool("add_task", {"description": description, "priority": priority})

def mcp_note_tool(content: str) -> str:
    """Use this tool to save a note or idea."""
    return execute_mcp_tool("add_note", {"content": content})

def mcp_calendar_tool(title: str, time: str) -> str:
    """Use this tool to schedule a calendar event."""
    return execute_mcp_tool("schedule_event", {"title": title, "time": time})

# --- 4. The Sub-Agents ---

# Agent A: The Analyzer and Executor
triage_agent = Agent(
    name="triage_agent",
    model=model_name,
    description="Analyzes the brain-dump and executes MCP tools.",
    instruction="""
    You are the core of AI Paradox. Analyze the user's PROMPT.
    Use your tools to route the information:
    1. If there is an actionable to-do, use the 'mcp_task_tool'.
    2. If there is a general idea to remember, use the 'mcp_note_tool'.
    3. If there is a meeting or time-based event, use the 'mcp_calendar_tool'.
    
    Execute all necessary tools. Return a raw list of the actions you took.
    
    PROMPT:
    { PROMPT }
    """,
    tools=[mcp_task_tool, mcp_note_tool, mcp_calendar_tool],
    output_key="execution_results"
)


# New Agent 1: The Wellness Protector
wellness_agent = Agent(
    name="wellness_agent",
    model=model_name,
    description="Analyzes user stress levels and injects wellness breaks.",
    instruction="""
    Analyze the user's PROMPT. 
    1. If the user sounds overwhelmed, rushed, or lists more than 4 tasks, add a note to the data: "USER IS STRESSED - Inject a 15-minute mandatory break task."
    2. If the user sounds calm, just pass the original prompt through.
    Output the refined analysis for the next agent.
    
    PROMPT:
    { PROMPT }
    """,
    output_key="wellness_context"
)

# New Agent 2: The Project Manager
project_manager_agent = Agent(
    name="project_manager",
    model=model_name,
    description="Breaks down massive goals into micro-tasks.",
    instruction="""
    Look at the original PROMPT and the WELLNESS_CONTEXT.
    If the user mentions a massive, multi-step goal (e.g., 'start a business', 'plan a vacation'), break it down into 2 to 3 specific, small, actionable micro-tasks. 
    Output a revised, highly structured list of all tasks, notes, and events that need to be processed.
    
    PROMPT: { PROMPT }
    WELLNESS_CONTEXT: { wellness_context }
    """,
    output_key="structured_agenda"
)

# --- 3. Update the Triage Agent ---
# (We update the Triage agent to use the Eisenhower prioritization)
triage_agent = Agent(
    name="triage_agent",
    model=model_name,
    description="Analyzes the structured agenda, assigns priorities, and executes MCP tools.",
    instruction="""
    You receive a STRUCTURED_AGENDA. You must execute tools to save this data.
    
    CRITICAL RULE FOR TASKS: You must act as the 'Eisenhower Prioritizer'. Evaluate every task:
    - If it's urgent/time-sensitive: Assign "High" priority.
    - If it's standard: Assign "Medium" priority.
    - If it's a "someday" goal: Assign "Low" priority.
    
    Use `mcp_task_tool` for tasks, `mcp_note_tool` for ideas, and `mcp_calendar_tool` for events.
    Return a list of what you executed.
    
    STRUCTURED_AGENDA:
    { structured_agenda }
    """,
    tools=[mcp_task_tool, mcp_note_tool, mcp_calendar_tool],
    output_key="execution_results"
)

# Agent B: The Response Formatter
response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Synthesizes the tool execution results into a clean response.",
    instruction="""
    You are AI Paradox's user interface voice. 
    Review the EXECUTION_RESULTS and write a clean, friendly summary for the user confirming what tasks were logged, what notes were saved, and what events were scheduled.

    EXECUTION_RESULTS:
    { execution_results }
    """
)

# --- 5. Workflows ---
paradox_workflow = SequentialAgent(
    name="paradox_workflow",
    description="Main workflow for triaging a brain-dump with advanced reasoning.",
    sub_agents=[
        wellness_agent,         # Step 1: Check mental load
        project_manager_agent,  # Step 2: Break down big goals
        triage_agent,           # Step 3: Assign priority and execute tools
        response_formatter      # Step 4: Write the friendly summary
    ]
)

root_agent = Agent(
    name="greeter",
    model=model_name,
    description="The main entry point.",
    instruction="""
    Let the user know you are AI Paradox.
    When the user sends a brain-dump, use 'add_prompt_to_state' to save it.
    After using the tool, transfer control to the 'paradox_workflow' agent.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[paradox_workflow]
)