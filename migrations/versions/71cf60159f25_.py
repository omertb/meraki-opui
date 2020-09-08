"""empty message

Revision ID: 71cf60159f25
Revises: 38647aca04e3
Create Date: 2020-09-08 18:04:40.488421

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71cf60159f25'
down_revision = '38647aca04e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'operator',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'operator',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    # ### end Alembic commands ###
