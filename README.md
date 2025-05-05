# A Financial Knowledge Graph Construction from SET50 Annual Reports

This project constructs a Financial Knowledge Graph (KG) from the annual reports of SET50 companies. It enables users to query financial data through a chatbot interface, facilitating complex financial analysis. The project compares the performance and efficiency of two database systems: Neo4j (graph-based) and MySQL (relational).


# Project Structure

 * llm-chatbot-python-neo4j: Contains code for Neo4j database integration.
 * llm-chatbot-python-mysql: Contains code for MySQL database integration.

Each directory includes the necessary files to run an independent instance of the chatbot application.

# Prerequisites
Before setting up the project, ensure you have the following installed:
Python: Version 3.8 or higher.
Neo4j: Community or Enterprise Edition.
MySQL: Version 8.0 or higher.
Node.js and npm: For frontend development.

# Set Up Databases:
[A-Financial-Knowledge-Graph-SET50-Annual-Reports-database](https://github.com/naphattha/A-Financial-Knowledge-Graph-SET50-Annual-Reports-database)

# Installation
Clone the Repository:
git clone https://github.com/naphattha/A-Financial-Knowledge-Graph-Construction-from-SET50-Annual-Reports.git
cd A-Financial-Knowledge-Graph-Construction-from-SET50-Annual-Reports

Set Up a Virtual Environment:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies:
pip install -r requirements.txt

# Run the Application:
streamlit run app.py
