from app.core.annotate_args import annotate_args
from app.core.base_entity import BaseEntity

# this class does not need all switches, only the ones the API cares about
# a set (replace doc) should never be done from the API, or it will override UI switches


@annotate_args
class Switches(BaseEntity):
    id: str = "switches"
    enable_relaxed_ir: bool = True
    enable_game_roster_status: bool = False
    donate_message: str = "Like the site?  Click here to donate and help pay the bill :)"
    enable_admin_switch_override: bool = False
    enable_client_scoring: bool = True
    enable_draft: bool = True
    enable_facebook_login: bool = False
    enable_game_roster_status: bool = True
    enable_invite_by_email: bool = False
    enable_login: bool = True
    enable_matchup_progress: bool = True
    enable_player_links: bool = True
    enable_projections: bool = True
    enable_public_leagues: bool = False
    enable_relaxed_ir: bool = True
    enable_score_testing: bool = False
    enable_twitter_login: bool = False
    show_donation_link: bool = True
    show_new_roster_ui_tip: bool = False
    enable_discord_integration: bool = True
