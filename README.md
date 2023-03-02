# hasura-pod42

A Discord bot to to answer question based on docs using the latest ChatGPT API, built on [Hasura GraphQL
Engine](https://github.com/hasura/graphql-engine) and [LangChain](https://github.com/hwchase17/langchain).

You can try out the bot on our [Discord](https://discord.gg/hasura)

It features include:
- Asynchronous architecture based on the Hasura events system with rate limiting and retries.
- Performant Discord bot built on Hasura's streaming subscriptions.
- Ability to ingest your content to the bot.
- Prompt to make GPT-3 answer with sources while minimizing bogus answers.

Made with :heart: by <a href="https://hasura.io">Hasura</a>

----------------
![Pod42 Demo](assets/pod42-demo.png)
----------------

## Table of contents
- [Installation](#installation)
  * [Setup Hasura Pod42](#steps-to-setup-hasura-pod42)
- [Architecture](#architecture)
- [Comparison: text-davinci-003 vs gpt-3.5-turbo](#comparison-text-davinci-003-vs-gpt-35-turbo)

## Installation

### Steps to Setup Hasura Pod42

- Setup `src/pod42-server`
- Use the url to populate `EVENT_TRIGGER_WEBHOOK_URL` in `hasura-cloud-deploy-config.yaml`
- You can use the one-click to deploy on Hasura Cloud to get started quickly:
  
  [![Deploy to Hasura Cloud](https://hasura.io/deploy-button.svg)]( https://cloud.hasura.io/deploy?github_repo=https://github.com/hasura/pod42#comparison-text-davinci-003-vs-gpt-35-turbo&hasura_dir=hasura)


## Architecture
![Pod42 Arch](assets/hasura-arch-pod42.png)


## Comparison: text-davinci-003 vs gpt-3.5-turbo

For Hasura's use-case, we want to emphasis on correctness of the answers, it's better for us if Pod42 says "I Don't Know" instead of bluffing an answer.

### Example: When Answer exists in Docs
![Pod42 text-davinci-003](assets/hasura-pod42-davinci-answer-1.png)

![Pod42 gpt-3.5-turbo](assets/hasura-pod42-chatgpt-answer-1.png)

### Example: When Question is Misunderstood
![Pod42 text-davinci-003](assets/hasura-pod42-davinci-incorrect-answer-1.png)

The above answer is completely false, it misunderstood the question as Discord passed a user-id instead of the text "@Cache"

![Pod42 gpt-3.5-turbo](assets/hasura-pod42-chatgpt-answer-2.png)

This is a much better answer, it might prompt the user to ask the question better and which point you get the following outcome

![Pod42 gpt-3.5-turbo](assets/hasura-pod42-chatgpt-answer-3.png)


---
Maintained with :heart: by <a href="https://hasura.io">Hasura</a>

