"""
Unit Tests for Priority Engine Rules and Validation
Verifies:
1. All four weights sum to exactly 1.0.
2. Every normalized factor remains between 0.0 and 100.0.
3. The final priority score remains strictly between 0.00 and 100.00.
4. Priority classifications follow approved boundaries (Low, Medium, High, Critical).
5. Recency evaluates elapsed hours from creation time to current time.
6. Boundary cases and extreme values are handled without errors.
"""
import unittest
from datetime import datetime, timedelta, timezone
from config import Config
from app.services.pipeline import calculate_priority_score


def get_current_time():
    """Returns timezone-naive UTC datetime for consistent test comparison."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TestPriorityRules(unittest.TestCase):

    def test_weights_sum_to_one(self):
        """Verifies that all 4 priority weights sum to exactly 1.0."""
        total = sum(Config.PRIORITY_WEIGHTS.values())
        self.assertAlmostEqual(total, 1.0, places=5, msg="Priority weights must sum to 1.0")

    def test_factor_normalization_bounds(self):
        """Verifies that every normalized factor remains clamped in [0.0, 100.0]."""
        now = get_current_time()

        # Test extreme lower boundary
        res_low = calculate_priority_score(
            count=0,
            severity=1,
            affected=0,
            created_at=now - timedelta(days=30),  # very old
            current_time=now
        )
        for key, val in res_low['normalized_factors'].items():
            self.assertGreaterEqual(val, 0.0, f"Factor {key} dropped below 0")
            self.assertLessEqual(val, 100.0, f"Factor {key} exceeded 100")

        # Test extreme upper boundary
        res_high = calculate_priority_score(
            count=1000,
            severity=10,  # exceeds 5
            affected=5000,
            created_at=now,  # fresh
            current_time=now
        )
        for key, val in res_high['normalized_factors'].items():
            self.assertGreaterEqual(val, 0.0, f"Factor {key} dropped below 0")
            self.assertLessEqual(val, 100.0, f"Factor {key} exceeded 100")

    def test_final_score_bounds(self):
        """Verifies that the final score remains strictly in [0.00, 100.00]."""
        now = get_current_time()
        for count in [1, 5, 10, 50]:
            for sev in [1, 2, 3, 4, 5]:
                for aff in [1, 10, 50, 100]:
                    for hours in [0, 5, 24, 72]:
                        res = calculate_priority_score(
                            count=count,
                            severity=sev,
                            affected=aff,
                            created_at=now - timedelta(hours=hours),
                            current_time=now
                        )
                        score = res['priority_score']
                        self.assertGreaterEqual(score, 0.0, f"Score {score} is negative")
                        self.assertLessEqual(score, 100.0, f"Score {score} exceeded 100")

    def test_priority_classifications(self):
        """
        Verifies classification boundaries:
        Low:      [0.00, 40.00)
        Medium:   [40.00, 70.00)
        High:     [70.00, 85.00)
        Critical: [85.00, 100.00]
        """
        now = get_current_time()

        # 1. Low Priority Case: Count=1, Severity=1, Affected=1, Old (60h ago)
        low_res = calculate_priority_score(
            count=1, severity=1, affected=1,
            created_at=now - timedelta(hours=60), current_time=now
        )
        self.assertLess(low_res['priority_score'], 40.00)
        self.assertEqual(low_res['priority_level'], 'Low')

        # 2. Critical Priority Case: Count=15, Severity=5, Affected=60, Fresh (0h)
        crit_res = calculate_priority_score(
            count=15, severity=5, affected=60,
            created_at=now, current_time=now
        )
        self.assertGreaterEqual(crit_res['priority_score'], 85.00)
        self.assertEqual(crit_res['priority_level'], 'Critical')

    def test_recency_decay(self):
        """Verifies that fresh complaints score higher on recency than aging ones."""
        now = get_current_time()
        fresh = calculate_priority_score(count=2, severity=3, affected=5, created_at=now, current_time=now)
        aged = calculate_priority_score(count=2, severity=3, affected=5, created_at=now - timedelta(hours=24), current_time=now)

        self.assertGreater(
            fresh['normalized_factors']['recency'],
            aged['normalized_factors']['recency'],
            "Fresh complaints must have higher recency score than aged ones"
        )
        self.assertGreater(
            fresh['priority_score'],
            aged['priority_score'],
            "Fresh complaints must produce higher total score when all other factors match"
        )


if __name__ == '__main__':
    unittest.main()
