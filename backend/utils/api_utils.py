import os
import openai
from openai import OpenAI
# import ipdb
import threading
import time
import requests
from queue import Queue
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

def prompt_format(prompt_template, prompt_content):
    return prompt_template.format(**prompt_content)


def get_response(message, model, max_tokens, temperature, candidate_n):
    client = OpenAI(api_key=OPENAI_API_KEY, base_url=BASE_URL)
    response = client.chat.completions.create(model=model,
                                                messages=message,
                                                max_tokens=max_tokens,
                                                temperature=temperature,
                                                n=candidate_n)
    if candidate_n == 1:
        return_response = response.choices[0].message.content
    else:
        return_response = [response.choices[i].message.content for i in range(candidate_n)]
    return return_response
    


# gpt-3.5-turbo-1106, qwen2.5-72b-instruct
def api_single_request(message, model="gpt-3.5-turbo-1106", max_tokens=128, temperature=0.7, candidate_n=1,
                       rank=-1, result_queue=None):
    request_cnt = 0
    if candidate_n == 1:
        temperature = 0
    while True:
        request_cnt += 1
        if request_cnt > 20:
            exit(0)
        try:
            return_response = get_response(message, model, max_tokens, temperature, candidate_n)#
            # single thread request
            if rank == -1:
                return return_response
            # multi thread request
            else:
                result_queue.put({
                    'rank': rank,
                    'response': return_response
                })
                return
        except Exception as e:
            print(e)
            print("API ERROR!")
            time.sleep(1)
            continue


def api_multi_request(messages, model="gpt-3.5-turbo-1106", max_tokens=128, temperature=0.7, candidate_n=1):
    threads = []
    result_queue = Queue()
    gathered_response = []
    for i in range(len(messages)):
        t = threading.Thread(target=api_single_request,
                             args=(messages[i], model, max_tokens, temperature, candidate_n, i, result_queue))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    while not result_queue.empty():
        gathered_response.append(result_queue.get())
    # assert len(gathered_response) == len(messages)
    gathered_response.sort(key=lambda x: x['rank'])
    gathered_response = [x['response'] for x in gathered_response]
    return gathered_response


def get_api_request(messages, model="gpt-3.5-turbo-1106", max_tokens=128, temperature=0.7, candidate_n=1):
    if len(messages) == 1:
        return [api_single_request(messages[0], model, max_tokens, temperature, candidate_n)]
    else:
        return api_multi_request(messages, model, max_tokens, temperature, candidate_n)

