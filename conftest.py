"""
Root pytest configuration for the SevenUnique AI backend test suite.

pytest-asyncio 1.4.0 is configured to run all async tests and fixtures
in a single session-scoped event loop (asyncio_default_test_loop_scope=session
in pytest.ini).  This ensures the Motor AsyncIOMotorClient — which binds to
the event loop it is created on — is always used on the same loop as the
test functions and the module-scoped seed_and_cleanup fixture.
"""


def pytest_configure(config):
    """Register custom markers to suppress PytestUnknownMarkWarning."""
    config.addinivalue_line("markers", "asyncio: mark test as async")
