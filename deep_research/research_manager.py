from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from clarification_agent import clarification_agent, WebSearchItemClarification, WebSearchPlanClarification
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
import asyncio


@function_tool
class ResearchManager:

    async def run_interactive_research(self, query: str):
        """Run the complete interactive research process with clarifications in a single trace"""
        trace_id = gen_trace_id()
        with trace("Interactive Research Workflow", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            
            # Step 1: Get clarification questions within the same trace
            print("Getting clarification questions...")
            clarification_plan = await self.clarification_questions_searches(query)
            
            # Return both trace info and clarification plan
            return {
                "trace_id": trace_id,
                "clarification_plan": clarification_plan,
                "query": query
            }

    async def get_clarification_questions(self, query: str, trace_id: str = None) -> WebSearchPlanClarification:
        """Get clarification questions for the query within the existing trace context"""
        if trace_id:
            # If we have a trace_id, we're already within a trace context
            with trace("Clarification questions", trace_id=trace_id):
                return await self.clarification_questions_searches(query)
        else:
            # Fallback for standalone calls
            return await self.clarification_questions_searches(query)

    async def run_interactive_research(self, query: str):
        """Run the complete interactive research process with clarifications in a single trace"""
        trace_id = gen_trace_id()
        with trace("Interactive Research Workflow", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            
            # Step 1: Get clarification questions within the same trace
            print("Getting clarification questions...")
            clarification_plan = await self.clarification_questions_searches(query)
            
            # Return both trace info and clarification plan
            return {
                "trace_id": trace_id,
                "clarification_plan": clarification_plan,
                "query": query
            }
    async def continue_research_with_answers(self, trace_id: str, query: str, user_answers: list, clarification_plan: WebSearchPlanClarification):
        """Continue research with user answers within the same trace context"""
        with trace("Research continuation", trace_id=trace_id):
            # Create enhanced query with clarifications
            enhanced_query = self.create_enhanced_query(query, clarification_plan, user_answers)
            yield f"Enhanced query created with {len(user_answers)} clarification answers"
            
            yield "Planning searches based on clarifications..."
            search_plan = await self.plan_searches(enhanced_query)
            yield "Searches planned, starting to search..."
            
            search_results = await self.perform_searches(search_plan)
            yield "Searches complete, writing report..."
            
            report = await self.write_report_with_clarifications(query, search_results, clarification_plan, user_answers)
            yield "Report written, sending email..."
            
            await self.send_email(report)
            yield "Email sent, research complete"
            yield report.markdown_report

    def create_enhanced_query(self, original_query: str, clarification_plan: WebSearchPlanClarification, user_answers: list) -> str:
        """Create an enhanced query incorporating user clarification answers"""
        enhanced_parts = [f"Original Query: {original_query}"]
        enhanced_parts.append("\nUser provided clarifications:")
        
        for i, clarification_item in enumerate(clarification_plan.searches):
            if i < len(user_answers) and user_answers[i].strip():
                enhanced_parts.append(f"- {clarification_item.clarification_question}: {user_answers[i]}")
        
        return "\n".join(enhanced_parts)

    async def write_report_with_clarifications(self, query: str, search_results: list[str], clarification_plan: WebSearchPlanClarification, user_answers: list) -> ReportData:
        """Write the report including clarification context"""
        print("Thinking about report with clarifications...")
        
        # Build context from clarifications
        clarification_context = []
        for i, clarification_item in enumerate(clarification_plan.searches):
            if i < len(user_answers) and user_answers[i].strip():
                clarification_context.append(f"{clarification_item.clarification_question}: {user_answers[i]}")
        
        input_parts = [f"Original query: {query}"]
        if clarification_context:
            input_parts.append(f"User clarifications: {clarification_context}")
        input_parts.append(f"Summarized search results: {search_results}")
        
        input = "\n".join(input_parts)
        
        result = await Runner.run(
            writer_agent,
            input,
        )

        print("Finished writing report with clarifications")
        return result.final_output_as(ReportData)

    async def run(self, query: str):
        """Original run method - kept for backward compatibility"""
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            print("Searching Clarification questions...")
            clarification_questions_query = await self.clarification_questions_searches(query)
            yield "Clarification questions are searched now, starting to search..."     
            print("Starting research...")
            search_plan = await self.plan_searches(clarification_questions_query)
            yield "Searches planned, starting to search..."     
            search_results = await self.perform_searches(search_plan)
            yield "Searches complete, writing report..."
            report = await self.write_report(query, search_results)
            yield "Report written, sending email..."
            await self.send_email(report)
            yield "Email sent, research complete"
            yield report.markdown_report
        
    async def clarification_questions_searches(self, query: str) -> WebSearchPlanClarification:
        """Come up with clarification questions to perform for the query"""
        print("Searching clarification questions...")
        result = await Runner.run(
            clarification_agent,
            f"Query: {query}",
        )
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlanClarification)
        
    async def plan_searches(self, query: str) -> WebSearchPlan:
        """Plan the searches to perform for the query"""
        print("Planning searches...")
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        print(f"Will perform {len(result.final_output.searches)} searches")
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """Perform the searches to perform for the query"""
        print("Searching...")
        num_completed = 0
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """Perform a search for the query"""
        input = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input,
            )
            return str(result.final_output)
        except Exception:
            return None

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """Write the report for the query"""
        print("Thinking about report...")
        input = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(
            writer_agent,
            input,
        )

        print("Finished writing report")
        return result.final_output_as(ReportData)
    
    async def send_email(self, report: ReportData) -> None:
        print("Writing email...")
        result = await Runner.run(
            email_agent,
            report.markdown_report,
        )
        print("Email sent")
        return report