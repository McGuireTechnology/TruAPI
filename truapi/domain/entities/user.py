from dataclasses import dataclass, field

from truapi.domain.value_objects.id import ID


@dataclass
class User:
    id: ID = field(default_factory=ID.new)
    username: str = ""
    email: str = ""
    display_name: str = ""
