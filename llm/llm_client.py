import os

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


class LLMClient:

    def __init__(self):

        api_key = os.getenv(
            "LONGCAT_API_KEY"
        )

        self.client = OpenAI(

            api_key=api_key,

            base_url=
            "https://api.longcat.chat/openai"
        )

        self.model = (
            "LongCat-Flash-Chat"
        )

    def ask(
        self,
        prompt
    ):

        try:

            response = (
                self.client.chat.completions.create(

                    model=self.model,

                    messages=[

                        {

                            "role":
                            "system",

                            "content":
                            (
                                "You are an expert "
                                "QA automation engineer "
                                "specialized in Selenium, "
                                "Pytest, API testing, "
                                "and test automation."
                            )
                        },

                        {

                            "role":
                            "user",

                            "content":
                            prompt
                        }
                    ],

                    temperature=0.2
                )
            )

            return (

                response
                .choices[0]
                .message
                .content
            )

        except Exception as e:

            print(
                "[LLM ERROR]",
                str(e)
            )

            return None