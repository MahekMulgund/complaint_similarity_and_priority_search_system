from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ==============================================================================
# 1. DEPARTMENTS TABLE
# ==============================================================================
class Department(db.Model):
    """
    Catalog of institutional service departments.
    Maintains clean separation from complaint categories.
    """
    __tablename__ = 'departments'

    department_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    categories = db.relationship('Category', backref='department', lazy=True)
    staff_members = db.relationship('User', backref='department', lazy=True)

    def __repr__(self):
        return f"<Department {self.department_id}: {self.department_name}>"


# ==============================================================================
# 2. CATEGORIES TABLE
# ==============================================================================
class Category(db.Model):
    """
    Complaint categories mapped directly to responsible departments.
    Used for candidate filtering in similarity comparisons and admin routing.
    """
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_id = db.Column(
        db.Integer,
        db.ForeignKey('departments.department_id', ondelete='RESTRICT'),
        nullable=False
    )
    category_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    complaints = db.relationship('Complaint', backref='category', lazy=True)
    issue_groups = db.relationship('IssueGroup', backref='category', lazy=True)

    def __repr__(self):
        return f"<Category {self.category_id}: {self.category_name}>"


# ==============================================================================
# 3. USERS TABLE
# ==============================================================================
class User(UserMixin, db.Model):
    """
    System users supporting all 3 SRS roles: user, admin, staff.
    Staff users are linked to a specific department.
    """
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    department_id = db.Column(
        db.Integer,
        db.ForeignKey('departments.department_id', ondelete='SET NULL'),
        nullable=True
    )
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum('user', 'admin', 'staff', name='user_roles'),
        nullable=False,
        default='user'
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submitted_complaints = db.relationship('Complaint', backref='author', lazy=True)
    history_actions = db.relationship('ComplaintHistory', backref='actor', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f"<User {self.user_id}: {self.email} ({self.role})>"


# ==============================================================================
# 4. ISSUE GROUPS TABLE
# ==============================================================================
class IssueGroup(db.Model):
    """
    Clusters of recurring similar complaints discovered by Module 3 (Similarity).
    Maintains the aggregate complaint count (Factor 1 for Priority).
    """
    __tablename__ = 'issue_groups'

    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.category_id', ondelete='RESTRICT'),
        nullable=False
    )
    group_title = db.Column(db.String(150), nullable=False)
    complaint_count = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    complaints = db.relationship('Complaint', backref='issue_group', lazy=True)
    similarity_records = db.relationship('SimilarityRecord', backref='issue_group', lazy=True)

    def __repr__(self):
        return f"<IssueGroup {self.group_id}: {self.group_title} (Count: {self.complaint_count})>"


# ==============================================================================
# 5. COMPLAINTS TABLE (THE ONE COMMON MODEL)
# ==============================================================================
class Complaint(db.Model):
    """
    THE SINGLE SOURCE OF TRUTH FOR COMPLAINTS.
    Both Member 1 and Member 2 must use these exact field names.
    Queue lifecycle and resolution statuses are tracked in separate fields.
    """
    __tablename__ = 'complaints'

    complaint_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='RESTRICT'),
        nullable=False
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.category_id', ondelete='RESTRICT'),
        nullable=False
    )
    group_id = db.Column(
        db.Integer,
        db.ForeignKey('issue_groups.group_id', ondelete='SET NULL'),
        nullable=True
    )

    # Content Fields
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cleaned_description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=False)

    # Priority Input Attributes
    severity = db.Column(db.Integer, nullable=False)  # 1 (Low) to 5 (Critical)
    affected_users = db.Column(db.Integer, nullable=False, default=1)

    # Algorithmic Output Attributes (Calculated by Member 2)
    similarity_score = db.Column(db.Numeric(5, 4), nullable=True)  # 0.0000 to 1.0000
    priority_score = db.Column(db.Numeric(5, 2), nullable=True)    # 0.00 to 100.00
    priority_level = db.Column(
        db.Enum('Low', 'Medium', 'High', 'Critical', name='priority_levels'),
        nullable=True
    )

    # Separate Status Lifecycle Fields
    queue_status = db.Column(
        db.Enum(
            'Queued', 'Processing', 'Processed', 'Failed', 'Needs Review',
            name='queue_statuses'
        ),
        nullable=False,
        default='Queued'
    )
    resolution_status = db.Column(
        db.Enum(
            'Open', 'Assigned', 'In Progress', 'Resolved', 'Closed',
            name='resolution_statuses'
        ),
        nullable=False,
        default='Open'
    )

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    similarity_evaluations = db.relationship(
        'SimilarityRecord',
        foreign_keys='SimilarityRecord.complaint_id',
        backref='analyzed_complaint',
        lazy=True,
        cascade='all, delete-orphan'
    )
    history = db.relationship(
        'ComplaintHistory',
        backref='complaint',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Complaint {self.complaint_id}: {self.title} [Prio: {self.priority_level}, Res: {self.resolution_status}]>"


# ==============================================================================
# 6. SIMILARITY RECORDS TABLE
# ==============================================================================
class SimilarityRecord(db.Model):
    """
    Audit log of TF-IDF and Cosine Similarity comparisons.
    Provides mathematical evidence of matches and clustering decisions.
    """
    __tablename__ = 'similarity_records'

    similarity_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey('complaints.complaint_id', ondelete='CASCADE'),
        nullable=False
    )
    compared_complaint_id = db.Column(
        db.Integer,
        db.ForeignKey('complaints.complaint_id', ondelete='SET NULL'),
        nullable=True
    )
    group_id = db.Column(
        db.Integer,
        db.ForeignKey('issue_groups.group_id', ondelete='CASCADE'),
        nullable=False
    )
    similarity_score = db.Column(db.Numeric(5, 4), nullable=False)
    threshold_used = db.Column(db.Numeric(5, 4), nullable=False)
    decision = db.Column(
        db.Enum('Merged', 'New Group', name='similarity_decisions'),
        nullable=False
    )
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SimilarityRecord {self.similarity_id}: Score {self.similarity_score} -> {self.decision}>"


# ==============================================================================
# 7. COMPLAINT HISTORY TABLE
# ==============================================================================
class ComplaintHistory(db.Model):
    """
    Complete audit trail of all queue and resolution status changes.
    actor_id is NULL for autonomous system actions (e.g. Queue Processor).
    """
    __tablename__ = 'complaint_history'

    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    complaint_id = db.Column(
        db.Integer,
        db.ForeignKey('complaints.complaint_id', ondelete='CASCADE'),
        nullable=False
    )
    actor_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id', ondelete='SET NULL'),
        nullable=True
    )
    status_type = db.Column(
        db.Enum('queue_status', 'resolution_status', name='history_status_types'),
        nullable=False
    )
    old_value = db.Column(db.String(50), nullable=False)
    new_value = db.Column(db.String(50), nullable=False)
    remarks = db.Column(db.Text, nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ComplaintHistory {self.history_id}: {self.status_type} ({self.old_value} -> {self.new_value})>"
