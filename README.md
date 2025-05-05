# A Financial Knowledge Graph Construction from SET50 Annual Reports

This project constructs a Financial Knowledge Graph (KG) from the annual reports of SET50 companies. It enables users to query financial data through a chatbot interface, facilitating complex financial analysis. The project compares the performance and efficiency of two database systems: Neo4j (graph-based) and MySQL (relational).

---

## Project Structure

- `llm-chatbot-python-neo4j`: Contains code for Neo4j database integration.
- `llm-chatbot-python-mysql`: Contains code for MySQL database integration.

Each directory includes the necessary files to run an independent instance of the chatbot application.

---

## Prerequisites
Before setting up the project, ensure you have the following installed:

- **Python**: Version 3.8 or higher  
- **Neo4j**: Community or Enterprise Edition  
- **MySQL**: Version 8.0 or higher  
- **Node.js and npm**: For frontend development (if applicable)
  
---

## Set Up Databases

To populate the databases with data, please follow the instructions in the database setup repository:  
👉 [A-Financial-Knowledge-Graph-SET50-Annual-Reports-database](https://github.com/naphattha/A-Financial-Knowledge-Graph-SET50-Annual-Reports-database)

---

## Installation
Clone the Repository:
```bash
git clone https://github.com/naphattha/A-Financial-Knowledge-Graph-Construction-from-SET50-Annual-Reports.git
cd A-Financial-Knowledge-Graph-Construction-from-SET50-Annual-Reports
```

Set Up a Virtual Environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install Dependencies:
```bash
pip install -r requirements.txt
```

---

## Run the Application:
```bash
streamlit run app.py
```
