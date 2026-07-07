import json
import os

from datetime import (
    datetime
)

from llm.llm_client import (
    LLMClient
)

from llm.prompts import (
    FLAKY_ANALYSIS_PROMPT
)


class FlakyTestAgent:

    def __init__(self):

        self.llm = (
            LLMClient()
        )

        self.history_path = (

            "flaky_analysis/"
            "flaky_history.json"
        )

    # -------------------------
    # Analyze Failure
    # -------------------------
    def analyze_failure(
        self,
        test_name,
        error_message
    ):

        prompt = (
            FLAKY_ANALYSIS_PROMPT
            .format(

                test_name=
                test_name,

                error=
                str(
                    error_message
                )
            )
        )

        response = (
            self.llm.ask(
                prompt
            )
        )

        return response

    # -------------------------
    # Save Failure
    # -------------------------
    def save_failure(
        self,
        test_name,
        error_message
    ):

        analysis = (
            self.analyze_failure(

                test_name=
                test_name,

                error_message=
                error_message
            )
        )

        entry = {

            "timestamp":
            str(
                datetime.now()
            ),

            "test_name":
            test_name,

            "error":
            str(
                error_message
            ),

            "analysis":
            analysis
        }

        history = []

        if os.path.exists(
            self.history_path
        ):

            with open(
                self.history_path,
                "r"
            ) as file:

                try:

                    history = (
                        json.load(
                            file
                        )
                    )

                except Exception:

                    history = []

        history.append(
            entry
        )

        with open(
            self.history_path,
            "w"
        ) as file:

            json.dump(

                history,

                file,

                indent=4
            )

        print(
            "\n[AI FLAKY ANALYSIS]"
        )

        print(
            analysis
        )