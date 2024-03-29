"""empty message

Revision ID: fb2940f8b100
Revises: None
Create Date: 2016-08-20 01:24:52.114819

"""

# revision identifiers, used by Alembic.
revision = 'fb2940f8b100'
down_revision = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('circles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('center_lat', sa.Float(), nullable=True),
    sa.Column('center_lng', sa.Float(), nullable=True),
    sa.Column('point', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326), nullable=True),
    sa.Column('radius', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=40), nullable=True),
    sa.Column('last_initial', sa.String(length=40), nullable=True),
    sa.Column('username', sa.String(length=40), nullable=True),
    sa.Column('notifications', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('seeds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('circle_id', sa.Integer(), nullable=True),
    sa.Column('seeder_id', sa.Integer(), nullable=True),
    sa.Column('isActive', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['circle_id'], ['circles.id'], ),
    sa.ForeignKeyConstraint(['seeder_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('seeds')
    op.drop_table('users')
    op.drop_table('circles')
    ### end Alembic commands ###
