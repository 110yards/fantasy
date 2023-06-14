

from datetime import datetime
from services.system.app.domain.commands.league.create_league_subscriptions import (
    CreateLeagueSubscriptionsCommand, CreateLeagueSubscriptionsCommandExecutor,
    create_league_subscriptions_command_executor)
from yards_py.core.logging import Logger
from yards_py.domain.entities.owned_player import OwnedPlayer
from yards_py.domain.entities.player import Player
from yards_py.domain.entities.team import Team
from yards_py.domain.repositories.league_owned_player_repository import LeagueOwnedPlayerRepository, create_league_owned_player_repository
from yards_py.domain.repositories.league_repository import (
    LeagueRepository, create_league_repository)
from fastapi.param_functions import Depends
from firebase_admin.firestore import firestore
from yards_py.domain.repositories.league_roster_repository import LeagueRosterRepository, create_league_roster_repository
from yards_py.domain.repositories.player_repository import PlayerRepository, create_player_repository


def create_map_new_players_migration(
    player_repo: PlayerRepository = Depends(create_player_repository),
    league_repo: LeagueRepository = Depends(create_league_repository),
    league_roster_repo: LeagueRosterRepository = Depends(create_league_roster_repository),
    league_owned_player_repo: LeagueOwnedPlayerRepository = Depends(create_league_owned_player_repository),
):
    return MapNewPlayerSourceMigration(
        league_repo=league_repo,
        league_roster_repo=league_roster_repo,
        player_repo=player_repo,
        league_owned_players_repo=league_owned_player_repo,
    )


class MapNewPlayerSourceMigration:
    '''
    Create a "slug" for each player, which is a hash of their name and team.
    Create a player dict by slug
    Create a player dict by cfl id
    For each rostered player, check by cfl id, if not match then check by slug.
        If no match, set as free agent.
        If match by id, update id.
        If match by slug, update id and set cfl id for future matching
    '''

    def __init__(
            self,
            league_repo: LeagueRepository,
            league_roster_repo: LeagueRosterRepository,
            player_repo: PlayerRepository,
            league_owned_players_repo: LeagueOwnedPlayerRepository,
    ):
        self.league_repo = league_repo
        self.league_roster_repo = league_roster_repo
        self.player_repo = player_repo
        self.league_owned_players_repo = league_owned_players_repo

    def run(self, commit=False, league_id: str = None) -> dict:
        Logger.info(f"Running map new player source migration {'(dry run)' if commit else ''}")

        if datetime.now().year != 2023:
            return "Migration only valid for 2023"
        
        if league_id:
            leagues = [self.league_repo.get(league_id)]
        else:
            leagues = self.league_repo.get_all()

        players = self.player_repo.get_all(2023)
        players_by_cfl_id = {p.cfl_central_id: p for p in players if p.cfl_central_id is not None}
        players_by_slug = {slug(p): p for p in players}

        roster_players_fixed = 0
        roster_players_failed = 0
        owned_players_fixed = 0
        failed_players = {}

        for league in leagues:
            if not league.is_active_for_season(2023):
                Logger.info(f"Skipping league {league.id} because it is not active for 2023")
                continue # nothing to do

            if commit:
                Logger.info(f"Removing owned players for league {league.id}")            
                owned_players = self.league_owned_players_repo.get_all(league.id)

                for owned_player in owned_players:                    
                    self.league_owned_players_repo.delete(league.id, owned_player.id)

            for roster in self.league_roster_repo.get_all(league.id):
                roster_owned_players = []
                for key, position in roster.positions.items():
                    if not position.player:
                        continue # no player to fix

                    if position.player.player_id is None:
                        # don't do this again if already fixed, but don't continue because the owned player list is very important
                        if position.player.cfl_central_id in players_by_cfl_id:
                            matched = players_by_cfl_id[position.player.cfl_central_id]
                            Logger.info(f"Matched player {position.player.display_name} to {matched.display_name} by cfl id")
                            position.player = matched
                            roster_players_fixed += 1
                        elif slug(position.player) in players_by_slug:
                            matched = players_by_slug[slug(position.player)]
                            matched.cfl_central_id = position.player.cfl_central_id
                            Logger.info(f"Matched player {position.player.display_name} to {matched.display_name} by slug")
                            players_by_cfl_id[matched.cfl_central_id] = matched
                            position.player = matched
                            roster_players_fixed += 1
                        else:
                            Logger.info(f"Could not match player {position.player.display_name} in league {league.id}")
                            failed_players[position.player.cfl_central_id] = f"{position.player.team.abbreviation} - {position.player.display_name} - {position.player.cfl_central_id}"
                            position.player.team = Team.free_agent()
                            roster_players_failed += 1
                        
                    roster_owned_players.append(OwnedPlayer.create(owner_id=roster.id, player=position.player))
                
                if commit:
                    self.league_roster_repo.update(league.id, roster)
                    for owned_player in roster_owned_players:
                        self.league_owned_players_repo.set(league.id, owned_player)         
                        owned_players_fixed += 1

        return {
            "roster_players_fixed": roster_players_fixed,
            "roster_players_failed": roster_players_failed,
            "owned_players_fixed": owned_players_fixed,
            "failed_players": [failed_players.values()],
        }

def slug(p: Player) -> str:
    first_name = p.first_name.lower().replace(" ", "-")
    last_name = p.last_name.lower().replace(" ", "-")
    slug = f"{p.team.abbreviation}-{first_name}-{last_name}"

    slug = slug.lower()
    slug = slug.replace("jr.", "")
    slug = slug.replace("iii", "")
    slug = slug.replace("ii", "")
    
    return slug
