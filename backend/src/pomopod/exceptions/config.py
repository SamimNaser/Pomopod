class SpaceAlreadyExists(Exception):
  """Exception raised when a space with the same name already exists."""


class SpaceDoesNotExist(Exception):
  """Exception raised when a space with the given name does not exists."""
