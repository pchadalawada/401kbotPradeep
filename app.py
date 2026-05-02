import os
import gradio as gr
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from agent import get_agent

load_dotenv()

# Initialize the agent
try:
    agent = get_agent()
    AGENT_LOADED = True
except Exception as e:
    print(f"Error loading agent: {e}")
    AGENT_LOADED = False

def convert_gradio_to_langchain_messages(gradio_history):
    """Convert Gradio history (list of dicts) to Langchain message objects."""
    langchain_msgs = []
    for msg in gradio_history:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            langchain_msgs.append(HumanMessage(content=content))
        elif role == "assistant":
            # For simplicity, we just pass the text back as an AIMessage.
            langchain_msgs.append(AIMessage(content=content))
    return langchain_msgs

def chat_interface(user_message, history):
    """Process a user message and generate a response using the LangGraph agent."""
    if not AGENT_LOADED:
        yield history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": "Error: Agent could not be loaded. Please ensure OPENAI_API_KEY is set in your .env file."}
        ]
        return
        
    # Append the new user message to the history
    history.append({"role": "user", "content": user_message})
    yield history # Yield immediately to show user message
    
    # Convert history to langchain format
    langchain_messages = convert_gradio_to_langchain_messages(history)
    
    # Run the agent
    config = {"configurable": {"thread_id": "gradio_session"}}
    
    try:
        # We use stream to get intermediate steps if we want, or just invoke.
        # Here we'll just invoke for simplicity and get the final output, 
        # but LangGraph agents can stream tokens too. Let's do simple invoke first.
        result = agent.invoke({"messages": langchain_messages}, config=config)
        
        # The result["messages"] contains the full conversation trace.
        # The last message is the AI's final response.
        final_message = result["messages"][-1].content
        
        history.append({"role": "assistant", "content": final_message})
        yield history
        
    except Exception as e:
        history.append({"role": "assistant", "content": f"An error occurred: {str(e)}"})
        yield history

# Define the Gradio Interface
with gr.Blocks(title="IRS-Compliant 401(k) Withdrawal Assistant") as demo:
    gr.Markdown("# 🏦 IRS-Compliant 401(k) Withdrawal Assistant")
    gr.Markdown(
        "I can help you understand 401(k) withdrawals, penalties, "
        "and tax implications based on the latest IRS regulations."
    )
    
    if not os.getenv("OPENAI_API_KEY"):
        gr.Warning("OPENAI_API_KEY is not set. The chatbot will not function correctly.")
    if not os.getenv("SERPER_API_KEY"):
        gr.Warning("SERPER_API_KEY is not set. The agent won't be able to search the web for the latest rules.")
        
    chatbot = gr.Chatbot(height=500)
    msg = gr.Textbox(placeholder="E.g., I'm 55 and need $10,000 for a medical emergency. What are the penalties?")
    clear = gr.ClearButton([msg, chatbot])
    
    msg.submit(chat_interface, [msg, chatbot], [chatbot])
    msg.submit(lambda: "", None, msg) # Clear input box after submission

if __name__ == "__main__":
    # In Cloud Run, it will bind to the PORT environment variable
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
