"""Business-logic layer.

Services orchestrate repositories and hold ALL business decisions. Handlers
and routers call services; they never query the database directly.
"""

from shared.services.user import UserService

__all__ = ["UserService"]
