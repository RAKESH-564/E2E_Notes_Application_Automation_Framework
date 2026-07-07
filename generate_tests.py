from agents.test_generation_agent import (
    TestGenerationAgent
)

from pages.product_page import (
    ProductPage
)

from pages.login_page import (
    LoginPage
)


agent = (
    TestGenerationAgent()
)

print(
    "\nGenerating LoginPage tests..."
)

agent.generate_ui_tests(
    LoginPage
)

print(
    "\nGenerating ProductPage tests..."
)

agent.generate_ui_tests(
    ProductPage
)

print(
    "\nAI test generation complete."
)