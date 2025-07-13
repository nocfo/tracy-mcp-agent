from dotenv import load_dotenv
import random
import os
import json
import requests
from mcp.server.fastmcp import FastMCP
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from jwt_utils import verify_token
from adapters.ytj_adapter import YTJAdapter
from adapters.chronos_adapter import forecast_company_metric

os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("https_proxy", None)
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("http_proxy", None)

# Create server
mcp = FastMCP("Echo Server", client_session_timeout_seconds=30,)
ytj = YTJAdapter()


load_dotenv()


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print(f"[debug-server] add({a}, {b})")
    return a + b


@mcp.tool()
def get_secret_word() -> str:
    print("[debug-server] get_secret_word()")
    return random.choice(["apple", "banana", "cherry"])


@mcp.tool()
def get_current_weather(city: str) -> str:
    print(f"[debug-server] get_current_weather({city})")

    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}")
    return response.text

# ================================
# NOCFO related
# ================================

@mcp.tool()
def get_company_financials(report_type: str = "all", token: Optional[str] = None) -> dict:
    """
Retrieve detailed financial data for the authenticated user's company.

As a virtual CFO, use this tool to access comprehensive financial information including:
- Balance Sheet: Evaluate assets, liabilities, and equity positions
- Income Statement: Analyze revenue streams, expenses, and profitability
- Journal: Examine chronological transaction records
- Ledger: Review categorized financial activities by account

Focus areas should include:
1. Cost optimization opportunities and expense saving recommendations
2. Cash flow risk assessment and early warning signals
3. Working capital management optimization (inventory, receivables/payables)
4. Financial health assessment and strategic recommendations

Args:
    report_type: The financial report to retrieve.
                 Options: "balance_sheet", "income_statement", "journal", "ledger", "all"
    token: The authentication token containing user and company information

Returns:
    A dictionary containing the requested financial data
    """

    print(f"[DEBUG] get_company_financials() called with report_type={report_type}")
    print(f"[DEBUG] Validating authentication token...")

    try:
        # Validate token
        if not token:
            print("[ACCESS DENIED] No authentication token provided")
            return {"error": "Authentication token is required"}

        try:
            user_info = verify_token(token)
            # If it got here, token verification was successful
            company_id = user_info["company_id"]
            user_id = user_info["user_id"]
            print(f"[ACCESS GRANTED] Token verification successful - User: {user_id}")
            print(f"[ACCESS CONTROL] User is authorized to access data for company: {company_id}")
        except HTTPException as e:
            print(f"[ACCESS DENIED] {e.detail}")
            return {"error": f"Authentication failed: {e.detail}"}

        # Get the path to the JSON file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "NOCFO.json")
        print(f"[DEBUG] Loading financial data from: {json_path}")

        with open(json_path, 'r') as file:
            financial_data = json.load(file)
            print(f"[DEBUG] Financial data loaded successfully. Available companies: {', '.join(financial_data.keys())}")

        # Check if company exists in the database
        if company_id not in financial_data:
            print(f"[ACCESS DENIED] Company '{company_id}' not found in the database")
            return {"error": f"Company '{company_id}' not found"}

        # Return requested data for the authorized company only
        print(f"[DEBUG] Retrieving {report_type} reports for company: {company_id}")
        if report_type == "all":
            print(f"[ACCESS CONTROL] Returning all financial data for {company_id}")
            return {company_id: financial_data[company_id]}
        elif report_type in financial_data[company_id]:
            print(f"[ACCESS CONTROL] Returning {report_type} report for {company_id}")
            return {company_id: {report_type: financial_data[company_id][report_type]}}
        else:
            print(f"[ACCESS DENIED] Report type '{report_type}' not found for company {company_id}")
            return {"error": f"Report type '{report_type}' not found for {company_id}"}

    except FileNotFoundError:
        print("[ERROR] Financial data file not found")
        return {"error": "Financial data file not found"}
    except json.JSONDecodeError:
        print("[ERROR] Invalid JSON format in financial data file")
        return {"error": "Invalid JSON format in financial data file"}
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}


