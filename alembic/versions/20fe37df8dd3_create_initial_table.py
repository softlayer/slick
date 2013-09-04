"""create initial tables

Revision ID: 20fe37df8dd3
Revises: None
Create Date: 2013-09-03 09:15:03.334658

"""

# revision identifiers, used by Alembic.
revision = '20fe37df8dd3'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.Unicode(255), index=True, nullable=False),
        sa.Column('use_two_factor', sa.Boolean, server_default='0',
                  nullable=False),
        sa.Column('phone_number', sa.Unicode(45)),
        sa.Column('use_sms', sa.Boolean, server_default='0', nullable=False)
    )

    op.create_table(
        'cci_template',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.Unicode(255), index=True, nullable=False),
        sa.Column('os', sa.Unicode(255)),
        sa.Column('cpus', sa.Integer, nullable=False, server_default='0'),
        sa.Column('memory', sa.Integer, nullable=False, server_default='0'),
        sa.Column('network', sa.Enum('10', '100', '1000')),
        sa.Column('private_network_only', sa.Boolean, nullable=False,
                  server_default='0'),
        sa.Column('dedicated_host', sa.Boolean, nullable=False,
                  server_default='0'),
        sa.Column('owner_id', sa.Integer, sa.ForeignKey('user.id'))
    )


def downgrade():
    op.drop_table('user')
    op.drop_table('cci_template')
