CREATE INDEX IF NOT EXISTS idx_cancel ON "Retail Data"(CustomerID, StockCode, Quantity);

-- All queries use the same cleaning rules as cleaning.py:
-- no cancellations, no zero/negative quantity or price,
-- no non-product codes, and no orders that were later cancelled.

-- Query 1: Which countries have the most orders?

WITH clean_sales AS (
    SELECT r.*
    FROM "Retail Data" r
    WHERE r.InvoiceNo NOT LIKE 'C%'
      AND r.Quantity > 0
      AND r.UnitPrice > 0
      AND UPPER(r.StockCode) NOT IN ('POST', 'DOT', 'M', 'D', 'C2', 'S', 'B',
                                     'BANK CHARGES', 'AMAZONFEE', 'CRUK', 'PADS')
      AND NOT EXISTS (
          SELECT 1 FROM "Retail Data" c
          WHERE c.InvoiceNo LIKE 'C%'
            AND c.CustomerID = r.CustomerID
            AND c.StockCode = r.StockCode
            AND c.Quantity = -r.Quantity
      )
)
SELECT Country, COUNT(DISTINCT InvoiceNo) AS num_orders
FROM clean_sales
GROUP BY Country
ORDER BY num_orders DESC
LIMIT 10;


-- Query 2: What are the top 10 best-selling products by quantity?

WITH clean_sales AS (
    SELECT r.*
    FROM "Retail Data" r
    WHERE r.InvoiceNo NOT LIKE 'C%'
      AND r.Quantity > 0
      AND r.UnitPrice > 0
      AND UPPER(r.StockCode) NOT IN ('POST', 'DOT', 'M', 'D', 'C2', 'S', 'B',
                                     'BANK CHARGES', 'AMAZONFEE', 'CRUK', 'PADS')
      AND NOT EXISTS (
          SELECT 1 FROM "Retail Data" c
          WHERE c.InvoiceNo LIKE 'C%'
            AND c.CustomerID = r.CustomerID
            AND c.StockCode = r.StockCode
            AND c.Quantity = -r.Quantity
      )
)
SELECT Description, SUM(Quantity) AS total_quantity
FROM clean_sales
WHERE Description IS NOT NULL
GROUP BY Description
ORDER BY total_quantity DESC
LIMIT 10;


-- Query 3: Which customers spend the most money?

WITH clean_sales AS (
    SELECT r.*
    FROM "Retail Data" r
    WHERE r.InvoiceNo NOT LIKE 'C%'
      AND r.Quantity > 0
      AND r.UnitPrice > 0
      AND UPPER(r.StockCode) NOT IN ('POST', 'DOT', 'M', 'D', 'C2', 'S', 'B',
                                     'BANK CHARGES', 'AMAZONFEE', 'CRUK', 'PADS')
      AND NOT EXISTS (
          SELECT 1 FROM "Retail Data" c
          WHERE c.InvoiceNo LIKE 'C%'
            AND c.CustomerID = r.CustomerID
            AND c.StockCode = r.StockCode
            AND c.Quantity = -r.Quantity
      )
)
SELECT CustomerID,
       COUNT(DISTINCT InvoiceNo) AS num_orders,
       ROUND(SUM(Quantity * UnitPrice), 2) AS total_spent
FROM clean_sales
WHERE CustomerID IS NOT NULL
GROUP BY CustomerID
ORDER BY total_spent DESC
LIMIT 10;