from agents.flaky_test_agent import (
    FlakyTestAgent
)

agent = (
    FlakyTestAgent()
)

agent.save_failure(

    test_name=
    "test_delete_note",

    error_message=
    """
    selenium.common.exceptions.
    TimeoutException:
    Message:
    timeout receiving
    renderer message
    """
)


SELF_HEAL_PROMPT = """
You are an expert Selenium locator healing system.

A locator failed.

Your task:

1. Analyze failed locator.
2. Analyze DOM snippet.
3. Suggest BEST replacement locator.
4. Prefer CSS selectors.
5. Use data-testid if available.
6. Avoid brittle XPath.

Locator Name:
{locator_name}

Broken Locator:
{broken_locator}

DOM:
{dom}

Return STRICTLY:

Type:
Value:
Confidence:
"""