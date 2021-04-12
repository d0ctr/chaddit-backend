from flask import jsonify, request, Blueprint

from src.models.thread import ThreadModel
from src.models.topic import TopicModel
from src.models.topictag import TopicTagModel
from src.schemas.thread import ThreadSchema
from src.schemas.topic import TopicSchema
from ..shared.responses import custom_response

from sqlalchemy.orm import load_only

import re
from urllib import parse

import math
from collections import Counter

search_api = Blueprint('search', __name__)
thread_schema = ThreadSchema()
topic_schema = TopicSchema()

tag_match = r'#[^\s#]+'
WORD = re.compile(r'\w+')

def text_to_vector(text):
  words = WORD.findall(text)
  return Counter(words)

def get_cosine(str1, str2):
  vec1 = text_to_vector(str1.lower())
  vec2 = text_to_vector(str2.lower())
  intersection = set(vec1.keys()) & set(vec2.keys())
  numerator = sum([vec1[x] * vec2[x] for x in intersection])

  sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
  sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
  denominator = math.sqrt(sum1) * math.sqrt(sum2)

  if not denominator:
    return 0.0
  else:
    return float(numerator) / denominator

def get_topic_result(query, tags):
  orderbyasc = request.args.get('orderby', type = str)
  orderbydesc = request.args.get('orderbydesc', type = str)

  if orderbyasc:
    topics = TopicModel.get_all(orderby=orderbyasc, order='asc')
  elif orderbydesc:
    topics = TopicModel.get_all(orderby=orderbyasc, order='desc')
  else:
    topics = TopicModel.get_all()
  if len(tags) > 0:
    topic_tags = TopicTagModel.query.filter(TopicTagModel.tag.in_(tags)).options(load_only('topic_id')).all()
    topic_tags = [id.topic_id for id in topic_tags]
    topics = topics.filter(TopicModel.topic_id.in_(topic_tags))
  if len(query) > 0:
    res = []
    for topic in topics.all():
      if get_cosine(topic.topic_title, query) >= 0.5:
        res.append(topic)
  else:
    res = topics.all()
  return res

def get_thread_result(query, tags):
  orderbyasc = request.args.get('orderby', type = str)
  orderbydesc = request.args.get('orderbydesc', type = str)

  if orderbyasc:
    threads = ThreadModel.get_all(orderby = orderbyasc, order = 'asc')
  elif orderbydesc:
    threads = ThreadModel.get_all(orderby = orderbydesc, order = 'desc')
  else:
    threads = ThreadModel.get_all()
  if len(tags) > 0:
    topic_tags = TopicTagModel.query.filter(TopicTagModel.tag.in_(tags)).options(load_only('topic_id')).all()
    topic_tags = [id.topic_id for id in topic_tags]
    threads = threads.filter(ThreadModel.topic_id.in_(topic_tags))
  if len(query) > 0:
    res = []
    for thread in threads.all():
      if get_cosine(thread.thread_title, query) >= 0.5:
        res.append(thread)
  else:
    res = threads.all()
  return res

def get_threads():
  orderbyasc = request.args.get('orderby', type = str)
  orderbydesc = request.args.get('orderbydesc', type = str)

  if orderbyasc:
    threads = ThreadModel.get_all(orderby = orderbyasc, order = 'asc')
  elif orderbydesc:
    threads = ThreadModel.get_all(orderby = orderbydesc, order = 'desc')
  else:
    threads = ThreadModel.get_all()
  return threads \
    .all()

def get_topics():
  orderbyasc = request.args.get('orderby', type = str)
  orderbydesc = request.args.get('orderbydesc', type = str)

  if orderbyasc:
    topics = TopicModel.get_all(orderby=orderbyasc, order='asc')
  elif orderbydesc:
    topics = TopicModel.get_all(orderby=orderbyasc, order='desc')
  else:
    topics = TopicModel.get_all()
  return topics \
    .all()

@search_api.route('/search/threads', methods=['GET'])
def get_threads_route():
  result = get_threads()
  result = thread_schema.dump(result, many=True)

  return custom_response(result, 200)

@search_api.route('/search/topics', methods=['GET'])
def get_topics_route():
  result = get_topics()
  result = topic_schema.dump(result, many=True)

  return custom_response(result, 200)

@search_api.route('/search/thread', methods=['GET'])
def get_thread_search():
  if 'query' in request.args:
    query = request.args['query']
  else:
    return custom_response({"error":"Query parameter not found"}, 400)

  query = query[1:-1]
  query = parse.unquote(query)
  tags = re.findall(tag_match, query)

  # Taking out tags from query
  query = re.sub(tag_match, '', query)
  # Removing multiple spaces form query
  query = re.sub(r'\s+', ' ', query)
  # Removing spaces from start and end of string
  query = query.strip()
  
  for i in range(len(tags)):
    tags[i] = re.sub(r'#', '', tags[i])

  result = get_thread_result(query, tags)
  result = thread_schema.dump(result, many=True)

  return custom_response(result, 200)

@search_api.route('/search/topic', methods=['GET'])
def get_topic_search():
  if 'query' in request.args:
    query = request.args['query']
  else:
    return custom_response({"error":"Query parameter not found"}, 400)

  query = query[1:-1]
  query = parse.unquote(query)
  tags = re.findall(tag_match, query)
  
  #Taking out tags from query
  query = re.sub(tag_match, '', query)
  # Removing multiple spaces form query
  query = re.sub(r'\s+', ' ', query)
  # Removing spaces from start and end of string
  query = query.strip()
  
  for i in range(len(tags)):
    tags[i] = re.sub(r'#', '', tags[i])

  result = get_topic_result(query, tags)
  result = topic_schema.dump(result, many=True)

  return custom_response(result, 200)

