import json
import unittest
from types import SimpleNamespace
from datetime import datetime

from dotenv import load_dotenv

from src.app import create_app
from src.config import app_config
from src.models import ChatModel, PostModel, RoleModel, ThreadModel, TopicModel
from tests.schemas import ChatSchema, PostSchema, RoleSchema, ThreadSchema, TopicSchema, TopicTagSchema, UserSchema
from src.shared.authetification import Auth
from src.shared.constants import RoleId
from src.views.user import email_exists

load_dotenv(override=False)
app = create_app('development')


class FlaskTest(unittest.TestCase):
    admin_token = ""
    user_token = ""
    test_topic_id = 1
    test_thread_id = 1
    test_user_id = 1
    test_chat_id = 1
    test_post_id = 1
    test_root_post_id = 1
    test_message_id = 1

    def setUp(self):
        self.tester = app.test_client(self)
        login_response = self.tester.post('/api/chaddit/c/login',
                                          json={
                                              'user_email': 'admin@chaddit.tk',
                                              'user_pass': 'admin'
                                          })
        self.admin_token = json.loads(login_response.data).get('api_token')

    def test_login(self):
        response = self.tester.post(
            '/api/chaddit/c/login',
            json={
                'user_email': 'admin@chaddit.tk',
                'user_pass': 'admin'
            })
        self.admin_token = json.loads(response.data).get('api_token')
        self.assertEqual(type(self.admin_token), str)
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        response = self.tester.post(
            '/api/chaddit/c/register',
            json={
                'user_email': 'user@chaddit.tk',
                'user_pass': 'user',
                'user_name': 'user'
            })
        self.user_token = response.get_json().get('api_token')
        self.assertEqual(response.status_code, 201)

    def test_get_topics(self):
        response = self.tester.get('/api/chaddit/c/topics')
        response_jsons = json.loads(response.data)
        for response_json in response_jsons:
            self.assertEqual(type(response_json.get('topic_id')), int)
            self.assertEqual(type(response_json.get('topic_title')), str)
            self.assertEqual(type(response_json.get('created_at')), str)
            self.assertEqual(type(response_json.get('updated_at')), str)
            self.assertEqual(type(response_json.get('author_id')), int)
            self.assertEqual(type(response_json.get('tags')), list)
            self.assertTrue(type((response_json.get('image')) == str) or (type(response_json.get('image')) == None))
            self.assertEqual(type(response_json.get('active')), bool)
            self.assertEqual(type(response_json.get('author')), dict)
            self.assertEqual(type(response_json.get('threads_count')), int)
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_on_update_user(self):
        response = self.tester.patch(
            f'/api/chaddit/c/user',
            headers={'api-token': str(self.admin_token)},
            json={
                'user_name': 'changed'
            },
            follow_redirects=True
        )
        response_json = json.loads(response.data)
        self.assertEqual(type(response_json.get('user_id')), int)
        self.assertEqual(type(response_json.get('user_name')), str)
        self.assertEqual(type(response_json.get('user_email')), str)
        self.assertTrue(type((response_json.get('avatar')) == str) or (type(response_json.get('avatar')) == None))
        self.assertEqual(type(response_json.get('role_id')), int)
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_types_post_topic(self):
        response = self.tester.post(
            f'/api/chaddit/c/topic',
            header={'api-token': str(self.admin_token)},
            json={
                'topic_title': "test topic title",
                'tags': [
                    {'test_tag': "test_tag_data"}
                ]
            }
        )
        response_json = json.loads(response.data)
        self.assertEqual(type(response_json.get('topic_id')), int)
        self.assertEqual(type(response_json.get('topic_title')), str)
        self.assertEqual(type(response_json.get('created_at')), str)
        self.assertEqual(type(response_json.get('updated_at')), str)
        self.assertEqual(type(response_json.get('author_id')), int)
        self.assertEqual(type(response_json.get('tags')), list)
        self.assertTrue(type((response_json.get('image')) == str) or (type(response_json.get('image')) == None))
        self.assertEqual(type(response_json.get('active')), bool)
        self.assertEqual(type(response_json.get('author')), dict)
        self.assertEqual(type(response_json.get('threads_count')), int)
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_types_update_topic(self):
        response = self.tester.patch(
            f'chaddit/c/topic/${self.test_topic_id}',
            headers={'api_token': self.admin_token}
        )
        response_json = json.loads(response.data)
        self.assertEqual(type(response_json.get('topic_id')), int)
        self.assertEqual(type(response_json.get('topic_title')), str)
        self.assertEqual(type(response_json.get('created_at')), str)
        self.assertEqual(type(response_json.get('updated_at')), str)
        self.assertEqual(type(response_json.get('author_id')), int)
        self.assertEqual(type(response_json.get('tags')), list)
        self.assertTrue(type((response_json.get('image')) == str) or (type(response_json.get('image')) == None))
        self.assertEqual(type(response_json.get('active')), bool)
        self.assertEqual(type(response_json.get('author')), dict)
        self.assertEqual(type(response_json.get('threads_count')), int)
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_types_create_thread(self):
        response = self.tester.post(
            f'chaddit/c/thread',
            headers={
                'api-token': self.admin_token,
                'topic_id': self.test_topic_id
            },
            json={
                'thread_title': "test thread title",
                'posts': [{'body': "test body"}]
            }
        )
        response_json = json.loads(response.data)
        self.assertEqual(type(response_json.get('thread_id')), int)
        self.assertEqual(type(response_json.get('thread_title')), str)
        self.assertEqual(type(response_json.get('created_at')), str)
        self.assertEqual(type(response_json.get('updated_at')), str)
        self.assertEqual(type(response_json.get('author_id')), int)
        self.assertTrue(type((response_json.get('image')) == str) or (type(response_json.get('image')) == None))
        self.assertEqual(type(response_json.get('active')), bool)
        self.assertEqual(type(response_json.get('author')), dict)
        self.assertEqual(type(response_json.get('topic_id')), int)
        self.assertEqual(type(response_json.get('posts')), dict)
        self.assertEqual(type(response_json.get('author')), dict)
        self.assertEqual(type(response_json.get('posts_count')), dict)
        self.assertEqual(type(response_json.get('views')), int)
        statusCode = response.status_code
        self.assertEqual(statusCode, 201)

    def test_types_update_thread(self):
        response = self.tester.patch(
            f'chaddit/c/thread/${self.test_thread_id}',
            headers={
                'api-token': self.admin_token,
            },
            json={
                'views': 100
            }
        )
        response_json = json.loads(response.data)
        self.assertEqual(type(response_json.get('thread_id')), int)
        self.assertEqual(type(response_json.get('thread_title')), str)
        self.assertEqual(type(response_json.get('created_at')), str)
        self.assertEqual(type(response_json.get('updated_at')), str)
        self.assertEqual(type(response_json.get('author_id')), int)
        self.assertTrue(type((response_json.get('image')) == str) or (type(response_json.get('image')) == None))
        self.assertEqual(type(response_json.get('active')), bool)
        self.assertEqual(type(response_json.get('author')), dict)
        self.assertEqual(type(response_json.get('topic_id')), int)
        self.assertEqual(type(response_json.get('posts')), dict)
        self.assertEqual(type(response_json.get('author')), dict)
        self.assertEqual(type(response_json.get('posts_count')), dict)
        self.assertEqual(type(response_json.get('views')), int)
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_types_create_post(self):
        response = self.tester.patch(
            f'chaddit/c/post',
            headers={
                'api-token': self.admin_token,
                'thread_id': self.test_thread_id,
                'post_id': self.test_post_id
            },
            json={
                'body': 'test post'
            }
        )
        response_json = json.loads(response.data)
        self.assertEqual(type(response_json.get('post_id')), int)
        self.assertEqual(type(response_json.get('body')), str)
        self.assertEqual(type(response_json.get('created_at')), str)
        self.assertEqual(type(response_json.get('updated_at')), str)
        self.assertEqual(type(response_json.get('author_id')), int)
        self.assertTrue(type((response_json.get('image')) == str) or (type(response_json.get('image')) == None))
        self.assertEqual(type(response_json.get('active')), bool)
        self.assertEqual(type(response_json.get('author')), dict)
        self.assertEqual(type(response_json.get('root_post_id')), int)
        self.assertEqual(type(response_json.get('thread_id')), int)
        self.assertEqual(type(response_json.get('responses')), dict)
        statusCode = response.status_code
        self.assertEqual(statusCode, 201)

    def test_types_create_message(self):
        response = self.tester.patch(
            f'chaddit/c/message',
            headers={
                'api-token': self.admin_token,
                'chat_id': self.test_chat_id,
            },
            json={
                'body': 'test message'
            }
        )
        response_json = json.loads(response.data)
        self.assertEqual(type(response_json.get('message_id')), int)
        self.assertEqual(type(response_json.get('body')), str)
        self.assertEqual(type(response_json.get('created_at')), str)
        self.assertEqual(type(response_json.get('updated_at')), str)
        self.assertEqual(type(response_json.get('author_id')), int)
        self.assertEqual(type(response_json.get('active')), bool)
        self.assertEqual(type(response_json.get('chat_id')), int)
        statusCode = response.status_code
        self.assertEqual(statusCode, 201)

    def test_types_create_chat(self):
        response = self.tester.post(
            f'chaddit/c/chat',
            headers={
                'api-token': self.admin_token,
            },
            json={
                'topic_id': self.test_topic_id
            }
        )
        response_json = json.loads(response.data)
        self.assertEqual(type(response_json.get('chat_id')), int)
        self.assertEqual(type(response_json.get('created_at')), str)
        self.assertEqual(type(response_json.get('updated_at')), str)
        self.assertEqual(type(response_json.get('full')), bool)
        self.assertEqual(type(response_json.get('active')), bool)
        self.assertEqual(type(response_json.get('participants')), dict)
        self.assertEqual(type(response_json.get('topic_id')), int)
        statusCode = response.status_code
        self.assertEqual(statusCode, 201)



    # def test_post_topic_successful(self):

    #     response = self.tester.post(
    #         '/chaddit/c/topic',
    #         json={
    #                 'topic_title': 'Test',
    #                 'tags':
    #                         [
    #                             {'tag': "test"}
    #                         ]
    #               },
    #         headers={'api-token': self.admin_token}
    #     )
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 201)

    # def test_threads(self):

    #     response = self.tester.get(
    #         '/chaddit/c/threads',
    #         headers={'topic-id': self.test_topic_id}
    #     )
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_chats(self):

    #     response = self.tester.get(
    #         '/chaddit/c/chats',
    #         headers={'api_token': self.admin_token})
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # # def test_chats_models(self):
    # #
    # #     response = self.tester.get(
    # #         '/chaddit/c/chats',
    # #         headers={'api_token': self.admin_token})
    # #     data = json.loads(response.data, object_hook=lambda d: SimpleNamespace(**d))
    # #     self.assertTrue(data, bool)

    # def test_bad_request(self):

    #     response = self.tester.get("chaddit/c/search/topic?query='Test'")
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_on_email_not_exists(self):
    #     app.app_context().push()
    #     exists = email_exists("not_existing@chaddit.tk")
    #     self.assertEqual(exists, False)

    # def test_on_email_exists(self):
    #     app.app_context().push()
    #     exists = email_exists("admin@chaddit.tk")
    #     self.assertEqual(exists, True)

    # def compare_db_and_endpoint_chats(self):
    #     app.app_context().push()
    #     db_chats = ChatModel.get_by_id(self.test_user_id)

    #     response = self.tester.get(
    #         '/chaddit/c/chats',
    #         headers={'api_token': self.admin_token})
    #     data = json.loads(response.data, object_hook=lambda d: SimpleNamespace(**d))
    #     self.assertNotEqual(db_chats, data)

    # def test_get_non_exists_db_chat_by_id(self):
    #     app.app_context().push()
    #     db_chats = ChatModel.get_by_id(self.test_chat_id)
    #     self.assertEqual(None, db_chats.topic_id)

    # def test_get_chat(self):

    #     response = self.tester.get(f"chaddit/c/chat/${self.test_chat_id}", headers={
    #         'api_token': self.admin_token
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_get_non_existing_chat(self):

    #     response = self.tester.get(f"chaddit/c/chat/${self.test_chat_id}", headers={
    #         'api_token': self.admin_token
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 404)

    # # posts
    # def test_get_posts_from_thread(self):

    #     response = self.tester.get("chaddit/c/posts", headers={
    #         'thread_id': self.test_thread_id
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_get_post(self):

    #     response = self.tester.get(f"chaddit/c/post/${self.test_post_id}")
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_get_non_existing_post(self):

    #     response = self.tester.get(f"chaddit/c/post/${self.test_post_id}")
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 400)

    # def test_get_thread(self):
    #     tester = app.client.test_client()
    #     response = self.tester.get('/chaddit/c/threads',
    #                           headers={
    #                               'post_id': self.test_post_id,
    #                               'thread_id': self.test_thread_id,
    #                               'user_id': self.test_user_id,
    #                               'topic_id': self.test_topic_id
    #                           })
    #     statusCode = response.status_code
    #     if statusCode != 200:
    #         print(response.data)
    #     self.assertEqual(statusCode, 200)

    # # user tests
    # def test_login(self):

    #     response = self.tester.get("chaddit/c/user", headers={
    #         'api_token': self.admin_token
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 307)

    # def test_get_user(self):

    #     response = self.tester.get(f"chaddit/c/user/${self.test_user_id}", headers={
    #         'api_token': self.admin_token
    #     })
    #     statusCode = response.status_code
    #     if statusCode != 200:
    #         print(response.data)
    #     self.assertEqual(statusCode, 200)

    # def test_get_all_users(self):

    #     response = self.tester.get("chaddit/c/users", headers={
    #         'role_id': RoleId.ADMINISTRATOR,
    #         'api_token': self.admin_token
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_get_all_users_bad_role(self):

    #     response = self.tester.get("chaddit/c/users", headers={
    #         'api_token': self.user_token
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 400)

    # def test_get_not_existing_user(self):

    #     response = self.tester.get("chaddit/c/user/-1", headers={
    #         'api_token': self.admin_token
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 404)

    # # def test_successful_register(self):
    # #
    # #     response = self.tester.post("chaddit/c/register", headers={
    # #         'user_email': 'usov@gmail.com',
    # #         'api_token': admin_token
    # #     })
    # #     statusCode = response.status_code
    # #     print(response.data)
    # #     self.assertEqual(statusCode, 200)
    # #
    # # def test_email_exists_register(self):
    # #
    # #     response = self.tester.post("chaddit/c/register", headers={
    # #         'user_email': 'usov.misha@gmail.com',
    # #         'api_token': admin_token
    # #         })
    # #     statusCode = response.status_code
    # #     print(response.data)
    # #     self.assertEqual(statusCode, 400)

    # def test_bad_delete_topic(self):

    #     response = self.tester.delete(f"chaddit/c/topic/${self.test_topic_id}", headers={
    #         'api_token': self.admin_token
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 404)

    # def test_bad_role_delete_topic(self):

    #     response = self.tester.delete(f"chaddit/c/topic/${self.test_topic_id}", headers={
    #         'api_token': self.admin_token
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 404)

    # def test_get_all_topics_order_by_alphabet(self):

    #     response = self.tester.get("chaddit/c/topics", headers={
    #         'orderby': "alphabet"
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_get_all_topics_order_by_popularity(self):

    #     response = self.tester.get("chaddit/c/topics", headers={
    #         'orderbydesc': "popularity"
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_get_message_for_chat(self):

    #     response = self.tester.get(f"chaddit/c/messages/${self.test_message_id}")
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_get_not_existing_thread(self):

    #     response = self.tester.get(f"chaddit/c/thread/${self.test_thread_id}")
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 404)

    # def test_get_existing_thread(self):

    #     response = self.tester.get(f"chaddit/c/thread/${self.test_thread_id}")
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_delete_non_existing_thread(self):

    #     response = self.tester.get(f"chaddit/c/thread/${self.test_thread_id}", headers={
    #         'role_id': RoleId.ADMINISTRATOR,
    #         'api_token': self.admin_token
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 404)

    # def test_delete_bad_role_id_thread(self):

    #     response = self.tester.get(f"chaddit/c/thread/${self.test_thread_id}", headers={
    #         'role_id': -1,
    #         'api_token': self.admin_token
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 404)

    # def test_non_existing_thread(self):

    #     response = self.tester.get(f"chaddit/c/thread/${self.test_thread_id}")
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 404)

    # def test_existing_thread(self):

    #     response = self.tester.get(f"chaddit/c/thread/${self.test_thread_id}")
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_bad_update_thread(self):

    #     response = self.tester.get(f"chaddit/c/thread/${self.test_thread_id}", headers={
    #         'role_id': 5,
    #         'api_token': self.admin_token
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 404)

    # def test_bad_role_update_thread(self):

    #     response = self.tester.patch(f"chaddit/c/thread/${self.test_thread_id}", headers={
    #         'role_id': 5,
    #         'api_token': self.admin_token
    #     }, json={
    #         'role_id': RoleId.USER
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_update_thread(self):

    #     response = self.tester.get(f"chaddit/c/thread/${self.test_thread_id}", headers={
    #         'api_token': self.admin_token
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 200)

    # def test_on_generate_token(self):
    #     newToken = Auth().generate_token(60)
    #     self.assertTrue(str(newToken[0]))

    # def test_on_decode_bad_token(self):
    #     newToken = Auth().decode_token("60")
    #     self.assertEqual(newToken['error'], {'message': 'Invalid admin_token, please try again with a new admin_token.'})

    # def test_on_decode_expired_token(self):
    #     newToken = Auth().decode_token("60")
    #     self.assertNotEqual(newToken['error'], {'message': 'Token expired, please login again.'})

    # def test_on_decode_good_token(self):
    #     newToken = Auth().decode_token(self.admin_token)
    #     self.assertEqual(newToken['data'], {'user_id': self.test_user_id})

    # # def test_on_get_created_message(self):
    # #     app.app_context().push()
    # #
    # #
    # #     response = self.tester.post('chaddit/c/message', headers={
    # #         'user_id': "4",
    # #         'chat_id': '68',
    # #         'api_token': admin_token
    # #     }, json={
    # #         'body':{
    # #             'chat_id': "40",
    # #             'author_id': "40"
    # #         }
    # #     })
    # #     app.app_context().push()
    # #     data = json.loads(response.data)
    # #     print(data)
    # #     chat = MessageModel.get_by_id(data["message_id"])
    # #     self.assertEqual(chat.chat_id, data["chat_id"])

    # def test_on_get_created_chat(self):

    #     response = self.tester.post('chaddit/c/chat', headers={
    #         'api_token': self.admin_token
    #     }, json={
    #         'topic_id': self.test_topic_id
    #     })
    #     app.app_context().push()
    #     data = json.loads(response.data)
    #     if response.status_code != 200:
    #         print(response.data)
    #     chat = ChatModel.get_by_id(data["chat_id"])
    #     self.assertEqual(chat.chat_id, data["chat_id"])

    # def test_on_get_created_post(self):

    #     response = self.tester.post('chaddit/c/post', headers={
    #         'api_token': self.admin_token,
    #         'thread_id': self.test_thread_id,
    #         'root_post_id': self.test_root_post_id,
    #         'post_id': self.test_post_id
    #     }, json={
    #         'body': 'jfefiejweij'
    #     })
    #     app.app_context().push()
    #     data = json.loads(response.data)
    #     if response.status_code != 200:
    #         print(response.data)
    #     chat = PostModel.get_by_id(data["post_id"])
    #     self.assertEqual(chat.thread_id, data["thread_id"])

    # def test_on_get_created_thread_without_title(self):

    #     response = self.tester.post('chaddit/c/thread', headers={
    #         'api_token': self.admin_token,
    #         'user_id': self.test_user_id,
    #         'topic_id': self.test_topic_id
    #     }, json={})
    #     responseCode = response.status_code
    #     self.assertEqual(responseCode, 400)

    # def test_on_get_created_thread_without_root_post(self):

    #     response = self.tester.post('chaddit/c/thread', headers={
    #         'api_token': self.admin_token,
    #         'topic_id': self.test_topic_id
    #     }, json={
    #         'thread_title': "fweufuewuhew",
    #         'posts': [
    #             {
    #                 'name': "jifjweio"
    #             }
    #         ]
    #     })
    #     responseCode = response.status_code
    #     self.assertEqual(responseCode, 400)

    # def test_on_get_created_thread(self):

    #     response = self.tester.post('chaddit/c/thread', headers={
    #         'api_token': self.admin_token,
    #         'topic_id': self.test_topic_id
    #     }, json={
    #         'thread_title': 'fweufuewuhew',
    #         'posts': [
    #             {
    #                 'body': "jwodjw"
    #             }
    #         ]
    #     })
    #     app.app_context().push()
    #     data = json.loads(response.data)
    #     if response.status_code != 200:
    #         print(response.data)
    #     chat = ThreadModel.get_by_id(data["thread_id"])
    #     self.assertEqual(chat.author_id, data["author_id"])

    # def test_on_get_created_topic_without_title(self):

    #     response = self.tester.post('chaddit/c/topic', headers={
    #         'api_token': self.admin_token,
    #         'user_id': self.test_user_id,
    #     }, json={})
    #     app.app_context().push()
    #     responseCode = response.status_code
    #     self.assertEqual(responseCode, 400)

    # def test_on_get_created_topic_without_tags(self):

    #     response = self.tester.post('chaddit/c/topic', headers={
    #         'api_token': self.admin_token,
    #         'user_id': self.test_user_id,
    #     }, json={
    #         'topic_title': 'jioefweiijfewji'
    #     })
    #     app.app_context().push()
    #     responseCode = response.status_code
    #     self.assertEqual(responseCode, 400)

    # # def test_on_get_created_topic(self):
    # #
    # #     response = self.tester.post('chaddit/c/topic', headers={
    # #         'api_token': admin_token,
    # #         'user_id': '40',
    # #     }, json={
    # #         'topic_title':'jioefweiijfewji',
    # #         'tags':[{'tag':'efjef'}, {'tag':'dddw'}]
    # #     })
    # #     app.app_context().push()
    # #     data = json.loads(response.data)
    # #     chat = TopicModel.get_by_id(data["topic_id"])
    # #     self.assertEqual(chat.author_id, data["author_id"])

    # def test_on_update_topic_bad_role(self):

    #     response = self.tester.patch(f'chaddit/c/topic/${self.test_topic_id}', headers={
    #         'api_token': self.admin_token
    #     })
    #     app.app_context().push()
    #     data = json.loads(response.data)
    #     if response.status_code != 200:
    #         print(response.data)
    #     topic = TopicModel.get_by_id(data["topic_id"])
    #     self.assertEqual(topic.author_id, data["author_id"])

    # def test_on_get_existing_role(self):
    #     app.app_context().push()
    #     role = RoleModel.get(RoleId.USER)
    #     self.assertEqual(RoleId.USER, role.role_id)

    # def test_create_message_without_body(self):

    #     response = self.tester.post('chaddit/c/message', headers={
    #         'api_token': self.admin_token
    #     }, json={
    #         'body': {}
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 400)

    # # def test_get_created_message(self):
    # #
    # #     response = self.tester.post('chaddit/c/message', headers={
    # #         'api_token': admin_token,
    # #         'chat_id': '68',
    # #         'author_id': '40'
    # #     }, json={
    # #         'body':{
    # #
    # #         }
    # #     })
    # #     data = json.loads(response.data)
    # #     print(response.data)
    # #     message = MessageModel.get_by_id(data["message_id"])
    # #     self.assertEqual(message.author_id, data["author_id"])
    # def test_on_bad_update_user(self):

    #     response = self.tester.patch('chaddit/c/user/-1', headers={
    #         'api_token': self.admin_token,
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 404)

    # def test_on_bad_update_user_password(self):

    #     response = self.tester.patch('chaddit/c/user/-1', headers={
    #         'api_token': self.admin_token,
    #     }, json={
    #         'user_pass': 'dwu'
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 404)

    # def test_on_bad_role_update_user(self):

    #     response = self.tester.patch(f'chaddit/c/user/${self.test_user_id}', headers={
    #         'api_token': self.user_token,
    #     }, json={
    #         'user_pass': 'dwu'
    #     })
    #     statusCode = response.status_code
    #     self.assertEqual(statusCode, 403)


if __name__ == "__main__":
    unittest.main()
