import os
import pymssql
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_db_conn():
    return pymssql.connect(
        server=os.getenv("SQL_SERVER"),
        user=os.getenv("SQL_USER"),
        password=os.getenv("SQL_PWD"),
        database=os.getenv("SQL_DB")
    )


@app.get("/employees", response_class=HTMLResponse)
async def get_employees(request: Request):
    try:
        with get_db_conn() as conn:
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute("SELECT name, department FROM Employees")
                employees = cursor.fetchall()
        return templates.TemplateResponse("employees.html", {"request": request, "employees": employees})
    except Exception as e:
        return HTMLResponse(content=f"Connection Error: {e}", status_code=500)


@app.post("/add-employee")
async def add_employee(name: str = Form(...), department: str = Form(...)):
    with get_db_conn() as conn:
        with conn.cursor() as cursor:
            # Use %s as the placeholder for pymssql
            cursor.execute(
                "INSERT INTO Employees (name, department) VALUES (%s, %s)", (name, department))
        conn.commit()
    return RedirectResponse(url="/employees", status_code=303)
