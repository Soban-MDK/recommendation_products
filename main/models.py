from sqlalchemy import Column, BigInteger, String, Date, UniqueConstraint, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from main.connections import conn_string_pos

Base = declarative_base()

class RecommendationEngine(Base):
    __tablename__ = 'personalized_recommendations'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    product_id = Column(BigInteger, nullable=False)
    customer_id = Column(BigInteger, nullable=False)
    total_bill_count = Column(BigInteger, default=0)
    last_purchase_bill_date = Column(Date)
    mis_reporting_category = Column(String(255))
    last_purchase_invoice_id = Column(BigInteger)
    total_qty = Column(BigInteger, default=0)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    deleted_at = Column(TIMESTAMP, nullable=True, default=None)

    __table_args__ = (
        UniqueConstraint('product_id', 'customer_id', name='uix_recommendation_composite'),
    )

engine_pos = create_engine(conn_string_pos())
Base.metadata.create_all(bind=engine_pos)