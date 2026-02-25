"""Integration tests for tars/ai/chat.py — mocked OpenAI and local LLM."""

from unittest.mock import MagicMock, patch


@patch("tars.ai.chat.local_llm")
@patch("tars.ai.chat._client")
@patch("tars.ai.chat._openai_available", True)
def test_get_response_openai_success(mock_client, mock_local):
    """Returns OpenAI response when available."""
    from tars.ai.chat import get_response

    mock_choice = MagicMock()
    mock_choice.message.content = "I'm TARS. I have a humor setting."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    result = get_response("Hello")
    assert result == "I'm TARS. I have a humor setting."


@patch("tars.ai.chat.local_llm")
@patch("tars.ai.chat._client")
@patch("tars.ai.chat._openai_available", True)
def test_get_response_falls_back_to_local(mock_client, mock_local):
    """Falls back to local LLM when OpenAI fails."""
    from tars.ai.chat import get_response

    mock_client.chat.completions.create.side_effect = Exception("API error")
    mock_local.is_available.return_value = True
    mock_local.get_response.return_value = "Local response here."

    result = get_response("Hello")
    assert result == "Local response here."


@patch("tars.ai.chat.local_llm")
@patch("tars.ai.chat._openai_available", False)
def test_get_response_no_backends(mock_local):
    """Returns offline message when no backends available."""
    from tars.ai.chat import get_response

    mock_local.is_available.return_value = False

    result = get_response("Hello")
    assert "offline" in result.lower() or "API key" in result.lower()


@patch("tars.ai.chat.local_llm")
@patch("tars.ai.chat._client")
@patch("tars.ai.chat._openai_available", True)
def test_get_response_passes_personality(mock_client, mock_local):
    """Personality settings are passed to the system prompt."""
    from tars.ai.chat import get_response

    mock_choice = MagicMock()
    mock_choice.message.content = "Response"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    get_response("Hello", honesty=0.9, humor=0.8, target_language="spanish")

    call_args = mock_client.chat.completions.create.call_args
    messages = call_args.kwargs.get("messages") or call_args[1].get("messages")
    system_msg = messages[0]["content"]
    assert "90.0%" in system_msg  # honesty
    assert "80.0%" in system_msg  # humor
    assert "spanish" in system_msg
