import pandas as pd
import sqlite3

def process_data():

    # Loading the transactions data from the CSV file into a pandas DataFrame
    file_path = r"src/data/transactions.csv" 
    df = pd.read_csv(file_path, encoding="utf-8")
    
    # Removing any rows with missing values in the DataFrame (Use dropna or another method)
    df.dropna(inplace=True)  # You can change this to other methods if required

    # Converting the 'TransactionDate' column to a datetime format using pandas
    df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], format="%Y-%m-%d")

    # Setting up a connection to SQLite database and create a table if it doesn't exist
    conn = sqlite3.connect("src/data/transactions.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product TEXT,
        amount REAL,
        TransactionDate TEXT,
        PaymentMethod TEXT,
        City TEXT,
        Category TEXT
    )
    """)

    # Cleaning the CustomerID column by removing 'CUST' prefix and converting to integer
    df["CustomerID"] = df["CustomerID"].str.replace("CUST", "").astype(int)

    # Renaming columns to match the database schema
    df.rename(columns={
        "TransactionID": "transaction_id",
        "CustomerID": "customer_id",
        "Product": "product",
        "Amount": "amount"
    }, inplace=True)
    
    # TO DO: Insert data into the database
    # Your task: Insert the cleaned DataFrame into the SQLite database. Ensure to replace the table if it already exists.
    df.to_sql("transactions", conn, if_exists="replace", index=False)


    # Example Queries - Write SQL queries based on the instructions below

    # TO DO: Query for Top 5 Most Sold Products
    # Your task: Write an SQL query to find the top 5 most sold products based on transaction count.
    cursor.execute("""
        SELECT product,
               COUNT(*) as transaction_count
        FROM transactions
        GROUP BY product
        ORDER BY transaction_count DESC
        LIMIT 5
                   """)
    
    top_products = cursor.fetchall()
    print("\n🏆 Top 5 Most Sold Products:")
    for row in top_products:
        print(f"  Product: {row[0]}, Number Sold: {row[1]}")


    # TO DO:  Query for Monthly Revenue Trend
    # Your task: Write an SQL query to find the total revenue per month.
    cursor.execute("""
        SELECT strftime('%Y-%m', TransactionDate) as month, 
               ROUND(SUM(amount), 2) as total_revenue
        FROM transactions
        GROUP BY month
        ORDER BY month ASC
                   """)
    
    monthly_revenue = cursor.fetchall()
    print("\n📅 Monthly Revenue Trend:")
    for row in monthly_revenue:
        print(f"  Month: {row[0]}, Total Revenue: ${row[1]}")


    # TO DO:  Query for Payment Method Popularity
    # Your task: Write an SQL query to find the popularity of each payment method used in transactions.
    cursor.execute("""
        SELECT PaymentMethod, 
               COUNT(*) as transaction_count,
               ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 1) as percentage
        FROM transactions
        GROUP BY PaymentMethod
        ORDER BY transaction_count DESC
                   """)
    
    payment_methods = cursor.fetchall()
    print("\n💳 Payment Method Popularity:")
    for row in payment_methods:
        print(f"  Payment Method: {row[0]:<12}, Transactions: {row[1]:>9,}, Share: {row[2]:>5.1f}%")


    # TO DO:  Query for Top 5 Cities with Most Transactions
    # Your task: Write an SQL query to find the top 5 cities with the most transactions.
    cursor.execute("""
        SELECT City,
               COUNT(*) as transaction_count
        FROM transactions
        GROUP BY City
        ORDER BY transaction_count DESC
        LIMIT 5
                   """)
    
    top_cities = cursor.fetchall()
    print("\n🏙️ Top 5 Cities with Most Transactions:")
    for row in top_cities:
        print(f"  City: {row[0]}, Transactions: {row[1]}")


    # TO DO:  Query for Top 5 High-Spending Customers
    # Your task: Write an SQL query to find the top 5 customers who spent the most in total.
    cursor.execute("""
        SELECT customer_id,
               ROUND(SUM(amount), 2) as total_spent,
               COUNT(*) as transaction_count
        FROM transactions
        GROUP BY customer_id
        ORDER BY total_spent DESC
        LIMIT 5
                   """)
    
    top_customers = cursor.fetchall()
    print("\n💰 Top 5 High-Spending Customers:")
    for row in top_customers:
        print(f"  Customer ID: {row[0]}, Total Spent: ${row[1]}, Transactions: {row[2]}")


    # TO DO:  Query for Hadoop vs Spark Related Product Sales
    # Your task: Write an SQL query to categorize products related to Hadoop and Spark and find their sales.
    cursor.execute("""
        SELECT 
            CASE 
                WHEN product LIKE '%Hadoop%' THEN 'Hadoop'
                WHEN product LIKE '%Spark%' THEN 'Spark'
            END as category,
            COUNT(*) as transaction_count,
            ROUND(SUM(amount), 2) as total_revenue
        FROM transactions
        WHERE product LIKE '%Hadoop%' OR product LIKE '%Spark%'
        GROUP BY 
            CASE
                WHEN product LIKE '%Hadoop%' THEN 'Hadoop'
                WHEN product LIKE '%Spark%' THEN 'Spark'
            END
        ORDER BY total_revenue DESC
                   """)
    
    hadoop_spark_sales = cursor.fetchall()
    print("\n🐘 Hadoop vs ⚡ Spark Related Product Sales:")
    for row in hadoop_spark_sales:
        print(f"  Category: {row[0]}, Transactions: {row[1]}, Total Revenue: ${row[2]}")


    # TO DO:  Query for Top Spending Customers in Each City
    # Your task: Write an SQL query to find the top spending customer in each city using subqueries.
    cursor.execute("""
        SELECT city_spending.City,
               city_spending.customer_id,
               city_spending.total_spent
        FROM (
            SELECT City,
                   customer_id,
                   ROUND(SUM(amount), 2) as total_spent
            FROM transactions
            GROUP BY City, customer_id
        ) as city_spending
        WHERE city_spending.total_spent = (
            SELECT MAX(inner_spending.total_spent)
            FROM (
                SELECT City,
                       customer_id,
                       ROUND(SUM(amount), 2) as total_spent
                FROM transactions
                GROUP BY City, customer_id
            ) as inner_spending
            WHERE inner_spending.City = city_spending.City
        )
        ORDER BY city_spending.total_spent DESC
                   """)
    
    top_city_customers = cursor.fetchall()
    print("\n🤑 Top Spending Customer in Each City:")
    for row in top_city_customers:
        print(f"  City: {row[0]}, Customer ID: {row[1]}, Total Spent: ${row[2]}")


    # Step 8: Close the connection
    # Your task: After all queries, make sure to commit any changes and close the connection
    conn.commit()
    conn.close()
    print("\n✅ Data Processing & Advanced Analysis Completed Successfully!")

if __name__ == "__main__":
    process_data()
