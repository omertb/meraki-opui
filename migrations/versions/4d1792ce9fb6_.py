"""empty message

Revision ID: 4d1792ce9fb6
Revises: e66b80c6a610
Create Date: 2020-08-29 14:46:45.747744

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d1792ce9fb6'
down_revision = 'e66b80c6a610'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ownership',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('network_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.ForeignKeyConstraint(['network_id'], ['networks.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'network_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ownership')
    # ### end Alembic commands ###
