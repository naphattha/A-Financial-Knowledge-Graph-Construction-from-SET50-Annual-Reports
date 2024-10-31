import json
import mysql.connector

# MySQL connection setup
connection = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your MySQL username
    password="Wealth3visual%",  # Replace with your MySQL password
    database="financials"  # Replace with your database name
)
cursor = connection.cursor()

# Load JSON data
with open('FilteredFinancialData.json', 'r', encoding='utf-8') as file:
    financial_data = json.load(file)

# Define the SQL query
query = """
INSERT INTO financial_statements (
    symbol, year, quarter, financialStatementType, dateAsof, accountPeriod,
    totalAssets, totalLiabilities, paidupShareCapital, shareholderEquity,
    totalEquity, totalRevenueQuarter, totalRevenueAccum, totalExpensesQuarter,
    totalExpensesAccum, ebitQuarter, ebitAccum, netProfitQuarter, netProfitAccum,
    epsQuarter, epsAccum, operatingCashFlow, investingCashFlow, financingCashFlow,
    roe, roa, netProfitMarginQuarter, netProfitMarginAccum, de, fixedAssetTurnover,
    totalAssetTurnover
) VALUES (
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s, %s,
    %s, %s, %s, %s,%s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s,
    %s
)
"""

# Insert JSON data into MySQL table
for record in financial_data:
    # Prepare values with default None for missing fields
    values = (
        record.get('symbol'),
        int(record.get('year', 0)) if record.get('year') else None,  # Convert to integer, or None
        int(record.get('quarter', 0)) if record.get('quarter') else None,  # Convert to integer, or None
        record.get('financialStatementType'),
        record.get('dateAsof'),
        record.get('accountPeriod'),
        float(record.get('totalAssets', 0)) if record.get('totalAssets') else None,  # Convert to float, or None
        float(record.get('totalLiabilities', 0)) if record.get('totalLiabilities') else None,  # Convert to float, or None
        float(record.get('paidupShareCapital', 0)) if record.get('paidupShareCapital') else None,  # Convert to float, or None
        float(record.get('shareholderEquity', 0)) if record.get('shareholderEquity') else None,  # Convert to float, or None
        float(record.get('totalEquity', 0)) if record.get('totalEquity') else None,  # Convert to float, or None
        float(record.get('totalRevenueQuarter', 0)) if record.get('totalRevenueQuarter') else None,  # Convert to float, or None
        float(record.get('totalRevenueAccum', 0)) if record.get('totalRevenueAccum') else None,  # Convert to float, or None
        float(record.get('totalExpensesQuarter', 0)) if record.get('totalExpensesQuarter') else None,  # Convert to float, or None
        float(record.get('totalExpensesAccum', 0)) if record.get('totalExpensesAccum') else None,  # Convert to float, or None
        float(record.get('ebitQuarter', 0)) if record.get('ebitQuarter') else None,  # Convert to float, or None
        float(record.get('ebitAccum', 0)) if record.get('ebitAccum') else None,  # Convert to float, or None
        float(record.get('netProfitQuarter', 0)) if record.get('netProfitQuarter') else None,  # Convert to float, or None
        float(record.get('netProfitAccum', 0)) if record.get('netProfitAccum') else None,  # Convert to float, or None
        float(record.get('epsQuarter', 0)) if record.get('epsQuarter') else None,  # Convert to float, or None
        float(record.get('epsAccum', 0)) if record.get('epsAccum') else None,  # Convert to float, or None
        float(record.get('operatingCashFlow', 0)) if record.get('operatingCashFlow') else None,  # Convert to float, or None
        float(record.get('investingCashFlow', 0)) if record.get('investingCashFlow') else None,  # Convert to float, or None
        float(record.get('financingCashFlow', 0)) if record.get('financingCashFlow') else None,  # Convert to float, or None
        float(record.get('roe', 0)) if record.get('roe') else None,  # Convert to float, or None
        float(record.get('roa', 0)) if record.get('roa') else None,  # Convert to float, or None
        float(record.get('netProfitMarginQuarter', 0)) if record.get('netProfitMarginQuarter') else None,  # Convert to float, or None
        float(record.get('netProfitMarginAccum', 0)) if record.get('netProfitMarginAccum') else None,  # Convert to float, or None
        float(record.get('de', 0)) if record.get('de') else None,  # Convert to float, or None
        float(record.get('fixedAssetTurnover', 0)) if record.get('fixedAssetTurnover') else None,  # Convert to float, or None
        float(record.get('totalAssetTurnover', 0)) if record.get('totalAssetTurnover') else None  # Convert to float, or None
    )
    
    cursor.execute(query, values)

# Commit the transaction
connection.commit()

# Close the connection
cursor.close()
connection.close()

import json
import mysql.connector

# MySQL connection setup
connection = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your MySQL username
    password="Wealth3visual%",  # Replace with your MySQL password
    database="financials"  # Replace with your database name
)
cursor = connection.cursor()

# Load JSON data
with open('FilteredEODData.json', 'r', encoding='utf-8') as file:
    eod_data = json.load(file)

# Insert JSON data into MySQL table
for record in eod_data:
    query = """
    INSERT INTO FilteredEODData (date, symbol, securityType, adjustedPriceFlag, prior, open, high, low, close, average, aomVolume, aomValue, trVolume, trValue, totalVolume, totalValue, pe, pbv, bvps, dividendYield, marketCap, volumeTurnover)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        record['date'],
        record['symbol'],
        record['securityType'],
        record['adjustedPriceFlag'],
        record['prior'],
        record['open'],
        record['high'],
        record['low'],
        record['close'],
        record['average'],
        record['aomVolume'],
        record['aomValue'],
        record['trVolume'],
        record['trValue'],
        record['totalVolume'],
        record['totalValue'],
        record['pe'],
        record['pbv'],
        record['bvps'],
        record['dividendYield'],
        record['marketCap'],
        record['volumeTurnover']
    )
    cursor.execute(query, values)

# Commit the transaction
connection.commit()

# Close the connection
cursor.close()
connection.close()

