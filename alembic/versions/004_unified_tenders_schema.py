
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004_unified_tenders_schema"
down_revision: Union[str, None] = None  
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создаёт единую схему: tenders + lots + индексы + триггер FTS"""
    
   
    op.create_table(
        "tenders",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("purchase_number", sa.String(length=30), unique=True, nullable=False, index=True),
        sa.Column("max_price", sa.Numeric(precision=15, scale=2)),
        sa.Column("currency", sa.String(length=3), server_default="RUB"),
        sa.Column("publish_date", sa.DateTime(timezone=True), index=True),
        sa.Column("submission_end", sa.DateTime(timezone=True), index=True),
        sa.Column("fz", sa.String(length=10), index=True),  # "44-ФЗ", "223-ФЗ"
        sa.Column("placing_way_code", sa.String(length=20), index=True),
        sa.Column("status", sa.String(length=50), index=True),
        sa.Column("customer_inn", sa.String(length=12), index=True),
        sa.Column("customer_name", sa.String(length=300), index=True),
        sa.Column("region", sa.String(length=100), index=True),  
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), comment="Исходные данные из ЕИС"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        
        
        sa.Column("search_vector", postgresql.TSVECTOR()),
    )
    
    
    op.create_index(
        "idx_tenders_search_composite",
        "tenders",
        ["publish_date", "max_price", "customer_inn", "fz", "status"],
        postgresql_include=["purchase_number", "customer_name"]  # Covering index
    )
    
    
    op.create_index("idx_tenders_raw_gin", "tenders", ["raw_data"], postgresql_using="gin")
    
    
    op.create_index(
        "idx_tenders_search_vector_gin",
        "tenders",
        ["search_vector"],
        postgresql_using="gin"
    )
    
    
    op.execute("""
        CREATE OR REPLACE FUNCTION trg_update_tenders_fts()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := 
                setweight(to_tsvector('russian', coalesce(NEW.customer_name, '')), 'A') ||
                setweight(to_tsvector('russian', coalesce(NEW.purchase_number, '')), 'B') ||
                setweight(to_tsvector('russian', coalesce(NEW.region, '')), 'C') ||
                setweight(to_tsvector('russian', coalesce(NEW.raw_data::text, '')), 'D');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE TRIGGER trigger_tenders_fts
        BEFORE INSERT OR UPDATE ON tenders
        FOR EACH ROW
        EXECUTE FUNCTION trg_update_tenders_fts();
    """)
    
    
    op.create_table(
        "lots",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("tender_id", sa.BigInteger(), sa.ForeignKey("tenders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lot_number", sa.Integer(), nullable=False),
        sa.Column("max_price", sa.Numeric(precision=15, scale=2)),
        sa.Column("currency", sa.String(length=3), server_default="RUB"),
        sa.Column("objects_description", postgresql.JSONB(astext_type=sa.Text()), comment="Описание объекта закупки, КТРУ"),
        sa.Column("guarantee_info", postgresql.JSONB(astext_type=sa.Text()), comment="Обеспечение заявки и контракта"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    
    op.create_index(
        "idx_lots_tender_lot_unique",
        "lots",
        ["tender_id", "lot_number"],
        unique=True
    )
    op.create_index("idx_lots_objects_gin", "lots", ["objects_description"], postgresql_using="gin")
    op.create_index("idx_lots_tender_id", "lots", ["tender_id"])  # Для JOIN при загрузке
    
    
    op.create_table(
        "tender_details",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("tender_id", sa.BigInteger(), sa.ForeignKey("tenders.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("collecting_start", sa.DateTime(timezone=True)),
        sa.Column("collecting_end", sa.DateTime(timezone=True), index=True),
        sa.Column("summarizing_date", sa.DateTime(timezone=True)),
        sa.Column("etp_name", sa.String(length=100)),
        sa.Column("etp_url", sa.String(length=300)),
        sa.Column("placing_way_name", sa.String(length=100)),
        sa.Column("lots_count", sa.Integer(), server_default="1"),
        sa.Column("is_goz", sa.Boolean(), server_default="false"),
        sa.Column("purchase_object_info", sa.Text()),
        sa.Column("raw_details", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_tender_details_tender_id", "tender_details", ["tender_id"], unique=True)


def downgrade() -> None:
    """Полный откат схемы"""
    
    
    op.execute("DROP TRIGGER IF EXISTS trigger_tenders_fts ON tenders;")
    op.execute("DROP FUNCTION IF EXISTS trg_update_tenders_fts;")
    
    
    op.drop_index("idx_tender_details_tender_id", table_name="tender_details")
    op.drop_index("idx_lots_tender_id", table_name="lots")
    op.drop_index("idx_lots_objects_gin", table_name="lots")
    op.drop_index("idx_lots_tender_lot_unique", table_name="lots")
    op.drop_index("idx_tenders_search_vector_gin", table_name="tenders")
    op.drop_index("idx_tenders_raw_gin", table_name="tenders")
    op.drop_index("idx_tenders_search_composite", table_name="tenders")
    
    
    op.drop_table("tender_details")
    op.drop_table("lots")
    op.drop_table("tenders")