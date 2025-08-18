from pydantic import BaseModel, Field
from agents import Agent

CLARIFICATION_QUESTIONS = 3

INSTRUCTIONS = f"You are a clarification agent. Given a query, come up with a set of clarification questions  \
to perform to best answer the query. Output {CLARIFICATION_QUESTIONS} terms to query for."


class WebSearchItemClarification(BaseModel):
    clarification_question: str = Field(description="Your clarification question for optimized deep search of query.")
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlanClarification(BaseModel):
    searches: list[WebSearchItemClarification] = Field(description="A list of web searches to perform to best answer the query.")
    
clarification_agent = Agent(
    name="ClarificationAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlanClarification,
)