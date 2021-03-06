"""empty message

Revision ID: d5c463fee2c6
Revises: 3560fb0f9bc0
Create Date: 2020-12-15 13:47:34.559831

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd5c463fee2c6'
down_revision = '3560fb0f9bc0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('flightplan', sa.Column('number_flown', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('flightplan', 'number_flown')
    # ### end Alembic commands ###
