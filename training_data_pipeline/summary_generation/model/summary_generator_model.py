import boto3
import streamlit as st
from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrock
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate

from graig_nlp.summary_generation.model.template import (
    TEMPLATE,
    EXAMPLES,
)


def prompt_generator():
    example_prompt = PromptTemplate.from_template("input: {input}\n AI: {output}")
    instructions = TEMPLATE
    examples = EXAMPLES
    input_query = """
    input: {query}
    """
    prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix=instructions,
        suffix=input_query,
        input_variables=["query"],
    )
    return prompt


def generate_summary(data, llm_client="anthropic"):
    if llm_client == "anthropic":
        anthropic_api_key = st.secrets.api_key.anthropic
        llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=0.6,
            anthropic_api_key=anthropic_api_key,
        )
    else:
        # Bedrock Client
        bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=st.secrets.aws.AWS_REGION,
            aws_access_key_id=st.secrets.aws.ACCESS_KEY,
            aws_secret_access_key=st.secrets.aws.SECRET_ACCESS_KEY,
            aws_session_token=st.secrets.aws.AWS_SESSION_TOKEN,
        )

        # Bedrock model
        llm = ChatBedrock(
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            client=bedrock_client,
            model_kwargs={"temperature": 0.2},
        )

    # intervals
    llm_data = {"query": data}
    prompt = prompt_generator()
    chain = prompt | llm
    summary = chain.invoke(llm_data)

    return summary
