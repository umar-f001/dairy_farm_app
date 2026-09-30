from dotenv import load_dotenv
load_dotenv()

import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

# LangChain aur baaki custom imports
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openrouter import ChatOpenRouter

from app.core.database import get_db

# APIRouter setup
router = APIRouter(prefix="/agent", tags=["AI Agent"])

class AgentRequest(BaseModel):
    user_message: str

# --- LANGCHAIN TOOLS ---
BASE_URL = "http://192.168.190.186:8000/api/v1"

# ==========================================
# 1. ANIMALS ENDPOINTS TO TOOLS
# ==========================================

@tool
async def get_all_animals() -> str:
    """Use this tool to get the list of all animals in the dairy farm."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/animals/list_animals")
        if response.status_code == 200:
            return str(response.json())
        return f"Error fetching animals data: {response.text}"

@tool
async def register_new_animal(tag_number: str, breed: str, gender: Optional[str] = "Female", date_of_birth: Optional[str] = None, status: Optional[str] = "Active") -> str:
    """Use this tool to register/add a new animal to the dairy farm database. 
    date_of_birth format should be 'YYYY-MM-DD'."""
    payload = {
        "tag_number": tag_number,
        "breed": breed,
        "gender": gender,
        "status": status
    }
    if date_of_birth:
        payload["date_of_birth"] = date_of_birth

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/animals/register_animal", json=payload)
        if response.status_code == 201:
            return f"Successfully registered animal: {response.json()}"
        return f"Failed to register animal. Error: {response.text}"

@tool
async def update_animal_record(tag_number: str, new_tag_number: Optional[str] = None, breed: Optional[str] = None, gender: Optional[str] = None, date_of_birth: Optional[str] = None, status: Optional[str] = None) -> str:
    """Use this tool to partially update an animal's information by using their current tag_number.
    date_of_birth format should be 'YYYY-MM-DD'."""
    payload = {}
    if new_tag_number: payload["tag_number"] = new_tag_number
    if breed: payload["breed"] = breed
    if gender: payload["gender"] = gender
    if date_of_birth: payload["date_of_birth"] = date_of_birth
    if status: payload["status"] = status

    async with httpx.AsyncClient() as client:
        response = await client.patch(f"{BASE_URL}/animals/update_animal/{tag_number}", json=payload)
        if response.status_code == 200:
            return f"Successfully updated animal record: {response.json()}"
        return f"Failed to update animal. Error: {response.text}"

@tool
async def delete_animal_record(tag_number: str) -> str:
    """Use this tool to delete an animal from the database using its tag number. Warning: This will delete all its milking records too."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BASE_URL}/animals/delete_animal/{tag_number}")
        if response.status_code == 200:
            return f"Successfully deleted: {response.json().get('message')}"
        return f"Failed to delete animal. Error: {response.text}"


# ==========================================
# 2. MILKING TRACKING ENDPOINTS TO TOOLS
# ==========================================

