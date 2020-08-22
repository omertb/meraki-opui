"""empty message

Revision ID: fd665f0a8d79
Revises: 5652a4cf5cf3
Create Date: 2020-08-13 13:58:49.948227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd665f0a8d79'
down_revision = '5652a4cf5cf3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('templates', sa.Column('template_user', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'templates', 'users', ['template_user'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'templates', type_='foreignkey')
    op.drop_column('templates', 'template_user')
    # ### end Alembic commands ###