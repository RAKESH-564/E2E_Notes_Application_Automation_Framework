TEST_GENERATION_PROMPT = """
You are an expert QA Automation Engineer.

Generate EXECUTABLE tests for an existing
Pytest + Selenium Page Object Model framework.

VERY IMPORTANT RULES:

1. Generate ONLY runnable tests.

2. Use ONLY methods listed below.

3. NEVER hallucinate methods.

4. Do NOT invent fixtures.

5. Use existing framework style.

6. Use:
logged_in_driver

for authenticated pages.

7. Create page object like:

page = ProductPage(
    logged_in_driver
)

8. Add meaningful assertions.

9. Ignore helper/framework methods:
safe_click
retry_click
js_click
wait_for_clickable
wait_for_element
wait_for_visible
wait_for_dom_ready
scroll
take_screenshot
get_elements

10. Only generate business scenarios.

11. Use realistic values.

12. Return ONLY Python code.

PAGE CLASS:
{class_name}

AVAILABLE METHODS:
{methods}

FRAMEWORK CONTEXT:
{context}
"""


FLAKY_ANALYSIS_PROMPT = """
You are an expert QA Automation Engineer.

Analyze this failed automation test.

Your job:

1. Identify root cause.
2. Decide if flaky or defect.
3. Suggest fix.
4. Give confidence score.

Test Name:
{test_name}

Error:
{error}

Return response STRICTLY in format:

Type:
Cause:
Suggested Fix:
Confidence:
"""


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