"""photos table from SQLA model"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '202406_photos_table_from_sqla_model'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'photos',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('geom', Geometry(geometry_type='POINT', srid=4326)),
        sa.Column('vlad', Vector(128)),
    )


def downgrade():
    op.drop_table('photos')
