"""empty message

Revision ID: 68b864673cd6
Revises: 21b9ad6ba5c4
Create Date: 2016-10-21 20:08:24.130994

"""

# revision identifiers, used by Alembic.
revision = '68b864673cd6'
down_revision = '21b9ad6ba5c4'

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reportedseeds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('reporter', sa.Integer(), nullable=True),
    sa.Column('seed', sa.Integer(), nullable=True),
    sa.Column('reason', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['reporter'], ['users.id'], ),
    sa.ForeignKeyConstraint(['seed'], ['seeds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('seeds', sa.Column('report_count', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('seeds', 'report_count')
    op.drop_table('reportedseeds')
    ### end Alembic commands ###
