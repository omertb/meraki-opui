"""empty message

Revision ID: 5652a4cf5cf3
Revises: d15b360e4132
Create Date: 2020-08-13 13:43:46.598009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5652a4cf5cf3'
down_revision = 'd15b360e4132'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('networks', sa.Column('bound_template', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'networks', 'templates', ['bound_template'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'networks', type_='foreignkey')
    op.drop_column('networks', 'bound_template')
    # ### end Alembic commands ###
