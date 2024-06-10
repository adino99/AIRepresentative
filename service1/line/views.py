from langchain.schema import AIMessage
from django.http.request import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import *

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from django.http import HttpResponse
from django.shortcuts import render
import os
import json
import sqlite3
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from bs4 import BeautifulSoup
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage, ImageSendMessage, UnfollowEvent, FollowEvent, VideoMessage, AudioMessage, FileMessage

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

OPENAI_API_KEY = '<your CHATGPT API KEY>'
llm_chatgpt = ChatOpenAI(model="gpt-3.5-turbo", temperature=1, api_key=OPENAI_API_KEY)

OLLAMA_HOST = '<YOUR OLLAMA HOST>'
OLLAMA_PORT = 11434
llm_ollama = ChatOllama(model="llama3:latest", base_url=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}")


LINE_CHANNEL_ACCESS_TOKEN = '<YOUR LINE ACCESS TOKEN>'
LINE_CHANNEL_SECRET = '<YOUR LINE SECRET>'
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def get_additional_faq_from_other(username, my_question):
    url = "http://localhost:7000/question"      # this is where other organization open webservice
    params = { 'u': username, 'q': my_question}
    response = requests.get(url, params=params) 
    if response.status_code == 200:
        # Print the text content of the response
        print("Response Text:")
        print(response.text)
        return response.text
    else:
        # Print an error message if the request failed
        print("Failed to retrieve data, status code:", response.status_code)
        return ""

@handler.add(event=MessageEvent, message=TextMessage)
def handle_text_message(event: MessageEvent):
    print("Source", event.source)
    print("User ID", event.source.user_id)
    print("Message", event.message)
    print("Message Type", event.message.type)
    print("Reply Token", event.reply_token)



    need_to_answer = decision_to_answer(event.source.user_id, event.message.text)

    if need_to_answer:

        need_to_route = decision_to_route(event.source.user_id, event.message.text)
        additional_faq = ""
        if need_to_route:
            additional_faq = get_additional_faq_from_other(event.source.user_id, event.message.text)

        message_out = main_process(event.source.user_id, event.message.text, additional_faq)
        txt_send_message = TextSendMessage(text=message_out)
        line_bot_api.reply_message(event.reply_token, txt_send_message)
        hist_obj = History(username=event.source.user_id, question=event.message.text, answer=message_out)
        hist_obj.save()

    else:
        txt_send_message = TextSendMessage(text="I don't know")
        line_bot_api.reply_message(event.reply_token, txt_send_message)

@handler.add(event=UnfollowEvent)
def handle_unfollow(event):
    # This function is called when someone adds the bot as a friend
    print("UNFRIEND Hiks")
    print(event)
    hist_obj = History.objects.filter(username=event.source.user_id)
    hist_obj.delete()

@handler.add(event=FollowEvent)
def handle_follow(event):
    # This function is called when someone adds the bot as a friend
    print("NEW FRIEND YEEY")
    print(event)
    

    message_out = "🌟 Hello from AI Representative! 🌟\n\nHi there! I'm Joy, your go-to AI for everything TIGP. Need help with forms, visa details, or anything else? Just ask, and let’s make your preparation for Taiwan as easy and fun as possible! 😊📝"
    
    txt_send_message = TextSendMessage(text=message_out)
    line_bot_api.reply_message(event.reply_token, txt_send_message)
    hist_obj = History(username=event.source.user_id, question="START", answer="START")
    hist_obj.save()

def getKG_route():
    knowledge_graphs = KnowledgeGraph.objects.filter(purpose='route')
    str_kgs = ""
    cnt = 1
    for i in knowledge_graphs:
        str_kgs += f"{cnt}. " + i.title + "\n"
        str_kgs += i.json + "\n"
        str_kgs += "\n"
        cnt += 1
    str_kgs += "\n"
    return str_kgs

