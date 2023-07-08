from langchain.chat_models import ChatOpenAI
from decouple import config
from langchain.schema import SystemMessage, HumanMessage

OPENAI_API_KEY = config("OPENAI_API_KEY")


def get_completion(instruct, message, temperature=0.7, max_tokens=2 * 1024, model_name="gpt-3.5-turbo-0613"):
    chat = ChatOpenAI(
        temperature=temperature,
        max_tokens=max_tokens,
        model_name=model_name,
        openai_api_key=OPENAI_API_KEY
    )
    messages = [
        SystemMessage(content=instruct),
        HumanMessage(content=message),
    ]
    result = chat(messages).content
    return result

async def aget_completion(instruct, message, temperature=0.7, max_tokens=2 * 1024, model_name="gpt-3.5-turbo-0613"):
    chat = ChatOpenAI(
        temperature=temperature,
        max_tokens=max_tokens,
        model_name=model_name,
        openai_api_key=OPENAI_API_KEY
    )
    messages = [
        SystemMessage(content=instruct),
        HumanMessage(content=message),
    ]
    result = await chat.apredict_messages(messages)


    return result.content



def get_completion_with_context(context, message, temperature=0.7, max_tokens=2 * 1024,
                                model_name="gpt-3.5-turbo-0613"):
    chat = ChatOpenAI(
        temperature=temperature,
        max_tokens=max_tokens,
        model_name=model_name,
        openai_api_key=OPENAI_API_KEY
    )

    context.append(HumanMessage(content=message))
    result = chat(context).content
    return result