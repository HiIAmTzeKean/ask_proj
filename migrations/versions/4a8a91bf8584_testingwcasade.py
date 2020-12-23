"""'testingwcasade'

Revision ID: 4a8a91bf8584
Revises: 4df595c6366b
Create Date: 2020-12-21 23:27:35.566134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a8a91bf8584'
down_revision = '4df595c6366b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('student_status_student_id_fkey', 'student_status', type_='foreignkey')
    op.create_foreign_key(None, 'student_status', 'student', ['student_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'student_status', type_='foreignkey')
    op.create_foreign_key('student_status_student_id_fkey', 'student_status', 'student', ['student_id'], ['id'])
    # ### end Alembic commands ###
