"""empty message

Revision ID: 63a624a32596
Revises: 91fb8fb2a50b
Create Date: 2021-07-06 15:08:55.961216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63a624a32596'
down_revision = '91fb8fb2a50b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_flights', sa.Column('show_flight', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_flights', 'show_flight')
    # ### end Alembic commands ###
