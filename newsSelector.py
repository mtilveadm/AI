# This program is an example of AI Agentico Workflow developed by Mahenda Tilve.
# There will be 5 agents used as tools here, 3 agents will query message against different OpenAI LLM models such as gpt5, gpt4 & gpt3.
# We will be using OpenAI Agentic Framework to build the workflow.
# Three agents will return and 4th agent will be used to select the best answer from the three and 5the agent will send out the email.

from unicodedata import is_normalized
from dotenv import load_dotenv
from agents import Agent, GuardrailFunctionOutput, Runner, input_guardrail, tool, trace, function_tool
from openai import BaseModel
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
instruction1 = "You are a news reporter agent which gives latest current news\
    you give latest and greatest news, be professional while replying and no bias please. \
    you use openAI LLM with gpt5 to give the latest news"

instruction2 = "You are a news reporter agent which gives latest current news\
    you give latest and greatest news, be professional while replying and no bias please. \
    you use openAI LLM with gpt4 to give the latest news"

instruction3 = "You are a news reporter agent which gives latest current news\
    you give latest and greatest news, be professional while replying and no bias please. \
    you use openAI LLM with gpt3 to give the latest news"

instruction4 = "You are an agent and your task is to select best news, use tool1, tool2 & tool3 to get latest news"

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

agent_openai_gpt3 = Agent(
    name="Open AI Agent Reporter",
    instructions=instruction3,
    model="gpt-3.5-turbo"
)

description = "Give me latest news"

tool1 = agent_openai_gpt5.as_tool(tool_name="openai_gpt5_tool", tool_description=description)
tool2 = agent_openai_gpt4.as_tool(tool_name="openai_gpt4_tool", tool_description=description)
tool3 = agent_openai_gpt3.as_tool(tool_name="openai_gpt3_tool", tool_description=description)

tools = [tool1, tool2, tool3]

## Input guardrail to check no country name was given in the message

# Pydantic BaseModel constructor class
class CountryNameCheck(BaseModel):
    is_name_in_message: bool
    name: str
    
    class Config:
        extra = "forbid"

# guardrail agent for country name check
guardrail_country_name_check_agent = Agent(
    name="guardrail_country_name_check_agent",
    instructions="""Analyze the given message and check if it contains any country names like USA, United States, Canada, India, China, etc. 
    
    Examples:
    - "Pick the best news from USA" → is_name_in_message: True, name: "USA"
    - "Pick the best news from Canada" → is_name_in_message: True, name: "Canada"  
    - "Pick the best news" → is_name_in_message: False, name: ""
    - "Get news about the country" → is_name_in_message: False, name: ""
    
    Only return True if you find a specific country name, not general terms like 'country' or 'news'.""",
    output_type=CountryNameCheck,
    model="gpt-4o-mini"
)

# function as a tool
@input_guardrail
async def guardrail_country_name_check(ctx, agent, message):
    result = await Runner.run(guardrail_country_name_check_agent, message, context=ctx.context)
    is_name_in_message = result.final_output.is_name_in_message
    return GuardrailFunctionOutput(output_info={"found country name:": result.final_output}, tripwire_triggered=is_name_in_message)


# Defining my main agent which will select best news.
agent_selector = Agent(
    name="Open AI Selector Agent",
    instructions=instruction4,
    model="gpt-4o-mini",
    tools = tools,
    input_guardrails=[guardrail_country_name_check]
)

message = "Select best news for country USA"

async def main():
    with trace("Select Best News From Main Function"):        
        result = await Runner.run(agent_selector, message)
        result = result.final_output
        print("\n Selected News:\n", result)

if __name__ == "__main__":
    asyncio.run(main())