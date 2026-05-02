import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from tools import get_all_tools

load_dotenv()

SYSTEM_PROMPT = """You are a licensed retirement planner and AI assistant specializing in 401(k) withdrawals.
Your primary goal is to provide accurate advice strictly confined to IRS regulations.

You have access to tools to:
1. Calculate tax withholdings and early withdrawal penalties.
2. Check if a reason qualifies for an IRS Safe Harbor Hardship withdrawal.
3. Search the web (via Serper API) for the most up-to-date IRS rules, SECURE 2.0 Act changes, and tax brackets.

Guidelines:
- ALWAYS ask clarifying questions if you need more information (e.g., age, amount, employment status) to give accurate advice.
- ALWAYS use your tools to perform calculations or check hardship eligibility before giving definitive answers.
- If a user asks a question outside the scope of 401(k) rules or retirement planning, politely decline to answer.
- Emphasize that your calculations are estimates and they should consult a tax professional for exact figures.
- Use the Google Serper tool whenever you are unsure of the latest rule or limit.
"""

def get_agent():
    """Create and return the LangGraph ReAct agent."""
    # Ensure OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable not set. Please add it to your .env file.")
        
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    tools = get_all_tools()
    
    agent_executor = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT
    )
    
    return agent_executor

if __name__ == "__main__":
    # Simple CLI test
    agent = get_agent()
    print("Agent loaded successfully. Tools available:", [t.name for t in get_all_tools()])