def getKG_all():
    knowledge_graphs = KnowledgeGraph.objects.all()
    str_kgs = ""
    cnt = 1
    for i in knowledge_graphs:
        str_kgs += f"{cnt}. " + i.title + "\n"
        str_kgs += i.json + "\n"
        str_kgs += "\n"
        cnt += 1
    str_kgs += "\n"
    return str_kgs

def getQA():
    del_blank = FAQ.objects.filter(question='')
    del_blank.delete()
    del_blank = FAQ.objects.filter(answer='')
    del_blank.delete()
    # print(aaa)
    faqs = FAQ.objects.all().order_by('created_at')
    str_faqs = ""
    for i in faqs:
        str_faqs += "Q: " + i.question + "\n"
        str_faqs += "A: " + i.answer + "\n"
        str_faqs += "\n"
    str_faqs += "\n"
    return str_faqs

def getRule():
    rules = Rule.objects.all()
    cnt = 1
    str_rules = ""
    for i in rules:
        str_rules += f"{cnt}. {i.rule}\n"
        cnt +=1
    str_rules += "\n"
    return str_rules

def getHistory(username):
    history = History.objects.filter(username=username).order_by('created_at')
    ret = ""
    for i in history:
        ret += f"{i.created_at} Request: {i.question}\n"
        ret += f"{i.created_at} Response: {i.answer}\n"
        ret += "\n"
    ret += "\n"        
    return ret

def decision_to_route(username, my_question):
    print("---------------------- QUESTION ROUTE ------------------------")
    print(my_question)
    
    knowledge_graph_str_json_filter = getKG_route()
    q_and_a_str = getQA()
    rule_str = getRule()
    chat_str = getHistory(username)

    messages = [
        HumanMessage(content="These are our 'KNOWLEDGE GRAPH' in JSON format:"),  # This is the knowledge graph
        HumanMessage(content=knowledge_graph_str_json_filter),  # IN JSON FORMAT
        HumanMessage(content="These are our 'RULES':"),  # This is the rules
        HumanMessage(content=rule_str),
        HumanMessage(content=f"{my_question}\n"+
"""Does the answer to the question is in the 'KNOWLEDGE GRAPH'?
Answer just Yes or No.
If the answer is No, just only say 'NO'.
If the answer is Yes, just only say 'YES'.""")
    ] 

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm_ollama | StrOutputParser()

    input_data = {'question': my_question} 
    answer = chain.invoke(input_data)
    print("---------------------- ANSWER ----------------------")
    print(answer)


    return True if answer == 'YES' else False


def decision_to_answer(username, my_question):
    print("---------------------- QUESTION MYSELF ------------------------")
    print(my_question)
    
    knowledge_graph_str_json_filter = getKG_all()
    q_and_a_str = getQA()
    rule_str = getRule()
    chat_str = getHistory(username)

    messages = [
        HumanMessage(content="These are our 'KNOWLEDGE GRAPH' in JSON format:"),  # This is the knowledge graph
        HumanMessage(content=knowledge_graph_str_json_filter),  # IN JSON FORMAT
        HumanMessage(content="These are our 'RULES':"),  # This is the rules
        HumanMessage(content=rule_str),
        HumanMessage(content=f"{my_question}\n"+
"""Does the answer to the question is in the 'KNOWLEDGE GRAPH'?
Answer just Yes or No.
If the answer is No, just only say 'NO'.
If the answer is Yes, just only say 'YES'.""")
    ] 

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm_ollama | StrOutputParser()

    input_data = {'question': my_question} 
    answer = chain.invoke(input_data)
    print("---------------------- ANSWER ----------------------")
    print(answer)


    return True if answer == 'YES' else False

