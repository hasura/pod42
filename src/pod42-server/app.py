import os
import logging
import pinecone
from langchain.vectorstores.pinecone import Pinecone
from langchain.chains import VectorDBQAWithSourcesChain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain import OpenAI, PromptTemplate
from langchain.llms import OpenAIChat
from sanic import Sanic
from sanic import response
import json
import asyncio
import requests
import tiktoken
logger = logging.getLogger()
logger.setLevel(logging.INFO)

PINECONE_API_KEY = os.environ['PINECONE_API_KEY']
PINECONE_INDEX_KEY = os.environ['PINECONE_INDEX_KEY']
OPEN_API_KEY = os.environ['OPEN_API_KEY']

ADMIN_SECRET = os.environ['ADMIN_SECRET']
HGE_ENDPOINT = os.environ['HGE_ENDPOINT']
HGE_URL = HGE_ENDPOINT + '/v1/graphql'
logging.basicConfig(level=logging.INFO)

HEADERS = {
    'Content-Type': 'application/json',
    'X-Hasura-Admin-Secret': ADMIN_SECRET,
}

query = """
mutation InsertAnswerOnSlackWithSourcesRefQuestion($Id: bigint!, $answer: String!, $sources:String!) {
    insert_answers_slack_one(
    	object:{
        question_id: $Id,
        answer: $answer,
        sources: $sources
      }
    ) {
    id
    question_id
    answer
    sources
  }
}
"""
EXAMPLE_PROMPT = PromptTemplate(
    template=">Example:\nContent:\n---------\n{page_content}\n----------\nSource: {source}",
    input_variables=["page_content", "source"],
)
template = """You are an AI assistant for the Hasura. The documentation is located at https://hasura.io/docs/latest/.
You are given the following extracted parts of a long document and a question. Provide a detailed answer with references ("SOURCES").
You should only use sources that are explicitly listed as a "source" in the context. Do NOT make up a source that is not listed.
If the question includes a request for code, provide a code block directly from the documentation.
If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
Do NOT assume a capability of Hasura which is not stated in the context.
ALWAYS return a list of "SOURCES" part in your answer.

Question: {question}
=========
{context}
=========
Answer:"""
PROMPT = PromptTemplate(template=template, input_variables=["question", "context"])
tiktoken_encoder  = tiktoken.get_encoding("gpt2")

def page_content(doc):
    return doc.page_content
def reduce_tokens_below_limit(docs, limit=3375):
    tokens = len(tiktoken_encoder.encode("".join(map(page_content, docs))))
    return docs if (tokens <= limit) else reduce_tokens_below_limit(docs[:-1])

class MyVectorDBQAWithSourcesChain(VectorDBQAWithSourcesChain):
    def _get_docs(self, inputs):
        question = inputs[self.question_key]
        docs = self.vectorstore.similarity_search(question, k=self.k)
        return reduce_tokens_below_limit(docs)

def blocking_chain(chain, request):
    return chain(request)

async def lambda_handler(event):
    logger.info("Request: %s", event)
    response_code = 200

    embeddings = OpenAIEmbeddings(openai_api_key=OPEN_API_KEY)
    pinecone.init(api_key=PINECONE_API_KEY, environment="us-west1-gcp")
    doc_chain = load_qa_with_sources_chain(
        OpenAIChat(temperature=0, openai_api_key=OPEN_API_KEY),
        chain_type="stuff",
        document_variable_name="context",
        prompt=PROMPT,
        document_prompt=EXAMPLE_PROMPT
    )
    store = Pinecone(pinecone.Index(PINECONE_INDEX_KEY), embeddings.embed_query, "text")
    chain = MyVectorDBQAWithSourcesChain(combine_document_chain=doc_chain, vectorstore=store, k=5)


    body = event.get('body')
    logger.info(body)

    question = ""
    id = "-1"

    if body is not None:
        question = body.get('question')
        id = body.get('id')


    result = await asyncio.to_thread(blocking_chain, chain, {"question": question})
    logger.info(result)

    qv = {'Id': id, 'answer': result["answer"], 'sources': result["sources"]}
    jsonBody = {'query': query, 'variables': qv}


    resp = await asyncio.to_thread(requests.post, HGE_URL, data=json.dumps(jsonBody), headers=HEADERS)

    response = {
        'statusCode': response_code,
        'body': resp.json()
    }

    logger.info("Response: %s", response)
    return response



app = Sanic("pod42-bot")

@app.route("/")
async def hello_world(request):
    return response.text("Hello World!")

@app.post('/question')
async def post_request(request):
    return response.json(await lambda_handler(request.json))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
