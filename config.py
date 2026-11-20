import os

# Gracefully load .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass



class Config:
    """Base application configuration loaded from environment variables."""

    # Flask Core
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-secret-key')

    # MySQL Database Connection
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'complaint_db')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Algorithmic Parameters (Configurable)
    SIMILARITY_THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD', 0.50))

    # Priority Engine Weights (Default: 35%, 25%, 25%, 15% -> Sum = 1.0)
    PRIORITY_WEIGHTS = {
        'count': float(os.environ.get('PRIORITY_WEIGHT_COUNT', 0.35)),
        'severity': float(os.environ.get('PRIORITY_WEIGHT_SEVERITY', 0.25)),
        'affected': float(os.environ.get('PRIORITY_WEIGHT_AFFECTED', 0.25)),
        'recency': float(os.environ.get('PRIORITY_WEIGHT_RECENCY', 0.15)),
    }

    # Priority Normalization Caps
    PRIORITY_C_MAX = int(os.environ.get('PRIORITY_C_MAX', 10))
    PRIORITY_U_MAX = int(os.environ.get('PRIORITY_U_MAX', 50))
    PRIORITY_RECENCY_DECAY = float(os.environ.get('PRIORITY_RECENCY_DECAY', 2.0))

    # Priority Classification Cutoffs
    PRIORITY_LEVELS = {
        'Low': (0.00, 40.00),
        'Medium': (40.00, 70.00),
        'High': (70.00, 85.00),
        'Critical': (85.00, 100.00),
    }

    @classmethod
    def validate_weights(cls):
        """Validates that all priority weights sum to exactly 1.0."""
        total = sum(cls.PRIORITY_WEIGHTS.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"Priority weights must sum to exactly 1.0, but got {total:.4f}"
            )
        return True
