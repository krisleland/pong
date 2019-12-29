"""removed handedness column

Revision ID: 90b8b3c9b7fe
Revises: d2f7d7e0d791
Create Date: 2019-12-19 20:38:07.702361

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90b8b3c9b7fe'
down_revision = 'd2f7d7e0d791'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_handedness', table_name='user')
    op.drop_column('user', 'handedness')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('handedness', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
    op.create_index('ix_user_handedness', 'user', ['handedness'], unique=False)
    # ### end Alembic commands ###
