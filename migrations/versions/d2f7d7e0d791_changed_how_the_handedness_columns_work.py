"""changed how the handedness columns work

Revision ID: d2f7d7e0d791
Revises: 75db74e3f64d
Create Date: 2019-12-19 20:37:24.469791

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2f7d7e0d791'
down_revision = '75db74e3f64d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_lefty', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('is_righty', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_user_is_lefty'), 'user', ['is_lefty'], unique=False)
    op.create_index(op.f('ix_user_is_righty'), 'user', ['is_righty'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_is_righty'), table_name='user')
    op.drop_index(op.f('ix_user_is_lefty'), table_name='user')
    op.drop_column('user', 'is_righty')
    op.drop_column('user', 'is_lefty')
    # ### end Alembic commands ###
