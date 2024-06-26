"""created all tables

Revision ID: 6fafc70bbb93
Revises: 
Create Date: 2024-06-16 01:47:46.257590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fafc70bbb93'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'order_vendor_association', 'orders', ['order_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.alter_column('orders', 'additional_note',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('orders', 'additional_note',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_constraint(None, 'order_vendor_association', type_='foreignkey')
    # ### end Alembic commands ###
