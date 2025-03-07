from sqlalchemy import Column, BigInteger, String, Date, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class RecommendationEngine(Base):
    __tablename__ = 'recommendation_engine'

    product_id = Column(BigInteger, primary_key=True, nullable=False)
    customer_id = Column(BigInteger, primary_key=True, nullable=False)
    total_bill_count = Column(BigInteger, default=0)
    last_purchase_bill_date = Column(Date)
    mis_reporting_category = Column(String(255), primary_key=True)
    last_purchase_invoice_id = Column(BigInteger)
    total_qty = Column(BigInteger, default=0)
    created_at = Column(Date)
    updated_at = Column(Date)
    deleted_at = Column(Date, nullable=True, default=None)

    __table_args__ = (
        UniqueConstraint('product_id', 'customer_id', 'mis_reporting_category', 
                        name='uix_recommendation_composite'),
    )