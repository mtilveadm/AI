# This program is an example of AI Agentico Workflow developed by Mahenda Tilve.
# There will be 5 agents used as tools here, 3 agents will query message against different OpenAI LLM models such as gpt5, gpt4 & gpt3.
# We will be using OpenAI Agentic Framework to build the workflow.
# Three agents will return and 4th agent will be used to select the best answer from the three and 5the agent will send out the email.


from dotenv import load_dotenv
from agents import Agent, Runner, tool, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
import asyncio

import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()

load_dotenv(override=True)

# Defining instructions for each of 3 agents
instruction1 = "You are a news reporter agent which gives latest current news in United States of america\
    you give latest and greatest news, be professional while replying and no bias please. \
    you use openAI LLM with gpt5 to give the latest news"

instruction2 = "You are a news reporter agent which gives latest current news in United States of america\
    you give latest and greatest news, be professional while replying and no bias please. \
    you use openAI LLM with gpt4 to give the latest news"

instruction3 = "You are a news reporter agent which gives latest current news in United States of america\
    you give latest and greatest news, be professional while replying and no bias please. \
    you use openAI LLM with gpt3 to give the latest news"

instruction4 = "You are an agent and your ask is to select best news, use tool1, tool2 & tool3 to get latest news"

instruction5 = "You are an agent responsible to send email out based on the best news supplied by other tool"

# Creating agents
agent_openai_gpt5 = Agent(
    name="Open AI Agent Reporter",
    instructions=instruction1,
    model="gpt-5-nano"
)

agent_openai_gpt4 = Agent(
    name="Open AI Agent Reporter",
    instructions=instruction2,
    model="gpt-4o-mini"
)

agent_openai_gp3 = Agent(
    name="Open AI Agent Reporter",
    instructions=instruction3,
    model="gpt-3.5-turbo"
)

description = "Give me latest news from USA"

tool1 = agent_openai_gpt5.as_tool(tool_name="openai_gpt5_tool", tool_description=description)
tool2 = agent_openai_gpt4.as_tool(tool_name="openai_gpt4_tool", tool_description=description)
tool3 = agent_openai_gp3.as_tool(tool_name="openai_gpt3_tool", tool_description=description)

tools = [tool1, tool2, tool3]

# Defining my main agent which will select best news.
agent_selector = Agent(
    name="Open AI Selector Agent",
    instructions=instruction4,
    model="gpt-4o-mini",
    tools = tools
)

async def main():
    with trace("Select Best News From Main Function"):        
        result = await Runner.run(agent_selector, "Pick the best news")
        result = result.final_output
        print("\n Selected News:\n", result)


if __name__ == "__main__":
    asyncio.run(main())