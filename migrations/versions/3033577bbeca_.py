"""empty message

Revision ID: 3033577bbeca
Revises: 77c31d07e64d
Create Date: 2021-06-12 09:13:13.563903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3033577bbeca'
down_revision = '77c31d07e64d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pois', sa.Column('altitude', sa.FLOAT(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pois', 'altitude')
    # ### end Alembic commands ###
