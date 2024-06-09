from oai import MY_KEY
from openai import OpenAI
import tiktoken

ENCODING_STANDARD = "cl100k_base"
ANALYSER_INSTR = """You will be provided with a few financial/technical analysis writeups, 
news content, or opinion articles by the user. Based on these content, determine if the asset 
being requested by the user has a overall bullish, bearish, or neutral sentiment. Follow the instructions 
of the user closely.
"""


def get_tokens(text: str):
    enc = tiktoken.get_encoding(ENCODING_STANDARD)
    return enc.encode(text)


def get_token_length(text: str):
    return len(get_tokens(text))


def decode_tokens(tokens):
    enc = tiktoken.get_encoding(ENCODING_STANDARD)
    return enc.decode(tokens)


def chunk(text: str, max_token_len=3000):
    text_tk_length = get_token_length(text)
    if text_tk_length > max_token_len:
        tokenized_text = get_tokens(text)
        return decode_tokens(tokenized_text[:max_token_len])
    return text


def get_gpt_response(user_prompt: str, openai_key: str, preferred_model="gpt-3.5-turbo", system_instruction=None):
    client = OpenAI(api_key=openai_key)

    if system_instruction is not None:
        gpt_prompt = [
            {"role":"system","content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]
    else:
        gpt_prompt = [
            {"role": "user", "content": user_prompt}
        ]

    response = client.chat.completions.create(
        model=preferred_model,
        messages=gpt_prompt,
        max_tokens=10
    )
    return response.choices[0].message.content
