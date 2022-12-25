"""Initial migration

Revision ID: 4910626a5885
Revises: 
Create Date: 2022-12-16 18:45:45.960371

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4910626a5885'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('habits',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('trackers',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('habit_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['habit_id'], ['habits.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trackers')
    op.drop_table('habits')
    # ### end Alembic commands ###