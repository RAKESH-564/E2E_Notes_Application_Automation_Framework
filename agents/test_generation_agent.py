import inspect
import os

from llm.llm_client import (
    LLMClient
)

from llm.prompts import (
    TEST_GENERATION_PROMPT
)


class TestGenerationAgent:

    def __init__(self):

        self.llm = (
            LLMClient()
        )

        self.output_folder = (
            "test_generation/"
            "generated_tests"
        )

        os.makedirs(
            self.output_folder,
            exist_ok=True
        )

        self.ignore_methods = {

            "click",
            "safe_click",
            "retry_click",
            "js_click",
            "wait_for_clickable",
            "wait_for_element",
            "wait_for_visible",
            "wait_for_dom_ready",
            "scroll",
            "take_screenshot",
            "get_elements",
            "__init__"
        }

    def generate_ui_tests(
        self,
        page_class
    ):

        class_name = (
            page_class.__name__
        )

        methods = [

            name

            for name, func
            in inspect.getmembers(
                page_class,
                inspect.isfunction
            )

            if (

                not name.startswith(
                    "_"
                )

                and

                name not in
                self.ignore_methods
            )
        ]

        framework_context = """

Framework uses:

Fixtures:
- driver
- logged_in_driver

Login:
LoginPage(driver)
.login(UserEmail,
UserPassword)

Authenticated page:
ProductPage(
logged_in_driver
)

Config:
UserEmail
UserPassword

Existing test style:
pytest + allure

Use only provided methods.
Never invent methods.
"""

        prompt = (
            TEST_GENERATION_PROMPT
            .format(

                class_name=
                class_name,

                methods=
                methods,

                context=
                framework_context
            )
        )

        generated_code = (
            self.llm.ask(
                prompt
            )
        )

        module_name = (
            class_name
            .replace(
                "Page",
                "_page"
            )
            .lower()
        )

        required_imports = f"""
        import pytest
        import allure

        from pages.{module_name} import (
            {class_name}
        )

        """

        if (
            f"from pages."
            not in generated_code
        ):

            generated_code = (
                required_imports
                + generated_code
            )

        file_path = (

            f"{self.output_folder}/"
            f"test_generated_"
            f"{class_name.lower()}.py"
        )

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                generated_code
            )

        print(
            f"[AI TEST GENERATED] "
            f"{file_path}"
        )