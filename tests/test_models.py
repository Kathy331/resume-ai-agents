# make sure to cd to the root of before running
# python test_models.py

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # if you use .env

client = OpenAI()

models = client.models.list()
for model in models.data:
    print(model.id)

# Here is my list of models as of July 2025, more detailes on API reference page in docs folders
# gpt-4-0613
# gpt-4
# gpt-3.5-turbo
# o4-mini-deep-research-2025-06-26
# codex-mini-latest
# gpt-4o-realtime-preview-2025-06-03
# gpt-4o-audio-preview-2025-06-03
# o4-mini-deep-research
# davinci-002
# babbage-002
# gpt-3.5-turbo-instruct
# gpt-3.5-turbo-instruct-0914
# dall-e-3
# dall-e-2
# gpt-4-1106-preview
# gpt-3.5-turbo-1106
# tts-1-hd
# tts-1-1106
# tts-1-hd-1106
# text-embedding-3-small
# text-embedding-3-large
# gpt-4-0125-preview
# gpt-4-turbo-preview
# gpt-3.5-turbo-0125
# gpt-4-turbo
# gpt-4-turbo-2024-04-09
# gpt-4o
# gpt-4o-2024-05-13
# gpt-4o-mini-2024-07-18
# gpt-4o-mini
# gpt-4o-2024-08-06
# chatgpt-4o-latest
# o1-preview-2024-09-12
# o1-preview
# o1-mini-2024-09-12
# o1-mini
# gpt-4o-realtime-preview-2024-10-01
# gpt-4o-audio-preview-2024-10-01
# gpt-4o-audio-preview
# gpt-4o-realtime-preview
# omni-moderation-latest
# omni-moderation-2024-09-26
# gpt-4o-realtime-preview-2024-12-17
# gpt-4o-audio-preview-2024-12-17
# gpt-4o-mini-realtime-preview-2024-12-17
# gpt-4o-mini-audio-preview-2024-12-17
# o1-2024-12-17
# o1
# gpt-4o-mini-realtime-preview
# gpt-4o-mini-audio-preview
# o3-mini
# o3-mini-2025-01-31
# gpt-4o-2024-11-20
# gpt-4o-search-preview-2025-03-11
# gpt-4o-search-preview
# gpt-4o-mini-search-preview-2025-03-11
# gpt-4o-mini-search-preview
# gpt-4o-transcribe
# gpt-4o-mini-transcribe
# o1-pro-2025-03-19
# o1-pro
# gpt-4o-mini-tts
# o4-mini-2025-04-16
# o4-mini
# gpt-4.1-2025-04-14
# gpt-4.1
# gpt-4.1-mini-2025-04-14
# gpt-4.1-mini
# gpt-4.1-nano-2025-04-14
# gpt-4.1-nano
# gpt-image-1
# gpt-3.5-turbo-16k
# tts-1
# whisper-1
# text-embedding-ada-002