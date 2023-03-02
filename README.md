# hasura-pod42

A Discord bot to to answer question based on docs using the latest ChatGPT API, built on [Hasura GraphQL
Engine](https://github.com/hasura/graphql-engine) and [LangChain](https://github.com/hwchase17/langchain).

[![Edit hasura-pod42](https://codesandbox.io/static/img/play-codesandbox.svg)](https://codesandbox.io/p/github/hasura/hasura-pod42/master?fontsize=14)

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

- Deploy GraphQL Engine on Hasura Cloud and setup PostgreSQL via Neon:
  [![Deploy to Hasura Cloud](https://graphql-engine-cdn.hasura.io/img/deploy_to_hasura.png)](https://cloud.hasura.io/signup)
- Get the Hasura app URL (say `hasura-pod42.hasura.app`)
- Clone this repo:
  ```bash
  git clone https://github.com/hasura/pod42.git
  ```
- [Install Hasura CLI](https://hasura.io/docs/latest/graphql/core/hasura-cli/install-hasura-cli.html)
- Goto `hasura/` and edit `config.yaml`:
  ```yaml
  endpoint: https://hasura-pod42.hasura.app
  ```
- Apply the migrations:
  ```bash
  hasura metadata apply
  hasura migrate apply
  hasura metadata reload
  ```
- Edit `HASURA_GRAPHQL_ENGINE_HOSTNAME` in `src/constants.js` and set it to the Hasura app URL:
  ```js
  const HASURA_GRAPHQL_ENGINE_HOSTNAME = 'realtime-backend2.hasura.app/v1/graphql';
  ```
- Run the app (go to the root of the repo):
  ```bash
  npm start
  ```

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

