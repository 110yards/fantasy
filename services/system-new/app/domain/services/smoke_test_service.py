from typing import Callable, List, Tuple

from fastapi import Depends

from app.yards_py.domain.repositories.state_repository import StateRepository, create_state_repository


def run_check(name: str, target: Callable):
    try:
        StriveLogger.info(f"Starting test '{name}'")
        target()
        StriveLogger.info(f"Test '{name}' completed successfully")
        return True
    except BaseException as ex:
        StriveLogger.error(f"Test '{name}' failed", exc_info=ex)
        return False


def smoke_test(
    state_repo: StateRepository = Depends(create_state_repository),
) -> Tuple[List[str], List[str]]:
    checks = {
        "firebase:state": state_repo.get,
    }

    StriveLogger.info("Smoke test started")
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
        StriveLogger.error("Smoke test completed with errors")
    else:
        StriveLogger.info("Smoke test completed successfully")
    return passes, failures
