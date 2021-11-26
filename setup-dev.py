
import os

import firebase_admin

from api.app.core.publisher import VirtualPubSubPublisher
from api.app.domain.commands.user.register_email import RegisterCommandExecutor, RegisterEmailCommand
from api.app.domain.entities.opponents import Opponents
from api.app.domain.entities.state import State
from api.app.domain.entities.switches import Switches
from api.app.domain.repositories.public_repository import create_public_repository
from api.app.domain.repositories.user_repository import create_user_repository

DEV_PROJECT_ID = "yards-dev"


# ensure we are set up to use the emulator

os.environ["GCLOUD_PROJECT"] = DEV_PROJECT_ID
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:9000"
os.environ["FIREBASE_AUTH_EMULATOR_HOST"] = "localhost:9099"

firebase_admin.initialize_app(options={"projectId": DEV_PROJECT_ID})

publisher = VirtualPubSubPublisher(DEV_PROJECT_ID)

public_repo = create_public_repository()
user_repo = create_user_repository()

default_switches = Switches()

print("If this script takes more than a few seconds, the emulator may not be running (or is not running on port 9000)")
print("In this case, press CTRL+C to stop, then run 'npm run start:emulators' in a different terminal and try again.")
print()
print("Configuring default switches...")
public_repo.set_switches(default_switches)
print("Done")

print("Configuring default state")
state = State(current_week=1, current_season=2021, season_weeks=16)
public_repo.set_state(state)

opponents = Opponents.create({})
public_repo.set_opponents(opponents)
print("Done")

print("Creating default admin account...")
command = RegisterEmailCommand(display_name="Admin", email="admin@110yards.dev")
command_executor = RegisterCommandExecutor(user_repo, publisher, is_dev=True)
command_executor.execute(command)
print("Done")

print("Setup script complete")
