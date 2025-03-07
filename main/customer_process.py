from main.queries import GET_SALES_DETAILS_DATA, GET_EXISTING_RECOMMENDATIONS
from main.connections import connection_pos, conn_string_pos
from main.common_helpers import read_data
from main.models import RecommendationEngine
from utils.logger import logger, logging

from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func, text


import pandas as pd

def get_sales_details_data():
    try:
        conn = connection_pos()
        data = read_data(conn, GET_SALES_DETAILS_DATA)
        print(data)

        return data
    except Exception as e:
        logging()
        return


def data_processing(data):
    try:
        data['purchase_invoice_id'] = data['sales_invoice_id']

        data = data.groupby(['product_id','customer_id', 'mis_reporting_category']).agg({'quantity':'sum','sales_invoice_id':'nunique','bill_date':'max','purchase_invoice_id':'last'}).reset_index()

        data = data.rename(columns={
            'quantity':'total_qty',
            'sales_invoice_id':'total_bill_count',
            'bill_date':'last_purchase_bill_date', 
            'purchase_invoice_id':'last_purchase_invoice_id'
        })

        return data

    except Exception as e:
        logging()
        return


def update_recommendations(data):
    try:
        pos_string = conn_string_pos()
        engine = create_engine(pos_string)
        Session = sessionmaker(bind=engine)
        session = Session()

        for _, row in data.iterrows():
            # Try to find existing record
            existing_record = session.query(RecommendationEngine).filter(
                and_(
                    RecommendationEngine.product_id == row['product_id'],
                    RecommendationEngine.customer_id == row['customer_id'],
                    RecommendationEngine.mis_reporting_category == row['mis_reporting_category'],
                    RecommendationEngine.deleted_at.is_(None)
                )
            ).first()

            if existing_record:
                # Update existing record
                existing_record.total_qty += row['total_qty']
                existing_record.total_bill_count += row['total_bill_count']
                existing_record.last_purchase_bill_date = max(
                    existing_record.last_purchase_bill_date,
                    row['last_purchase_bill_date']
                )
                existing_record.last_purchase_invoice_id = row['last_purchase_invoice_id']
                existing_record.updated_at = datetime.now()
            
            else:
                # Create new record
                new_record = RecommendationEngine(
                    product_id=row['product_id'],
                    customer_id=row['customer_id'],
                    mis_reporting_category=row['mis_reporting_category'],
                    total_qty=row['total_qty'],
                    total_bill_count=row['total_bill_count'],
                    last_purchase_bill_date=row['last_purchase_bill_date'],
                    last_purchase_invoice_id=row['last_purchase_invoice_id'],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                session.add(new_record)

        session.commit()
        logger.info("Successfully updated recommendation engine entries")
        return True

    except Exception as e:
        logging()
        session.rollback()
        return False

    finally:
        session.close()


def update_recommendations_and_mark_processed():
    try:
        data = get_sales_details_data()
        pos_string = conn_string_pos()
        engine = create_engine(pos_string)
        
        processed_invoice_ids = data['sales_invoice_id'].unique().tolist()
        
        grouped_data = data_processing(data)
        
        try:
            success = update_recommendations(grouped_data)
        except Exception as e:
            logger.warning(f"Efficient update failed, falling back to standard update: {e}")
            logging()
            return
            # success = update_recommendations(grouped_data)
            
        if not success:
            logger.error("Failed to update recommendations, skipping invoice status update")
            return False
            
        with engine.connect() as connection:
            invoice_ids_str = ','.join(str(id) for id in processed_invoice_ids)
            
            update_query = text(f"""
                UPDATE sales_invoices 
                SET is_recommendation_data_updated = true
                WHERE id IN ({invoice_ids_str})
            """)
            
            connection.execute(update_query)
            connection.commit()
            
            logger.info(f"Successfully marked {len(processed_invoice_ids)} sales invoices as processed")
            
        return True
        
    except Exception as e:
        logger.error(f"Error in update_recommendations_and_mark_processed: {e}")
        return False


def update_recommendations_efficient(data):
    try:
        pos_string = conn_string_pos()
        engine = create_engine(pos_string)
        Session = sessionmaker(bind=engine)
        session = Session()

        now = datetime.now()
        records = [
            {**row.to_dict(), "created_at": now, "updated_at": now}
            for _, row in data.iterrows()
        ]

        stmt = insert(RecommendationEngine).values(records)

        stmt = stmt.on_conflict_do_update(
            index_elements=["product_id", "customer_id", "mis_reporting_category"],  # Use columns directly
            set_={
                "total_qty": RecommendationEngine.total_qty + stmt.excluded.total_qty,
                "total_bill_count": RecommendationEngine.total_bill_count + stmt.excluded.total_bill_count,
                "last_purchase_bill_date": func.greatest(
                    RecommendationEngine.last_purchase_bill_date, stmt.excluded.last_purchase_bill_date
                ),
                "last_purchase_invoice_id": stmt.excluded.last_purchase_invoice_id,
                "updated_at": now
            }
        )

        session.execute(stmt)
        session.commit()
        logger.info("Successfully updated recommendation engine entries")
        return True

    except Exception as e:
        logger.error(f"Error updating recommendations: {e}")
        session.rollback()
        return False

    finally:
        session.close()
