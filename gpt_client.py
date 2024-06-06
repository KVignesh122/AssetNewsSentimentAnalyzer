from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import tiktoken

ENCODING_STANDARD = "cl100k_base"


def get_tokens(text):
    enc = tiktoken.get_encoding(ENCODING_STANDARD)
    return enc.encode(text)


def get_token_length(text: str):
    return len(get_tokens(text))


def decode_tokens(tokens):
    enc = tiktoken.get_encoding(ENCODING_STANDARD)
    return enc.decode(tokens)


def chunk(text: str, max_token_len=2000):
    text_tk_length = get_token_length(text)
    if text_tk_length > max_token_len:
        tokens = get_tokens(text)
        return decode_tokens(tokens[:max_token_len])
    return text


keyvault = SecretClient(vault_url="https://uptalevaultdev.vault.azure.net/", credential=DefaultAzureCredential())
# print(keyvault.get_secret("UptaleOpenAI").value)
keyvault = AzureOpenAI(
    azure_endpoint = "https://uptale-openai-dev-global.openai.azure.com/", 
    # api_key = keyvault.get_secret("UptaleOpenAI").value, # Retrieve the API key from the Key Vault
    api_key="c091fd8d60e942ac85ab43e6e98ad56d",
    api_version="2024-02-15-preview"
)
MODEL = "uptale-gpt-35-turbo"


def get_gpt_response(user_prompt: str, system_instruction=None):
    if system_instruction:
        gpt_prompt = [
            {"role":"system","content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]
    else:
        gpt_prompt = [
            {"role": "user", "content": user_prompt}
        ]

    response = keyvault.chat.completions.create(
        model=MODEL,
        messages = gpt_prompt
    )
    return response.choices[0].message.content
