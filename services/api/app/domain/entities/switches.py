from app.core.annotate_args import annotate_args
from app.core.base_entity import BaseEntity

# this class does not need all switches, only the ones the API cares about
# a set (replace doc) should never be done from the API, or it will override UI switches


@annotate_args
class Switches(BaseEntity):
    id = "switches"
    enable_relaxed_ir = True
    enable_game_roster_status = False
    donate_message = "Like the site?  Click here to donate and help pay the bill :)"
    enable_admin_switch_override = False
    enable_client_scoring = True
    enable_draft = True
    enable_facebook_login = False
    enable_game_roster_status = True
    enable_invite_by_email = False
    enable_login = True
    enable_matchup_progress = True
    enable_player_links = True
    enable_projections = True
    enable_public_leagues = False
    enable_relaxed_ir = True
    enable_score_testing = False
    enable_twitter_login = False
    show_donation_link = True
    show_new_roster_ui_tip = False
    enable_discord_integration = True
