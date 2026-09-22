# Student Result Agent — LangChain + SQLite

A reimplemented version of the original **Student-LangChain-Tools** project.

The project still solves the same problem — a user can ask natural-language questions about students, marks, totals, averages, and passing eligibility — but the implementation is organized differently.

## What changed?

Instead of exposing four independent database/rules operations exactly like the original notebook, this version uses a small service-style structure:

- A reusable SQLite database helper handles connections.
- `get_student_profile()` retrieves identity and academic information together.
- `calculate_result()` performs total/average calculations from explicit marks.
- `check_passing_status()` applies the university rules.
- The calculator uses a restricted AST-based evaluator instead of raw `eval()`.
- The agent has a clearer system prompt and decides which tools are necessary.
- The database is initialized by a separate `setup_database.py` script.
- The API key is loaded from an environment variable; **no secret is stored in the source code**.

## Architecture

```text
User Question
      |
      v
LangChain Agent
      |
      +--------------------+
      |                    |
      v                    v
Student Profile Tool   Result/Rule Tools
      |                    |
      v                    v
    SQLite             Calculation Logic
      |                    |
      +----------+---------+
                 |
                 v
          Final Natural-Language Answer
```

## Features

The agent can answer questions such as:

```text
What is the name and department of 22CS045?
```

```text
Show me the complete result of 22CS045.
```

```text
What is the total and average mark of 22CS047?
```

```text
Is 22CS045 eligible to pass?
```

```text
Give me the result summary for 22CS045.
```

The agent chooses the required tool(s) instead of following a hard-coded sequence.

## Passing Rules

The example university rules are:

- Minimum overall average: **40%**
- Minimum mark in every subject: **35**

## Project Structure

```text
Student-LangChain-Tools-Variant/
├── student_agent.py
├── setup_database.py
├── students.db
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

### 1. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API key

Copy `.env.example` to `.env`:

```bash
copy .env.example .env
```

or on Linux/macOS:

```bash
cp .env.example .env
```

Then put your provider API key in `.env`.

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

**Do not commit `.env` or your API key to GitHub.**

The API key supplied during the request is intentionally not embedded in this project. Because an API key was shared in chat, rotate/revoke that key in the provider console if it is an active secret.

### 4. Initialize the database

```bash
python setup_database.py
```

The command creates `students.db` and inserts the sample student records.

### 5. Run the agent

```bash
python student_agent.py
```

You can then enter questions interactively.

Example:

```text
You: What is the total and average mark of 22CS045?

Agent: The total mark for Dhanushya is 325/400 and the average is 81.25%.
```

Use `exit` to stop the program.

## Example Data

| Student ID | Name | Department | Python | Database | AI | Web |
|---|---|---|---:|---:|---:|---:|
| 22CS045 | Dhanushya | Computer Science | 85 | 72 | 90 | 78 |
| 22CS046 | Rahul | Computer Science | 65 | 70 | 68 | 72 |
| 22CS047 | Priya | Information Technology | 92 | 88 | 95 | 90 |
| 22CS048 | Arun | Information Technology | 55 | 60 | 58 | 62 |
| 22CS049 | Meena | Computer Science | 78 | 85 | 80 | 88 |

## Important implementation details

### Tool 1 — `get_student_profile`

Fetches the student's name, department, and all subject marks in one database query.

### Tool 2 — `calculate_result`

Calculates:

- Total
- Average
- Percentage

The tool accepts explicit marks rather than querying the database itself. This keeps data retrieval and calculation separate.

### Tool 3 — `check_passing_status`

Checks both business rules:

```text
average >= 40
AND
every subject >= 35
```

It returns the individual rule results and the final eligibility.

### Tool 4 — `calculator`

A small arithmetic tool is included for general numerical calculations. It uses Python's AST parser and only permits a restricted set of arithmetic operations.

## Why this is a different implementation

The original project primarily demonstrated several small tools directly querying the database.

This version demonstrates a slightly more production-oriented separation:

```text
Agent
  |
  +--> Data retrieval
  |
  +--> Calculation
  |
  +--> Business-rule evaluation
```

This makes it easier to replace SQLite later with PostgreSQL or move the calculation/business logic into service classes.

## Technologies

- Python
- LangChain
- LangChain Google GenAI
- SQLite
- Google Gemini
- Pydantic-compatible tool schemas through LangChain

## Security note

Never hard-code API keys like:

```python
os.environ["GEMINI_API_KEY"] = "your-secret-key"
```

Use environment variables or a secret manager instead.

Also make sure `.env` is included in `.gitignore`.