@tool
async def generate_milk_yield() -> str:
    """Use this tool to randomly generate the milk yield amount BEFORE recording/uploading the milk log. 
    It's essential to call this before running the uploadMilkRec tool."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/milkingmilkYield")
        if response.status_code == 200:
            return f"Generated milk yield amount successfully: {response.json()}"
        return f"Failed to generate milk yield. Error: {response.text}"

@tool
async def record_milk_production(tag_number: str, shift: str) -> str:
    """Use this tool to record/upload a milk production log for a specific animal. 
    shift must be either 'Morning' or 'Evening'. Always ensure generate_milk_yield is called before this."""
    payload = {
        "tag_number": tag_number,
        "shift": shift
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/milking/uploadMilkRec", json=payload)
        if response.status_code == 201:
            return f"Milk production recorded successfully: {response.json()}"
        return f"Failed to record milk production. Error: {response.text}"

@tool
async def get_milk_records(tag_number: Optional[str] = None, number_of_days: Optional[int] = None) -> str:
    """Use this tool to fetch/get milk yield logs. You can filter by tag_number and/or number_of_days."""
    params = {}
    if tag_number: params["tag_number"] = tag_number
    if number_of_days: params["number_of_days"] = number_of_days
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/milking/get_milk_record", params=params)
        if response.status_code == 200:
            return str(response.json())
        return f"No milk records found or error occurred: {response.text}"


# ==========================================
# 3. FEED / INVENTORY ENDPOINTS TO TOOLS
# ==========================================

@tool
async def log_feed_inventory(quantity_kg: float, supplier_name: Optional[str] = "General Market", total_cost: Optional[float] = 0.0, current_date: Optional[str] = None) -> str:
    """Use this tool to create/log a new feed or inventory purchase entry.
    quantity_kg must be greater than 0. total_cost must be >= 0. current_date format is 'YYYY-MM-DD'."""
    payload = {
        "quantity_kg": quantity_kg,
        "supplier_name": supplier_name,
        "total_cost": total_cost
    }
    if current_date:
        payload["current_date"] = current_date

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/inventory/log_inventory", json=payload)
        if response.status_code == 201:
            return f"Inventory logged successfully: {response.json()}"
        return f"Failed to log inventory. Error: {response.text}"

@tool
async def list_all_inventory_logs() -> str:
    """Use this tool to get a full list of all feed inventory logs ordered by date."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/inventory/list_logs")
        if response.status_code == 200:
            return str(response.json())
        return f"Error fetching inventory logs: {response.text}"

@tool
async def update_inventory_log(log_id: int, quantity_kg: Optional[float] = None, supplier_name: Optional[str] = None, total_cost: Optional[float] = None, current_date: Optional[str] = None) -> str:
    """Use this tool to update an existing inventory log using its log_id.
    current_date format should be 'YYYY-MM-DD'."""
    payload = {}
    if quantity_kg is not None: payload["quantity_kg"] = quantity_kg
    if supplier_name is not None: payload["supplier_name"] = supplier_name
    if total_cost is not None: payload["total_cost"] = total_cost
    if current_date is not None: payload["current_date"] = current_date

    async with httpx.AsyncClient() as client:
        response = await client.patch(f"{BASE_URL}/inventory/update_log/{log_id}", json=payload)
        if response.status_code == 200:
            return f"Inventory log updated successfully: {response.json()}"
        return f"Failed to update inventory log. Error: {response.text}"

@tool
async def delete_inventory_log(log_id: int) -> str:
    """Use this tool to delete an inventory log from the system using its log_id."""
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BASE_URL}/inventory/delete_log/{log_id}")
        if response.status_code == 200:
            return f"Successfully deleted inventory log: {response.json().get('message')}"
        return f"Failed to delete inventory log. Error: {response.text}"


# ---- Master Tools List ----
tools = [
    get_all_animals, 
    register_new_animal, 
    update_animal_record, 
    delete_animal_record,
    generate_milk_yield, 
    record_milk_production, 
    get_milk_records,
    log_feed_inventory, 
    list_all_inventory_logs, 
    update_inventory_log, 
    delete_inventory_log
]


# ---- Agent Setup ----
openrouter_key = os.getenv("OPENROUTER_API_KEY")

llm = ChatOpenRouter(
    model="stealth/ox-alpha",
    max_tokens=1024,
    openrouter_api_key=openrouter_key
)

prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an advanced AI assistant for a Dairy Farm Management System.\n"
        "You have full control over Animals, Milk Production, and Feed Inventory management.\n"
        "Important Instructions:\n"
        "1. When a user asks to record/upload milk production, you MUST first run 'generate_milk_yield' to set the yield value, and then immediately invoke 'record_milk_production'.\n"
        "2. Ensure dates passed to tools are string format 'YYYY-MM-DD'.\n"
        "Be efficient, professional, and execute commands accurately based on user text."
    )),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- POST ENDPOINT ---
@router.post("")
async def chat_with_agent(payload: AgentRequest, db: AsyncSession = Depends(get_db)):
    try:
        response = await agent_executor.ainvoke({"input": payload.user_message})
        output_text = response.get("output", "")
        
        if "user not found" in output_text.lower() or "unauthorized" in output_text.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"OpenRouter Authentication Failed: {output_text}"
            )
            
        return {"response": output_text}
        
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent failed to process request: {str(e)}"
        )