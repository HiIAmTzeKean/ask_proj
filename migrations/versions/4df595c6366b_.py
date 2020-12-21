"""empty message

Revision ID: 4df595c6366b
Revises: 8826fc2247c7
Create Date: 2020-12-19 23:45:29.099638

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4df595c6366b'
down_revision = '8826fc2247c7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('student_status', sa.Column('dojo_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'student_status', 'dojo', ['dojo_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'student_status', type_='foreignkey')
    op.drop_column('student_status', 'dojo_id')
    # ### end Alembic commands ###
