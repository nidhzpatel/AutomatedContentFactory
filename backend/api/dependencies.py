from backend.config import settings


def get_settings():
    """Dependency provider for application settings."""
    return settings
