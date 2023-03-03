# This example requires the 'message_content' privileged intent to function.

import asyncio
import logging
import os

import discord
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport

ADMIN_SECRET = os.environ["ADMIN_SECRET"]
HGE_ENDPOINT = os.environ["HGE_ENDPOINT"]
HGE_ENDPOINT_WSS = os.environ["HGE_ENDPOINT_WSS"]
HGE_URL = HGE_ENDPOINT + "/v1/graphql"
HGE_WSS_URL = HGE_ENDPOINT_WSS + "/v1/graphql"

HEADERS = {"X-Hasura-Admin-Secret": ADMIN_SECRET}

wtransport = WebsocketsTransport(
    url=HGE_WSS_URL, headers=HEADERS, connect_args={"ping_interval": None}
)
gql_client = Client(
    transport=wtransport,
    fetch_schema_from_transport=True,
    execute_timeout=1000
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Pod42")

insertQuestion = gql(
    """
mutation InsertQuestionInSlackTable(
  $question:String!,
  $asked_by:String!
) {
  insert_questions_slack_one(
    object: {
      asked_by: $asked_by,
      question: $question
    }) {
    question
    asked_by
    id
  }
}
"""
)

subscriptionForQuestionAndAnswer = gql(
    """
subscription MySubscription {
  questions_with_answers_stream(batch_size: 100, cursor: {initial_value: {answer_id: "1"}}) {
    answer
    asked_by
    question
    sources
    answer_id
    question_id
  }
}

"""
)


questionIdToSay = {}
HASURA_BLOG = "https://hasura.io/blog/"


def clean_content(content):
    return content.strip().replace(".mdx", "").replace("GHOST_URL/", HASURA_BLOG)


async def process_msg(msg):
    for m in msg["questions_with_answers_stream"]:
        logger.info(m)
        if m["question_id"] in questionIdToSay:
            answer = clean_content(m["answer"])
            answerWithSources = f"{answer}"
            if m["sources"]:
                sources = clean_content(m["sources"])
                answerWithSources += f"\n\n*Sources:*\n{sources}"
            answerWithSources += "\n\nWas the answer helpful?"
            await questionIdToSay[m["question_id"]].reply(
                answerWithSources, mention_author=True
            )
            del questionIdToSay[m["question_id"]]


async def execute_subscription(session):
    async for msg in session.subscribe(subscriptionForQuestionAndAnswer):
        asyncio.create_task(process_msg(msg))


async def start_async() -> None:
    while True:
        try:
            session = await gql_client.connect_async(reconnecting=True)
            await execute_subscription(session)
        except:
            logger.error("Error while processing subscription")
            asyncio.sleep(1)
            continue


class Pod42Client(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def openai_timeout(self, message, question_id):
        await asyncio.sleep(150)
        if question_id in questionIdToSay:
            await message.reply(
                "Sorry! We have encountered an error with OpenAI. Please try after sometime.\n You can check http://status.openai.com for more info",
                mention_author=True,
            )
            del questionIdToSay[question_id]

    async def setup_hook(self) -> None:
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(start_async())

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info("------")

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if self.user.mention in message.content:
            await message.reply("On it", mention_author=True)
            response = await gql_client.session.execute(
                insertQuestion,
                variable_values={
                    "question": message.content.replace(
                        "<@1066988115518046258>", ""
                    ).strip(),
                    "asked_by": message.author.name,
                },
            )
            logger.info(response)
            questionIdToSay[response["insert_questions_slack_one"]["id"]] = message
            self.loop.create_task(
                self.openai_timeout(
                    message, response["insert_questions_slack_one"]["id"]
                )
            )


intents = discord.Intents.default()
intents.message_content = True

client = Pod42Client(intents=intents)
client.run(os.environ["DISCORD_TOKEN"])
