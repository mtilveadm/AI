"""DevOps ChatBot agent to help Engineering with their asks"""

from google.adk.agents import Agent
from bitbucket import prompt
from bitbucket.sub_agents.deployment import deployment_agent

print("[DEBUG] Loading root_agent from agent.py...")
root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="DevOps agent helping Engineering team for their tasks",
    instruction=prompt.ROOT_AGENT_INSTR,
    sub_agents=[
        deployment_agent,
    ]
)
print("[DEBUG] root_agent created and ready.")
