import pytest
from unittest.mock import Mock, patch
from libs.openai_sdk import OpenaiSdk

@pytest.fixture
def openai_sdk():
    return OpenaiSdk(api_key="YOUR_API_KEY", model_name="YOUR_MODEL_NAME")

@pytest.mark.asyncio
async def test_generate_completion(openai_sdk):
    prompt = "Test prompt."
    response = {"choices": [{"text": "Generated text."}]}
    with patch("openai.Completion.create", new=Mock(return_value=response)):
        result = await openai_sdk.generate_completion(prompt)
        assert result == "Generated text."

@pytest.mark.asyncio
async def test_generate_completions(openai_sdk):
    prompts = ["Test prompt 1.", "Test prompt 2.", "Test prompt 3."]
    responses = [{"choices": [{"text": "Generated text 1."}]},
                 {"choices": [{"text": "Generated text 2."}]},
                 {"choices": [{"text": "Generated text 3."}]}]
    with patch("openai.Completion.create", side_effect=responses):
        results = await openai_sdk.generate_completions(prompts)
        assert results == ["Generated text 1.", "Generated text 2.", "Generated text 3."]

@pytest.mark.asyncio
async def test_run(openai_sdk):
    prompts = ["Test prompt 1.", "Test prompt 2.", "Test prompt 3."]
    responses = [{"choices": [{"text": "Generated text 1."}]},
                 {"choices": [{"text": "Generated text 2."}]},
                 {"choices": [{"text": "Generated text 3."}]}]
    with patch("openai.Completion.create", side_effect=responses):
        results = openai_sdk.run(prompts)
        assert results == ["Generated text 1.", "Generated text 2.", "Generated text 3."]
