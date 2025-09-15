from google.adk.agents import Agent

from bitbucket import prompt
import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env

from bitbucket.tools.bb_deployment import deploy_pipeline_tool
from bitbucket.tools.bb_deployment import list_deployment_environments_tool

deployment_agent = Agent(
    model="gemini-2.5-flash",
    name="deployment_agent",
    description="Deployment agent takes repo name and environment name from root_agent to perform deployment to non-production environments",
    instruction=prompt.DEPLOYMENT_AGENT_PROMPT,
    tools=[deploy_pipeline_tool, list_deployment_environments_tool]
)