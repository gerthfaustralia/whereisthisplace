"""add prediction metadata columns"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '202406_add_prediction_columns'
down_revision = '202405_add_photos_table'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('photos', sa.Column('score', sa.Float()))
    op.add_column('photos', sa.Column('bias_warning', sa.String()))
    op.add_column('photos', sa.Column('source', sa.String()))


def downgrade():
    op.drop_column('photos', 'source')
    op.drop_column('photos', 'bias_warning')
    op.drop_column('photos', 'score')
