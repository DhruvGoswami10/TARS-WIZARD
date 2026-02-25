"""Shared pytest fixtures for TARS tests."""

import pytest

from tars.commands.language import LanguageState
from tars.utils.threading import SharedState


@pytest.fixture
def language_state():
    """Create a fresh LanguageState."""
    return LanguageState()


@pytest.fixture
def shared_state(language_state):
    """Create a fresh SharedState wrapping LanguageState."""
    return SharedState(language_state)
