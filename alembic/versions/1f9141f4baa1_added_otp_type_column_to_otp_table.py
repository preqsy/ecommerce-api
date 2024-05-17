"""added otp_type column to OTP table

Revision ID: 1f9141f4baa1
Revises: 3912cf353291
Create Date: 2024-05-16 08:27:25.921250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f9141f4baa1'
down_revision: Union[str, None] = '3912cf353291'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('otp', sa.Column('otp_type', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('otp', 'otp_type')
    # ### end Alembic commands ###