def main_process(username, my_question, additional_faq):
    print("---------------------- QUESTION ------------------------")
    print(my_question)
    
    knowledge_graph_str_json_filter = getKG_all()
    q_and_a_str = getQA() 
    q_and_a_str += "\n" + additional_faq + "\n"
    # q_and_a_str = additional_faq  + "\n"

    rule_str = getRule()
    chat_str = getHistory(username)

    messages = [
        HumanMessage(content="These are our 'CHAT HISTORY':"),  # This is the chat histories
        HumanMessage(content=chat_str),
        HumanMessage(content="These are our 'KNOWLEDGE GRAPH' in JSON format:"),  # This is the knowledge graph
        HumanMessage(content=knowledge_graph_str_json_filter),  # IN JSON FORMAT
        HumanMessage(content="These are our 'KNOWLEDGE BASE' in a Question and Answer format (FAQ):"),  # This is the QA as knowledge
        HumanMessage(content=q_and_a_str),
        HumanMessage(content="These are our 'RULES':"),  # This is the rules
        HumanMessage(content=rule_str),
        HumanMessage(content=f"Now, answer my question: {my_question}"),
    ] 

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm_ollama | StrOutputParser()

    input_data = {'question': my_question} 
    answer = chain.invoke(input_data)
    print("---------------------- ANSWER ----------------------")
    print(answer)


    return answer

def main_process_generate_faq(username, my_question, additional_faq):
    print("---------------------- QUESTION ------------------------")
    print(my_question)
    
    knowledge_graph_str_json_filter = getKG_all()
    q_and_a_str = getQA() 
    q_and_a_str += "\n" + additional_faq + "\n"
    rule_str = getRule()
    chat_str = getHistory(username)
    # print("KG", ":", knowledge_graph_str_json_filter)
    # print("FAQ", ":", q_and_a_str)
    # print("Rules", ":", rule_str)
    # print("History", ":", chat_str)

    messages = [
        HumanMessage(content="These are our 'CHAT HISTORY':"),  # This is the chat histories
        HumanMessage(content=chat_str),
        HumanMessage(content="These are our 'KNOWLEDGE GRAPH' in JSON format:"),  # This is the knowledge graph
        HumanMessage(content=knowledge_graph_str_json_filter),  # IN JSON FORMAT
        HumanMessage(content="These are our 'KNOWLEDGE BASE' in a Question and Answer format (FAQ):"),  # This is the QA as knowledge
        HumanMessage(content=q_and_a_str),
        HumanMessage(content="These are our 'RULES':"),  # This is the rules
        HumanMessage(content=rule_str),
        HumanMessage(content=f"Now, answer my question: {my_question}"),
        HumanMessage(content="Using your answer, please generate 10 FAQ with just format \nQ: <some question related to your answer>\nQ: <some answer related to your question>\n\n"),
    ] 

    # print("PROMPT")
    # print(messages)

    prompt = ChatPromptTemplate.from_messages(messages)
    chain = prompt | llm_ollama | StrOutputParser()

    input_data = {'question': my_question} 
    answer = chain.invoke(input_data)
    print("---------------------- ANSWER ----------------------")
    print(answer)


    return answer

def question(request):
    if 'q' not in request.GET:
        return HttpResponse('use parameter ?u=[your name]&q=[your question]')
    if 'u' not in request.GET:
        return HttpResponse('use parameter ?u=[your name]&q=[your question]')
    my_question = request.GET['q']
    my_username = request.GET['u']
    print(my_username, ":", my_question)
    my_answer = main_process_generate_faq(my_username, my_question, "")
    hist_obj = History(username=my_username, question=my_question, answer=my_answer)
    hist_obj.save()
    return HttpResponse(my_answer)


@csrf_exempt
@require_POST
def line(request: HttpRequest):
    signature = request.headers["X-Line-Signature"]
    body = request.body.decode()

    try:
        handler.handle(body, signature)
        print(body)
        print(signature)
    except InvalidSignatureError:
        # CHANNEL_ACCESS_TOKEN
        messages = (
            "Invalid signature. Please check your channel access token/channel secret."
        )
        logger.error(messages)
        return HttpResponseBadRequest(messages)
    return HttpResponse("OK")
