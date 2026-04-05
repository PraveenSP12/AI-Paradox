from mcp.server.fastmcp import FastMCP
import sqlite3

# Initialize the MCP Server
mcp = FastMCP("Nexus_MCP_Server")

# Initialize Local Database
conn = sqlite3.connect("paradox.db", check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, description TEXT, status TEXT)")
conn.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, description TEXT, priority TEXT, status TEXT)")
conn.commit()

# Update the tool to accept priority
@mcp.tool()
def add_task(description: str, priority: str = "Medium") -> str:
    """Task Manager Tool: Add a new actionable task with a priority level."""
    conn.execute("INSERT INTO tasks (description, priority, status) VALUES (?, ?, 'PENDING')", (description, priority))
    conn.commit()
    return f"Success: Task '{description}' added with {priority} priority."
    
@mcp.tool()
def add_task(description: str) -> str:
    """Task Manager Tool: Add a new actionable task to the database."""
    conn.execute("INSERT INTO tasks (description, status) VALUES (?, 'PENDING')", (description,))
    conn.commit()
    return f"Success: Task '{description}' added."

@mcp.tool()
def add_note(content: str) -> str:
    """Notes Tool: Save a raw idea, summary, or note to the database."""
    conn.execute("INSERT INTO notes (content) VALUES (?)", (content,))
    conn.commit()
    return f"Success: Note saved."

@mcp.tool()
def schedule_event(title: str, time: str) -> str:
    """Calendar Tool: Schedule a calendar event."""
    return f"Success: Scheduled '{title}' at {time} in your Calendar."

if __name__ == "__main__":
    mcp.run_stdio()