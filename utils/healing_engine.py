import json
import os
import re

from selenium.webdriver.common.by import By

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException
)

from llm.llm_client import (
    LLMClient
)

from llm.prompts import (
    SELF_HEAL_PROMPT
)


class HealingEngine:

    def __init__(self):

        self.llm = (
            LLMClient()
        )

        self.fallback_path = (
            "healing/"
            "locator_fallbacks.json"
        )

        self.healed_path = (
            "healing/"
            "healed_locators.json"
        )

        self.by_mapping = {

            "id": By.ID,

            "name": By.NAME,

            "xpath": By.XPATH,

            "css": By.CSS_SELECTOR,

            "class": By.CLASS_NAME
        }

    # -----------------------------
    # Load fallback locators
    # -----------------------------
    def load_fallbacks(
        self
    ):

        if not os.path.exists(
            self.fallback_path
        ):
            return {}

        with open(
            self.fallback_path,
            "r"
        ) as file:

            return json.load(
                file
            )

    # -----------------------------
    # Load healed locators
    # -----------------------------
    def load_healed_locators(
        self
    ):

        if not os.path.exists(
            self.healed_path
        ):
            return {}

        with open(
            self.healed_path,
            "r"
        ) as file:

            return json.load(
                file
            )

    # -----------------------------
    # Save healed locator
    # -----------------------------
    def save_healed_locator(
        self,
        element_name,
        locator_type,
        locator_value
    ):

        healed = (
            self.load_healed_locators()
        )

        healed[element_name] = {

            "type":
            locator_type,

            "value":
            locator_value
        }

        with open(
            self.healed_path,
            "w"
        ) as file:

            json.dump(

                healed,

                file,

                indent=4
            )

    # -----------------------------
    # Ask LLM to heal locator
    # -----------------------------
    def ask_llm_to_heal(
        self,
        driver,
        element_name
    ):

        try:

            dom = (
                driver.page_source
            )[:5000]

            prompt = (
                SELF_HEAL_PROMPT
                .format(

                    locator_name=
                    element_name,

                    broken_locator=
                    element_name,

                    dom=
                    dom
                )
            )

            response = (
                self.llm.ask(
                    prompt
                )
            )

            print(
                "\n[LLM HEAL RESPONSE]"
            )

            print(
                response
            )

            locator_type = None
            locator_value = None

            type_match = re.search(
                r"Type:\s*(.*)",
                response
            )

            value_match = re.search(
                r"Value:\s*(.*)",
                response
            )

            if type_match:

                locator_type = (
                    type_match
                    .group(1)
                    .strip()
                    .lower()
                )

            if value_match:

                locator_value = (
                    value_match
                    .group(1)
                    .strip()
                )

            if (

                locator_type
                and
                locator_value
            ):

                by_type = (
                    self.by_mapping.get(
                        locator_type
                    )
                )

                if by_type:

                    element = (
                        driver.find_element(

                            by_type,

                            locator_value
                        )
                    )

                    self.save_healed_locator(

                        element_name,

                        locator_type,

                        locator_value
                    )

                    print(

                        f"[LLM HEALED] "
                        f"{element_name}"
                    )

                    return element

        except Exception as e:

            print(
                "[LLM HEAL FAILED]",
                str(e)
            )

        return None

    # -----------------------------
    # Try healing locator
    # -----------------------------
    def heal_locator(
        self,
        driver,
        element_name
    ):

        fallbacks = (
            self.load_fallbacks()
        )

        locator_list = (
            fallbacks.get(
                element_name,
                []
            )
        )

        for locator in locator_list:

            try:

                locator_type = (
                    locator["type"]
                )

                locator_value = (
                    locator["value"]
                )

                by_type = (
                    self.by_mapping[
                        locator_type
                    ]
                )

                element = (
                    driver.find_element(

                        by_type,

                        locator_value
                    )
                )

                self.save_healed_locator(

                    element_name,

                    locator_type,

                    locator_value
                )

                print(

                    f"[HEALED] "
                    f"{element_name}"
                )

                return element

            except (

                NoSuchElementException,
                TimeoutException,
                StaleElementReferenceException
            ):

                continue

        # -------------------------
        # LLM Healing
        # -------------------------
        print(
            f"\n[LLM HEALING] "
            f"{element_name}"
        )

        return self.ask_llm_to_heal(

            driver,

            element_name
        )