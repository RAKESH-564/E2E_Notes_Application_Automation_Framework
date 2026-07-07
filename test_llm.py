from llm.llm_client import (
    LLMClient
)

client = (
    LLMClient()
)

response = client.ask(

    "Explain flaky tests "
    "in Selenium."
)

print(response)