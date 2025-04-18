"""circuit cutting

Revision ID: 10775e5e3f9a
Revises: 9aac847198b4
Create Date: 2024-11-11 16:54:10.413007

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "10775e5e3f9a"
down_revision = "9aac847198b4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("Job", schema=None) as batch_op:
        batch_op.add_column(sa.Column("cut_to_width", sa.INTEGER(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("Job", schema=None) as batch_op:
        batch_op.drop_column("cut_to_width")

    # ### end Alembic commands ###
