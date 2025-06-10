class AlitaError(Exception):
    """Base exception for all errors raised by the Alita framework."""
    pass

class ToolCreationError(AlitaError):
    """Raised when a tool cannot be created."""
    pass

class ToolExecutionError(AlitaError):
    """Raised when a tool fails to execute."""
    pass

class PlanningError(AlitaError):
    """Raised during a planning failure."""
    pass
