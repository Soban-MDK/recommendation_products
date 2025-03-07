# from main.customer_process import get_sales_details_data, data_processing, update_recommendations_efficient

# df = get_sales_details_data()
# df = data_processing(df)
# update_recommendations_efficient(df)
# print("DONE")
# # print(df.head())

from main.customer_process import update_recommendations_and_mark_processed
update_recommendations_and_mark_processed()
print("DONE")
