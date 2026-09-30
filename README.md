## Dairy Farm Automation API
An advanced asynchronous FastAPI application designed to automate dairy farm management. The system handles animal tracking, milk production logs, and feed inventory tracking, while embedding a LangChain-powered AI Agent that dynamically executes farm tasks using function-calling tools.
------------------------------
## 🚀 Key Features

* Animal Management: CRUD endpoints for registering livestock details (breeds like Sahiwal, Cholistani, etc.), statuses (Pregnant, Sick, Active, Dry), and tracking history.
* Milk Production Tracking: High-precision logging for shifts (Morning/Evening) linked directly to the animal database via cascading foreign keys.
* Feed & Inventory Logs: Track supplier details, costs, and current stock metrics to monitor warehouse margins.
* LangChain AI Agent: Integrates an LLM via OpenRouter using functional tools to allow operators to look up records, modify livestock files, or register entries using plain natural language chat.
* Asynchronous Design: Completely non-blocking database queries built via SQLAlchemy's modern async/await engine utilizing asyncpg.

------------------------------
## 🛠️ Tech Stack

* Framework: FastAPI (Asynchronous Python)
* Database ORM: SQLAlchemy 2.0 (Async Extension) + PostgreSQL
* AI Core: LangChain Core, LangChain OpenRouter Integration
* Data Schemas: Pydantic v2
* HTTP Client: HTTPX (Used by Agent tools for internal API routing)

------------------------------
## 📁 System Architecture
app/
├── api/
│   ├── api_v1.py           # Master API router configuration
│   └── endpoints/
│       ├── agent.py         # LangChain AI agent and execution setup
│       ├── animals.py       # Animal registration and record lifecycles
│       ├── feed.py          # Inventory logs and tracking endpoints
│       └── milk_tracking.py # Milking yields and shift logging operations
├── core/
│   └── database.py          # Async PostgreSQL session engines
├── models/
│   ├── base.py              # Declarative SQLAlchemy base mappings
│   ├── animal.py            # 'animals' database table structure
│   ├── feed.py              # 'inventory_logs' database table structure
│   └── milk_tracking.py     # 'milk_logs' relational database table
├── schema/
│   ├── animal.py            # Pydantic creation, update, and response validation
│   ├── feed.py              # Pydantic structures for tracking food supplies
│   └── milk_tracking.py     # Pydantic schemas protecting milk entry inputs
└── main.py                  # API instantiation, Lifespan hooks, and Middlewares

------------------------------
## ⚡ Getting Started
## 1. Prerequisites
Ensure you have Python 3.10+ and a running PostgreSQL instance configured.
## 2. Environment Setup
Create a .env file in the root directory to declare your external API secrets:

OPENROUTER_API_KEY=your_openrouter_api_key_here

## 3. Installation
Clone the repository and install your dependencies:

git clone https://github.com
cd dairy_farm_app
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
# Install required packages
pip install fastapi uvicorn sqlalchemy asyncpg pydantic langchain-core langchain-openai httpx python-dotenv

Note: Update the database connection URI inside app/core/database.py if your local PostgreSQL credentials differ from the default string (postgresql+asyncpg://postgres:12345678@localhost:5432/postgres).
## 4. Running the Application
Launch the server using Uvicorn:

uvicorn app.main:app --reload

Upon startup, the application's asynchronous lifespan handler will automatically connect to your database and generate all necessary structural tables if they do not already exist.
------------------------------
## 🔌 API Endpoints Summary
## Animals (/api/v1/animals)

* POST /register_animal - Add a unique animal with structural constraints.
* PATCH /update_animal/{tag_number} - Adjust parameters dynamically.
* GET /list_animals - Fetch comprehensive records ordered sequentially.
* DELETE /delete_animal/{tag_number} - Remove an animal and clear its dependent logs automatically.

## Milk Production (/api/v1/milking)

* GET /milkYield - Simulates a randomized organic yield amount (5 to 25 liters).
* POST /uploadMilkRec - Permanently commits a yield entry for a specific animal shift.
* GET /get_milk_record - Query histories with tag filters and custom day metrics.

## Feed Inventory (/api/v1/inventory)

* POST /log_inventory | GET /list_logs | PATCH /update_log/{id} | DELETE /delete_log/{id}

## AI Agent Interface (/api/v1/agent)

* POST /agent - Standard plain-text input execution gateway.

------------------------------
## 🤖 The Core AI Agent Protocol
The embedded system utilizes a native toolkit orchestration schema. When you prompt the agent via text, it decides which endpoint to call internally using async HTTPX routines.

⚠️ Important Sequence Dependency: For recording shift production logs, the agent framework enforces an explicit sequential rule. It must execute the generate_milk_yield routine to secure a mock volume metric before committing the entry to the system database.

------------------------------
🔬 API Documentation & Testing: Once the backend is online, navigate to http://localhost:8000/docs to test endpoints directly inside the interactive Swagger UI browser environment.
------------------------------
