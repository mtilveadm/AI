import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager
import asyncio

load_dotenv(override=True)

research_manager = ResearchManager()

async def run_research(query: str):
    """Initial run - gets clarification questions and shows them to user"""
    if not query.strip():
        return (
            "Please enter a research query first.",  # status
            gr.Group(visible=False),                 # clarification_section
            gr.HTML(visible=False),                  # questions_display
            gr.Button(visible=False),               # submit_answers_btn
            None,                                   # clarification_state
            *[gr.Textbox(visible=False, label="") for _ in range(10)]  # answer_components
        )
    
    try:
        # Start interactive research workflow - this creates the trace and gets clarifications
        workflow_data = await research_manager.run_interactive_research(query)
        clarification_plan = workflow_data["clarification_plan"]
        
        if clarification_plan and clarification_plan.searches:
            questions = []
            for item in clarification_plan.searches:
                questions.append(item.clarification_question)
            
            # Create HTML display of questions
            questions_html = "<div style='margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 8px;'>"
            questions_html += "<h3 style='color: #2563eb; margin-bottom: 15px;'>📝 Clarification Questions</h3>"
            questions_html += f"<p style='margin-bottom: 15px; color: #666;'>View trace: https://platform.openai.com/traces/trace?trace_id={workflow_data['trace_id']}</p>"
            questions_html += "<p style='margin-bottom: 15px; color: #666;'>Please answer these questions to help me provide better research:</p>"
            for i, question in enumerate(questions):
                questions_html += f"<div style='margin-bottom: 10px;'><strong>Question {i+1}:</strong> {question}</div>"
            questions_html += "</div>"
            
            # Prepare answer textboxes
            answer_components = []
            for i in range(10):
                if i < len(questions):
                    answer_components.append(
                        gr.Textbox(
                            visible=True,
                            label=f"Question {i+1}",
                            placeholder=f"Answer: {questions[i][:60]}...",
                            lines=2
                        )
                    )
                else:
                    answer_components.append(gr.Textbox(visible=False, label=""))
            
            return (
                f"Generated {len(questions)} clarification questions. Please answer them and click 'Submit Answers' to continue.",  # status
                gr.Group(visible=True),                    # clarification_section
                gr.HTML(value=questions_html, visible=True), # questions_display
                gr.Button(visible=True),                   # submit_answers_btn
                workflow_data,                             # clarification_state (includes trace_id)
                *answer_components                         # answer_components
            )
        else:
            return (
                "No clarification questions generated. Starting research directly...",
                gr.Group(visible=False),
                gr.HTML(visible=False),
                gr.Button(visible=False),
                None,
                *[gr.Textbox(visible=False, label="") for _ in range(10)]
            )
            
    except Exception as e:
        return (
            f"Error getting clarifications: {str(e)}",
            gr.Group(visible=False),
            gr.HTML(visible=False),
            gr.Button(visible=False),
            None,
            *[gr.Textbox(visible=False, label="") for _ in range(10)]
        )

async def submit_answers_and_continue(workflow_data, *answers):
    """Submit clarification answers and continue with research"""
    if not workflow_data:
        yield "No workflow data found. Please restart the process."
        return
        
    trace_id = workflow_data["trace_id"]
    query = workflow_data["query"]
    clarification_plan = workflow_data["clarification_plan"]
    questions = [item.clarification_question for item in clarification_plan.searches]
    
    # Filter answers to match number of questions
    user_answers = list(answers[:len(questions)])
    
    # Check if all questions are answered
    empty_answers = [i+1 for i, ans in enumerate(user_answers) if not ans.strip()]
    if empty_answers:
        yield f"Please answer all questions. Missing answers for question(s): {', '.join(map(str, empty_answers))}"
        return
    
    yield f"Answers submitted! Continuing research within the same trace..."
    
    # Continue with the research process using the same trace_id
    async for update in research_manager.continue_research_with_answers(trace_id, query, user_answers, clarification_plan):
        yield update

def create_interface():
    with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
        gr.Markdown("# 🔬 Deep Research Assistant")
        gr.Markdown("Enter your research query and click **Run** to begin. The system will ask clarification questions before starting the research.")
        
        with gr.Row():
            with gr.Column():
                query_textbox = gr.Textbox(
                    label="Research Query",
                    placeholder="What would you like to research? (e.g., 'Impact of artificial intelligence on healthcare')",
                    lines=3
                )
                run_button = gr.Button("🚀 Run Research", variant="primary", size="lg")
        
        # Status display
        status_display = gr.Markdown("💡 **Ready to start!** Enter your research query above and click 'Run Research'.")
        
        # Clarification section (initially hidden)
        clarification_section = gr.Group(visible=False)
        with clarification_section:
            questions_display = gr.HTML(visible=False)
            
            # Answer textboxes (up to 10 questions)
            answer_components = []
            for i in range(10):
                answer_box = gr.Textbox(
                    label=f"Answer {i+1}",
                    visible=False,
                    placeholder="Enter your answer here...",
                    lines=2
                )
                answer_components.append(answer_box)
            
            submit_answers_btn = gr.Button("✅ Submit Answers & Continue Research", variant="primary", visible=False)
        
        # Results section
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📄 Research Report")
                report_display = gr.Markdown()
        
        # Hidden state to store clarification data
        clarification_state = gr.State()
        
        # Event handlers
        run_button.click(
            fn=run_research,
            inputs=[query_textbox],
            outputs=[
                status_display,
                clarification_section,
                questions_display,
                submit_answers_btn,
                clarification_state
            ] + answer_components
        )
        
        submit_answers_btn.click(
            fn=submit_answers_and_continue,
            inputs=[clarification_state] + answer_components,
            outputs=[report_display]
        )
        
        # Allow enter key on query textbox to run research
        query_textbox.submit(
            fn=run_research,
            inputs=[query_textbox],
            outputs=[
                status_display,
                clarification_section,
                questions_display,
                submit_answers_btn,
                clarification_state
            ] + answer_components
        )
    
    return ui

# Create and launch the interface
if __name__ == "__main__":
    ui = create_interface()
    ui.launch(inbrowser=True)