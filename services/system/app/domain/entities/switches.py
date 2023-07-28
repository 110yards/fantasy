from app.core.base_entity import BaseEntity

# this class does not need all switches, only the ones the API cares about
# a set (replace doc) should never be done from the API, or it will override UI switches


class Switches(BaseEntity):
    id: str = "switches"
    enable_discord_integration: bool = False
