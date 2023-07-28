from app.core.publisher import VirtualPubSubPublisher
from app.domain.commands.user.update_profile import UpdateProfileCommand, UpdateProfileCommandExecutor
from app.domain.entities.user import User
from app.domain.enums.login_type import LoginType
from app.domain.repositories.user_repository import UserRepository
from tests.asserts import are_equal
from tests.mocks.mock_firestore_proxy import MockFirestoreProxy


def get_user_repo(user: User) -> UserRepository:
    users = [user]
    proxy = MockFirestoreProxy(users)
    return UserRepository(proxy)


def test_update_display_name():
    user = User(id="user1", display_name="Test Guy", email="test@guy.com", login_type=LoginType.EMAIL)

    user_repo = get_user_repo(user)
    publisher = VirtualPubSubPublisher("test_project")
    command_executor = UpdateProfileCommandExecutor(user_repo, publisher)

    command = UpdateProfileCommand(uid=user.id, display_name="Test Guy Updated", current_user_id=user.id)

    result = command_executor.execute(command)

    assert result.success

    expected = command.display_name
    actual = user_repo.get(user.id).display_name

    are_equal(expected, actual)


def test_update_another_user_should_fail():
    user = User(id="user1", display_name="Test Guy", email="test@guy.com", login_type=LoginType.EMAIL)

    user_repo = get_user_repo(user)
    publisher = VirtualPubSubPublisher("test_project")
    command_executor = UpdateProfileCommandExecutor(user_repo, publisher)

    command = UpdateProfileCommand(uid=user.id, display_name="Test Guy Updated", current_user_id="user2")

    result = command_executor.execute(command)

    assert not result.success