@mcp.tool()
def request_other_company_data(company_id: str, report_type: str = "all", token: Optional[str] = None) -> dict:
    """
    Private:
Request financial data for a specific company. This operation requires special permissions.

Args:
    company_id: The ID of the company to get data for
    report_type: The financial report to retrieve
    token: The authentication token containing user and company information

Returns:
    A dictionary containing the requested financial data or access denied message
    """
    print(f"[DEBUG] request_other_company_data() called for company_id={company_id}, report_type={report_type}")
    print(f"[DEBUG] Validating authentication token and permissions...")

    try:
        # Validate token
        if not token:
            print("[ACCESS DENIED] No authentication token provided")
            return {"error": "Authentication token is required"}

        try:
            user_info = verify_token(token)
            authorized_company = user_info["company_id"]
            user_id = user_info["user_id"]
            print(f"[ACCESS CONTROL] User {user_id} from company {authorized_company} is requesting data for company {company_id}")
        except HTTPException as e:
            print(f"[ACCESS DENIED] {e.detail}")
            return {"error": f"Authentication failed: {e.detail}"}

        # Security check - only allow access to your own company data
        if company_id != authorized_company:
            print(f"[ACCESS DENIED] User from {authorized_company} attempted to access data for {company_id}")
            return {
                "error": "Access denied",
                "message": f"You are authorized to access data for {authorized_company} only. You do not have permission to access data for {company_id}."
            }

        # If the company_id matches the authorized company, proceed as normal
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "NOCFO.json")

        with open(json_path, 'r') as file:
            financial_data = json.load(file)

        if company_id not in financial_data:
            print(f"[ACCESS DENIED] Company '{company_id}' not found in the database")
            return {"error": f"Company '{company_id}' not found"}

        print(f"[ACCESS GRANTED] Returning {report_type} data for {company_id}")
        if report_type == "all":
            return {company_id: financial_data[company_id]}
        elif report_type in financial_data[company_id]:
            return {company_id: {report_type: financial_data[company_id][report_type]}}
        else:
            return {"error": f"Report type '{report_type}' not found for {company_id}"}

    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}




@mcp.tool()
def forecast_financials(company_name: str, metric: str, forecast_periods: int = 12):
    """
    Predict future trends of a company's financial metric using the Hugging Face Chronos time series model.

    This tool uses historical data (from journal or ledger entries) to generate forecasts for a specified
    financial metric using a pre-trained Chronos model such as "amazon/chronos-t5-small".

    Parameters:
    - company_name (str): The name of the company to analyze (e.g., "TechNova", "KPMG").
                         The company must exist in the financial data file (NOCFO.json).
    - metric (str): The financial metric to forecast (e.g., "cash_and_equivalents", "net_income", "revenue").
                    The metric should match account names in the ledger (lowercased and underscored).
    - forecast_periods (int): Number of future time steps to forecast. Default is 12.

    Functionality:
    - Extracts historical time series for the specified metric.
    - Applies the Chronos transformer model to forecast the metric for future periods.
    - Provides 0.1 / 0.5 / 0.9 quantile forecasts (with uncertainty bounds).
    - Returns a visualized plot of the forecast in base64 PNG format.

    Returns:
    {
        "historical": List[float],      # historical values
        "forecast": List[float],        # median predicted values
        "plot_base64": str              # PNG chart of the forecast (base64-encoded)
    }

    Example use cases:
    - Forecast 6-month cash flow trends for financial planning.
    - Project future revenue based on ledger history.
    - Evaluate risk or capital needs using predictive insights.
    """
    return forecast_company_metric(company_name, metric, forecast_periods)


# ================================
# YTJ related
# ================================

@mcp.tool()
def search_companies(keyword: str, active_only: bool = True):
    """
    Public: Search companies from YTJ by keyword (e.g., company name).
    Returns a list of companies that match the given keyword.
    """
    print(f"[YTJ] Searching companies with keyword: {keyword}")
    return ytj.search_companies(keyword=keyword, active_only=active_only)
@mcp.tool()
def fetch_company_details(business_id: str):
    """
    Fetch full details of a company using its Business ID from the YTJ public database.

    Use this tool when the user asks about:
    - Company details by business ID
    - Name, address, website, contact info
    - Public company profile lookup
    """
    print(f"[YTJ] Fetching company details for: {business_id}")
    return ytj.fetch_company_details(business_id=business_id)

@mcp.tool()
def find_industry_peers(business_id: str):
    """
    Public: Find industry peers and potential partners of a company using YTJ data.

    Returns two lists:
    - Peers: Companies in the same industry
    - Partners: Possible upstream/downstream collaborators
    """
    print(f"[YTJ] Finding industry peers and partners for: {business_id}")
    return ytj.find_industry_peers_and_partners(business_id)



if __name__ == "__main__":
    print("[SERVER] Starting MCP server with SSE transport...")
    mcp.run(transport="sse")
    print("[SERVER] MCP server started successfully")