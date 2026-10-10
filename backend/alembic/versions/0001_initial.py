from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("projects", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("description", sa.Text()), sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("repository_url", sa.String(500)), sa.Column("default_branch", sa.String(120), nullable=False), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()))
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])
    op.create_table("builds", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("image_name", sa.String(255)), sa.Column("image_tag", sa.String(120)), sa.Column("commit_sha", sa.String(64)), sa.Column("logs", sa.Text(), nullable=False), sa.Column("started_at", sa.DateTime()), sa.Column("completed_at", sa.DateTime()))
    op.create_index("ix_builds_project_id", "builds", ["project_id"])
    op.create_table("deployments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False), sa.Column("build_id", sa.Integer(), sa.ForeignKey("builds.id", ondelete="RESTRICT"), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("environment", sa.String(50), nullable=False), sa.Column("image_name", sa.String(255), nullable=False), sa.Column("container_id", sa.String(255)), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()), sa.Column("started_at", sa.DateTime()), sa.Column("stopped_at", sa.DateTime()))
    op.create_index("ix_deployments_project_id", "deployments", ["project_id"])

def downgrade():
    op.drop_table("deployments"); op.drop_table("builds"); op.drop_table("projects"); op.drop_index("ix_users_email", table_name="users"); op.drop_table("users")
