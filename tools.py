import os
from langchain_core.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import Tool

def get_serper_tool():
    """Returns the Google Serper tool if the API key is present."""
    if os.getenv("SERPER_API_KEY"):
        serper = GoogleSerperAPIWrapper()
        return Tool(
            name="GoogleSerperSearch",
            func=serper.run,
            description="Search Google via Serper API. Use for checking the most up-to-date IRS regulations, tax brackets, and 401(k) rules.",
        )
    return None

@tool
def calculate_tax_penalty(amount: float, age: float) -> str:
    """Calculate the estimated tax withholding and early withdrawal penalty for a 401(k) standard withdrawal.
    
    Args:
        amount: The total amount the user wants to withdraw.
        age: The user's age in years.
    """
    try:
        # Mandatory 20% federal tax withholding
        tax_withholding = amount * 0.20
        
        # 10% early withdrawal penalty if under 59.5
        penalty = 0.0
        if age < 59.5:
            penalty = amount * 0.10
            
        net_amount = amount - tax_withholding - penalty
        
        report = (
            f"Withdrawal Amount: ${amount:,.2f}\n"
            f"Mandatory 20% Federal Tax Withholding: ${tax_withholding:,.2f}\n"
        )
        if penalty > 0:
            report += f"10% Early Withdrawal Penalty (Under 59.5): ${penalty:,.2f}\n"
        else:
            report += "No Early Withdrawal Penalty (Age 59.5 or older).\n"
            
        report += f"Estimated Net Payout: ${net_amount:,.2f}\n"
        report += "\nNote: State taxes and your actual income tax bracket may affect the final amount."
        return report
    except Exception as e:
        return f"Error calculating tax penalty: {str(e)}"

@tool
def check_hardship_eligibility(reason: str) -> str:
    """Check if a withdrawal reason matches standard IRS safe harbor hardship criteria.
    
    Args:
        reason: The reason the user needs the money (e.g. 'medical expenses', 'buying a car', 'eviction').
    """
    reason_lower = reason.lower()
    
    safe_harbor_keywords = {
        "medical": ["medical", "doctor", "hospital", "surgery", "disease", "illness"],
        "home_purchase": ["buy a home", "first time home", "principal residence", "buying a house"],
        "tuition": ["tuition", "college", "university", "education", "school fees"],
        "eviction": ["eviction", "foreclosure", "rent", "kicked out"],
        "funeral": ["funeral", "burial", "death"],
        "home_repair": ["damage", "repair", "casualty", "hurricane", "fire", "flood"]
    }
    
    matched_categories = []
    for category, keywords in safe_harbor_keywords.items():
        if any(keyword in reason_lower for keyword in keywords):
            matched_categories.append(category)
            
    if matched_categories:
        return (
            f"The reason '{reason}' appears to potentially qualify for a Safe Harbor Hardship Withdrawal "
            f"under the category: {', '.join(matched_categories)}.\n"
            "Note: Hardship withdrawals are still subject to income tax and potentially the 10% early withdrawal penalty unless an exception applies."
        )
    else:
        return (
            f"The reason '{reason}' DOES NOT clearly match standard IRS Safe Harbor Hardship categories. "
            "Generally, things like buying a car, credit card debt, or vacations do not qualify for a hardship withdrawal."
        )

def get_all_tools():
    """Return a list of all available tools."""
    tools = [calculate_tax_penalty, check_hardship_eligibility]
    serper_tool = get_serper_tool()
    if serper_tool:
        tools.append(serper_tool)
    return tools
