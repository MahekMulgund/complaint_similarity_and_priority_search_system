"""
Pipeline Orchestrator & Priority Calculation Engine
Contains the mathematical priority calculation rules and temporary mock pipeline.

================================================================================
WARNING: TEMPORARY MOCK PIPELINE ACTIVE
The similarity clustering in this file is a temporary stub to facilitate
independent UI development for Member 1. Member 2 will provide the true
NLTK preprocessing, TF-IDF vectorization, and Cosine similarity engine.
================================================================================
"""
from datetime import datetime
from config import Config


def calculate_priority_score(count: int, severity: int, affected: int, created_at: datetime, current_time=None) -> dict:
    """
    Computes the standardized, weighted priority score and classification level.

    Guarantees:
    - All 4 weights sum to exactly 1.0.
    - Each normalized factor is clamped strictly between 0.0 and 100.0.
    - Final priority score is clamped strictly between 0.00 and 100.00.
    - Classifications match approved boundaries:
        Low:      [0.00, 40.00)
        Medium:   [40.00, 70.00)
        High:     [70.00, 85.00)
        Critical: [85.00, 100.00]
    """
    if current_time is None:
        current_time = datetime.utcnow()

    weights = Config.PRIORITY_WEIGHTS
    c_max = Config.PRIORITY_C_MAX
    u_max = Config.PRIORITY_U_MAX
    decay_rate = Config.PRIORITY_RECENCY_DECAY

    # Validate weight sum constraint
    total_weights = sum(weights.values())
    if abs(total_weights - 1.0) > 1e-6:
        raise ValueError(f"Priority weights must sum to 1.0, but got {total_weights:.4f}")

    # 1. Normalize Similar Complaint Count (C >= 1)
    safe_count = max(1, count)
    norm_count = min(safe_count / c_max, 1.0) * 100.0
    norm_count = max(0.0, min(100.0, norm_count))

    # 2. Normalize Severity (S between 1 and 5)
    safe_severity = max(1, min(5, severity))
    norm_severity = (safe_severity / 5.0) * 100.0
    norm_severity = max(0.0, min(100.0, norm_severity))

    # 3. Normalize Affected Users (U >= 1)
    safe_affected = max(1, affected)
    norm_affected = min(safe_affected / u_max, 1.0) * 100.0
    norm_affected = max(0.0, min(100.0, norm_affected))

    # 4. Normalize Recency (based on elapsed hours from created_at to current_time)
    elapsed_seconds = (current_time - created_at).total_seconds()
    elapsed_hours = max(0.0, elapsed_seconds / 3600.0)
    norm_recency = max(0.0, 100.0 - (elapsed_hours * decay_rate))
    norm_recency = max(0.0, min(100.0, norm_recency))

    # Weighted Score Summation
    raw_score = (
        (weights['count'] * norm_count) +
        (weights['severity'] * norm_severity) +
        (weights['affected'] * norm_affected) +
        (weights['recency'] * norm_recency)
    )

    final_score = round(max(0.0, min(100.0, raw_score)), 2)

    # Classification Mapping
    if final_score < 40.00:
        level = 'Low'
    elif final_score < 70.00:
        level = 'Medium'
    elif final_score < 85.00:
        level = 'High'
    else:
        level = 'Critical'

    return {
        'priority_score': final_score,
        'priority_level': level,
        'normalized_factors': {
            'count': round(norm_count, 2),
            'severity': round(norm_severity, 2),
            'affected': round(norm_affected, 2),
            'recency': round(norm_recency, 2)
        }
    }


def process_complaint_pipeline(complaint_id: int) -> bool:
    """
    TEMPORARY MOCK PIPELINE FOR UI DEVELOPMENT
    Allows Member 1 to verify status transitions, priority badges, and
    tracking views without blocking on Member 2's algorithms.

    To be replaced by Member 2 with true TF-IDF & Cosine Similarity calls.
    """
    from app.models import db, Complaint, IssueGroup, SimilarityRecord, ComplaintHistory

    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return False

    try:
        # Mark queue status as Processing
        old_queue = complaint.queue_status
        complaint.queue_status = 'Processing'

        # TEMPORARY MOCK SIMILARITY RESULT
        # For demonstration, assign to a default group or create one
        existing_group = IssueGroup.query.filter_by(category_id=complaint.category_id).first()
        if existing_group:
            existing_group.complaint_count += 1
            group_id = existing_group.group_id
            group_count = existing_group.complaint_count
            sim_score = 0.7500
            decision = 'Merged'
        else:
            new_group = IssueGroup(
                category_id=complaint.category_id,
                group_title=complaint.title,
                complaint_count=1
            )
            db.session.add(new_group)
            db.session.flush()
            group_id = new_group.group_id
            group_count = 1
            sim_score = 0.0000
            decision = 'New Group'

        # REAL PRIORITY CALCULATION
        prio_result = calculate_priority_score(
            count=group_count,
            severity=complaint.severity,
            affected=complaint.affected_users,
            created_at=complaint.created_at
        )

        # Update complaint record
        complaint.group_id = group_id
        complaint.similarity_score = sim_score
        complaint.priority_score = prio_result['priority_score']
        complaint.priority_level = prio_result['priority_level']
        complaint.queue_status = 'Processed'
        complaint.resolution_status = 'Open'

        # Record similarity log
        sim_log = SimilarityRecord(
            complaint_id=complaint.complaint_id,
            compared_complaint_id=None,
            group_id=group_id,
            similarity_score=sim_score,
            threshold_used=Config.SIMILARITY_THRESHOLD,
            decision=decision
        )
        db.session.add(sim_log)

        # Record audit history for queue status change
        hist = ComplaintHistory(
            complaint_id=complaint.complaint_id,
            actor_id=None,  # System automated action
            status_type='queue_status',
            old_value=old_queue,
            new_value='Processed',
            remarks='Automated pipeline intake and priority evaluation completed.'
        )
        db.session.add(hist)

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        complaint.queue_status = 'Failed'
        db.session.commit()
        raise e
