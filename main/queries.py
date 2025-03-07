# Add the flag as well from sales_invoices table
GET_SALES_DETAILS_DATA = '''
SELECT 
    si.id as sales_invoice_id, 
    si.is_recommendation_data_updated as flag,
    sid.product_id,
    date(sid.created_at) as bill_date,
    sid.quantity, 
    si.customer_id, 
    p.mis_reporting_category
FROM sales_invoice_details sid
JOIN sales_invoices si on si.id = sid.sales_invoice_id
JOIN products p on p.id = sid.product_id
WHERE si.is_recommendation_data_updated = false
'''


GET_EXISTING_RECOMMENDATIONS = """
SELECT product_id, customer_id, mis_reporting_category, created_at, deleted_at 
FROM recommendation_engine 
WHERE deleted_at IS NULL;
"""