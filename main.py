from fastapi import FastAPI
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel
import uvicorn
import os
from sqlalchemy import create_engine, text

app = FastAPI()

# PostgreSQL connection details
DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "127.0.0.1:5432"
DB_NAME = "hospital"
DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# SQLAlchemy engine for direct queries
engine = create_engine(DATABASE_URI)

# LangChain components
db = SQLDatabase.from_uri(DATABASE_URI)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", openai_api_key=OPENAI_API_KEY)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Setup SQLDatabaseChain (NO memory here!)
chain = SQLDatabaseChain.from_llm(
    llm=llm,
    db=db,
    verbose=True,
    return_intermediate_steps=True,
    output_key="result"  # this is important
)

# Fix SQL markdown issue
prompt = chain.llm_chain.prompt.template
chain.llm_chain.prompt.template = prompt.replace("```sql", "").replace("```", "")

# Clean SQL markdown from results
def strip_sql_backticks(response_obj):
    steps = response_obj.get("intermediate_steps", [])
    response_obj["intermediate_steps"] = [
        step.replace("```sql", "").replace("```", "").strip() if isinstance(step, str) else step
        for step in steps
    ]
    if isinstance(response_obj.get("result", ""), str):
        response_obj["result"] = response_obj["result"].replace("```sql", "").replace("```", "").strip()
    return response_obj

# Request schema
class QueryRequest(BaseModel):
    query: str

# Endpoint
@app.post("/ask")
async def ask(request: QueryRequest):
    # LangChain cannot store to memory due to multiple keys; handle memory manually
    raw_output = chain.invoke({"query": request.query})
    cleaned_output = strip_sql_backticks(raw_output)

    # Store only query/response to memory
    memory.save_context(
        {"query": request.query},
        {"response": cleaned_output["result"]}
    )

    return {
        "response": cleaned_output["result"],
        "sql_query": cleaned_output.get("intermediate_steps", [""])[-1]
    }

# Endpoint to fetch appointment schedule
@app.get("/appointments")
def get_appointments():
    query = text(
        """
        SELECT a.id as appointment_id, a.patient_name, a.time_slot, a.status,
               d.name as doctor_name, d.is_available, dep.name as department_name
        FROM doctors d
        LEFT JOIN departments dep ON d.department_id = dep.id
        LEFT JOIN appointments a ON a.doctor_id = d.id
        ORDER BY a.time_slot
        """
    )
    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.mappings().all()
    return [dict(row) for row in rows]

# Run server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
