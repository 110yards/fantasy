from typing import Callable, List, Tuple

from app.core.logging import Logger
from app.domain.repositories.state_repository import StateRepository, create_state_repository
from fastapi import Depends


def run_check(name: str, target: Callable):
    try:
        Logger.info(f"Starting test '{name}'")
        target()
        Logger.info(f"Test '{name}' completed successfully")
        return True
    except BaseException as ex:
        Logger.error(f"Test '{name}' failed", exc_info=ex)
        return False


def smoke_test(
    state_repo: StateRepository = Depends(create_state_repository),
) -> Tuple[List[str], List[str]]:
    checks = {
        "firebase:state": state_repo.get,
    }

    Logger.info("Smoke test started")
    passes: List[str] = []
    failures: List[str] = []

    for name in checks:
        check = checks[name]
        passed = run_check(name, check)
        if passed:
            passes.append(name)
        else:
            failures.append(name)

    if failures:
        Logger.error("Smoke test completed with errors")
    else:
        Logger.info("Smoke test completed successfully")
    return passes, failures
