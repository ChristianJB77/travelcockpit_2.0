"""empty message

Revision ID: 9842856aebe9
Revises: 88bbc83d3dc4
Create Date: 2021-03-06 12:47:35.794942

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9842856aebe9'
down_revision = '88bbc83d3dc4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('secrets', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'secrets', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'secrets', type_='foreignkey')
    op.drop_column('secrets', 'user_id')
    # ### end Alembic commands ###
