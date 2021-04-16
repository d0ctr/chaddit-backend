import json
import unittest
from types import SimpleNamespace
from datetime import datetime

from dotenv import load_dotenv

from src.app import create_app
from src.config import app_config
from src.models import ChatModel, PostModel, RoleModel, ThreadModel, TopicModel
from src.schemas import ChatSchema, PostSchema, RoleSchema, ThreadSchema, TopicSchema, TopicTagSchema, UserSchema
from src.shared.authetification import Auth
from src.shared.constants import RoleId
from src.views.user import email_exists

load_dotenv(override=False)
app = create_app('production')


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

    def test_login(self):
        tester = app.test_client(self)
        response = tester.post(
            '/api/chaddit/c/login', 
            json={
                'user_email': 'admin@chaddit.tk',
                'user_pass': 'admin'
        })
        self.admin_token = response.data.get('api_token')
        self.assertEqual(type(self.admin_token), str)
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        tester = app.test_client(self)
        response = tester.post(
            '/api/chaddit/c/register',
            json={
                'user_email': 'user@chaddit.tk',
                'user_pass': 'user',
                'user_name': 'user'
        })
        self.user_token = response.data.get('api_token')
        self.assertEqual(response.status_code, 201)

    def test_get_topics(self):
        tester = app.test_client(self)
        response = tester.get('/chaddit/c/topics')
        topics = TopicSchema(response.data, many = True)
        for topic in topics:
            self.assertEqual(type(topic.topic_id), int)
            self.assertEqual(type(topic.topic_title), str)
            self.assertEqual(type(topic.created_at), datetime)
            self.assertEqual(type(topic.updated_at), datetime)
            self.assertEqual(type(topic.author_id), int)
            self.assertEqual(type(topic.tags[0]), TopicTagSchema)
            self.assertEqual(type(topic.image), str | None)
            self.assertEqual(type(topic.active), bool)
            self.assertEqual(type(topic.author), UserSchema)
            self.assertEqual(type(topic.threads_count), int)
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_on_update_user(self):
        tester = app.test_client(self)
        response = tester.patch(
            'chaddit/c/user/' + str(self.test_user_id),
            json={
                'user_name':'admin'
            }
        )
        self.assertEqual(response.data.user_id, int)
        self.assertEqual(response.data.user_name, str)
        self.assertEqual(response.data.user_email, str)
        self.assertEqual(response.data.avatar, str)
        self.assertEqual(response.data.role_id, int)

    def test_post_topic_successful(self):
        tester = app.test_client(self)
        response = tester.post(
            '/chaddit/c/topic',
            json={
                    'topic_title': 'Test',
                    'tags': 
                            [
                                {'tag': "test"}
                            ]
                  },
            headers={'api-token': self.admin_token}
        )
        statusCode = response.status_code
        self.assertEqual(statusCode, 201)

    def test_threads(self):
        tester = app.test_client(self)
        response = tester.get(
            '/chaddit/c/threads', 
            headers={'topic-id': self.test_topic_id}
        )
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_chats(self):
        tester = app.test_client(self)
        response = tester.get(
            '/chaddit/c/chats', 
            headers={'api_token': self.admin_token})
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    # def test_chats_models(self):
    #     tester = app.test_client(self)
    #     response = tester.get(
    #         '/chaddit/c/chats', 
    #         headers={'api_token': self.admin_token})
    #     data = json.loads(response.data, object_hook=lambda d: SimpleNamespace(**d))
    #     self.assertTrue(data, bool)

    def test_bad_request(self):
        tester = app.test_client(self)
        response = tester.get("chaddit/c/search/topic?query='Test'")
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_on_email_not_exists(self):
        app.app_context().push()
        exists = email_exists("not_existing@chaddit.tk")
        self.assertEqual(exists, False)

    def test_on_email_exists(self):
        app.app_context().push()
        exists = email_exists("admin@chaddit.tk")
        self.assertEqual(exists, True)

    def compare_db_and_endpoint_chats(self):
        app.app_context().push()
        db_chats = ChatModel.get_by_id(self.test_user_id)
        tester = app.test_client(self)
        response = tester.get(
            '/chaddit/c/chats', 
            headers={'api_token': self.admin_token})
        data = json.loads(response.data, object_hook=lambda d: SimpleNamespace(**d))
        self.assertNotEqual(db_chats, data)

    def test_get_non_exists_db_chat_by_id(self):
        app.app_context().push()
        db_chats = ChatModel.get_by_id(self.test_chat_id)
        self.assertEqual(None, db_chats.topic_id)

    def test_get_chat(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/chat/${self.test_chat_id}", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_non_existing_chat(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/chat/${self.test_chat_id}", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    # posts
    def test_get_posts_from_thread(self):
        tester = app.test_client(self)
        response = tester.get("chaddit/c/posts", headers={
            'thread_id': self.test_thread_id
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_post(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/post/${self.test_post_id}")
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_non_existing_post(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/post/${self.test_post_id}")
        statusCode = response.status_code
        self.assertEqual(statusCode, 400)

    def test_get_thread(self):
        tester = app.client.test_client()
        response = tester.get('/chaddit/c/threads',
                              headers={
                                  'post_id': self.test_post_id,
                                  'thread_id': self.test_thread_id,
                                  'user_id': self.test_user_id,
                                  'topic_id': self.test_topic_id
                              })
        statusCode = response.status_code
        if statusCode != 200:
            print(response.data)
        self.assertEqual(statusCode, 200)

    # user tests
    def test_login(self):
        tester = app.test_client(self)
        response = tester.get("chaddit/c/user", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 307)

    def test_get_user(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/user/${self.test_user_id}", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        if statusCode != 200:
            print(response.data)
        self.assertEqual(statusCode, 200)

    def test_get_all_users(self):
        tester = app.test_client(self)
        response = tester.get("chaddit/c/users", headers={
            'role_id': RoleId.ADMINISTRATOR,
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_all_users_bad_role(self):
        tester = app.test_client(self)
        response = tester.get("chaddit/c/users", headers={
            'api_token': self.user_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 400)

    def test_get_not_existing_user(self):
        tester = app.test_client(self)
        response = tester.get("chaddit/c/user/-1", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    # def test_successful_register(self):
    #     tester = app.test_client(self)
    #     response = tester.post("chaddit/c/register", headers={
    #         'user_email': 'usov@gmail.com',
    #         'api_token': admin_token
    #     })
    #     statusCode = response.status_code
    #     print(response.data)
    #     self.assertEqual(statusCode, 200)
    #
    # def test_email_exists_register(self):
    #     tester = app.test_client(self)
    #     response = tester.post("chaddit/c/register", headers={
    #         'user_email': 'usov.misha@gmail.com',
    #         'api_token': admin_token
    #         })
    #     statusCode = response.status_code
    #     print(response.data)
    #     self.assertEqual(statusCode, 400)

    def test_bad_delete_topic(self):
        tester = app.test_client(self)
        response = tester.delete(f"chaddit/c/topic/${self.test_topic_id}", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_bad_role_delete_topic(self):
        tester = app.test_client(self)
        response = tester.delete(f"chaddit/c/topic/${self.test_topic_id}", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_get_all_topics_order_by_alphabet(self):
        tester = app.test_client(self)
        response = tester.get("chaddit/c/topics", headers={
            'orderby': "alphabet"
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_all_topics_order_by_popularity(self):
        tester = app.test_client(self)
        response = tester.get("chaddit/c/topics", headers={
            'orderbydesc': "popularity"
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_message_for_chat(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/messages/${self.test_message_id}")
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_not_existing_thread(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/thread/${self.test_thread_id}")
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_get_existing_thread(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/thread/${self.test_thread_id}")
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_delete_non_existing_thread(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/thread/${self.test_thread_id}", headers={
            'role_id': RoleId.ADMINISTRATOR,
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_delete_bad_role_id_thread(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/thread/${self.test_thread_id}", headers={
            'role_id': -1,
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_non_existing_thread(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/thread/${self.test_thread_id}")
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_existing_thread(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/thread/${self.test_thread_id}")
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_bad_update_thread(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/thread/${self.test_thread_id}", headers={
            'role_id': 5,
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_bad_role_update_thread(self):
        tester = app.test_client(self)
        response = tester.patch(f"chaddit/c/thread/${self.test_thread_id}", headers={
            'role_id': 5,
            'api_token': self.admin_token
        }, json={
            'role_id': RoleId.USER
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_update_thread(self):
        tester = app.test_client(self)
        response = tester.get(f"chaddit/c/thread/${self.test_thread_id}", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_on_generate_token(self):
        newToken = Auth().generate_token(60)
        self.assertTrue(str(newToken[0]))

    def test_on_decode_bad_token(self):
        newToken = Auth().decode_token("60")
        self.assertEqual(newToken['error'], {'message': 'Invalid admin_token, please try again with a new admin_token.'})

    def test_on_decode_expired_token(self):
        newToken = Auth().decode_token("60")
        self.assertNotEqual(newToken['error'], {'message': 'Token expired, please login again.'})

    def test_on_decode_good_token(self):
        newToken = Auth().decode_token(self.admin_token)
        self.assertEqual(newToken['data'], {'user_id': self.test_user_id})

    # def test_on_get_created_message(self):
    #     app.app_context().push()
    #
    #     tester = app.test_client(self)
    #     response = tester.post('chaddit/c/message', headers={
    #         'user_id': "4",
    #         'chat_id': '68',
    #         'api_token': admin_token
    #     }, json={
    #         'body':{
    #             'chat_id': "40",
    #             'author_id': "40"
    #         }
    #     })
    #     app.app_context().push()
    #     data = json.loads(response.data)
    #     print(data)
    #     chat = MessageModel.get_by_id(data["message_id"])
    #     self.assertEqual(chat.chat_id, data["chat_id"])

    def test_on_get_created_chat(self):
        tester = app.test_client(self)
        response = tester.post('chaddit/c/chat', headers={
            'api_token': self.admin_token
        }, json={
            'topic_id': self.test_topic_id
        })
        app.app_context().push()
        data = json.loads(response.data)
        if response.status_code != 200:
            print(response.data)
        chat = ChatModel.get_by_id(data["chat_id"])
        self.assertEqual(chat.chat_id, data["chat_id"])

    def test_on_get_created_post(self):
        tester = app.test_client(self)
        response = tester.post('chaddit/c/post', headers={
            'api_token': self.admin_token,
            'thread_id': self.test_thread_id,
            'root_post_id': self.test_root_post_id,
            'post_id': self.test_post_id
        }, json={
            'body': 'jfefiejweij'
        })
        app.app_context().push()
        data = json.loads(response.data)
        if response.status_code != 200:
            print(response.data)
        chat = PostModel.get_by_id(data["post_id"])
        self.assertEqual(chat.thread_id, data["thread_id"])

    def test_on_get_created_thread_without_title(self):
        tester = app.test_client(self)
        response = tester.post('chaddit/c/thread', headers={
            'api_token': self.admin_token,
            'user_id': self.test_user_id,
            'topic_id': self.test_topic_id
        }, json={})
        responseCode = response.status_code
        self.assertEqual(responseCode, 400)

    def test_on_get_created_thread_without_root_post(self):
        tester = app.test_client(self)
        response = tester.post('chaddit/c/thread', headers={
            'api_token': self.admin_token,
            'topic_id': self.test_topic_id
        }, json={
            'thread_title': "fweufuewuhew",
            'posts': [
                {
                    'name': "jifjweio"
                }
            ]
        })
        responseCode = response.status_code
        self.assertEqual(responseCode, 400)

    def test_on_get_created_thread(self):
        tester = app.test_client(self)
        response = tester.post('chaddit/c/thread', headers={
            'api_token': self.admin_token,
            'topic_id': self.test_topic_id
        }, json={
            'thread_title': 'fweufuewuhew',
            'posts': [
                {
                    'body': "jwodjw"
                }
            ]
        })
        app.app_context().push()
        data = json.loads(response.data)
        if response.status_code != 200:
            print(response.data)
        chat = ThreadModel.get_by_id(data["thread_id"])
        self.assertEqual(chat.author_id, data["author_id"])

    def test_on_get_created_topic_without_title(self):
        tester = app.test_client(self)
        response = tester.post('chaddit/c/topic', headers={
            'api_token': self.admin_token,
            'user_id': self.test_user_id,
        }, json={})
        app.app_context().push()
        responseCode = response.status_code
        self.assertEqual(responseCode, 400)

    def test_on_get_created_topic_without_tags(self):
        tester = app.test_client(self)
        response = tester.post('chaddit/c/topic', headers={
            'api_token': self.admin_token,
            'user_id': self.test_user_id,
        }, json={
            'topic_title': 'jioefweiijfewji'
        })
        app.app_context().push()
        responseCode = response.status_code
        self.assertEqual(responseCode, 400)

    # def test_on_get_created_topic(self):
    #     tester = app.test_client(self)
    #     response = tester.post('chaddit/c/topic', headers={
    #         'api_token': admin_token,
    #         'user_id': '40',
    #     }, json={
    #         'topic_title':'jioefweiijfewji',
    #         'tags':[{'tag':'efjef'}, {'tag':'dddw'}]
    #     })
    #     app.app_context().push()
    #     data = json.loads(response.data)
    #     chat = TopicModel.get_by_id(data["topic_id"])
    #     self.assertEqual(chat.author_id, data["author_id"])

    def test_on_update_topic_bad_role(self):
        tester = app.test_client(self)
        response = tester.patch(f'chaddit/c/topic/${self.test_topic_id}', headers={
            'api_token': self.admin_token
        })
        app.app_context().push()
        data = json.loads(response.data)
        if response.status_code != 200:
            print(response.data)
        topic = TopicModel.get_by_id(data["topic_id"])
        self.assertEqual(topic.author_id, data["author_id"])

    def test_on_get_existing_role(self):
        app.app_context().push()
        role = RoleModel.get(RoleId.USER)
        self.assertEqual(RoleId.USER, role.role_id)

    def test_create_message_without_body(self):
        tester = app.test_client(self)
        response = tester.post('chaddit/c/message', headers={
            'api_token': self.admin_token
        }, json={
            'body': {}
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 400)

    # def test_get_created_message(self):
    #     tester = app.test_client(self)
    #     response = tester.post('chaddit/c/message', headers={
    #         'api_token': admin_token,
    #         'chat_id': '68',
    #         'author_id': '40'
    #     }, json={
    #         'body':{
    #
    #         }
    #     })
    #     data = json.loads(response.data)
    #     print(response.data)
    #     message = MessageModel.get_by_id(data["message_id"])
    #     self.assertEqual(message.author_id, data["author_id"])
    def test_on_bad_update_user(self):
        tester = app.test_client(self)
        response = tester.patch('chaddit/c/user/-1', headers={
            'api_token': self.admin_token,
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_on_bad_update_user_password(self):
        tester = app.test_client(self)
        response = tester.patch('chaddit/c/user/-1', headers={
            'api_token': self.admin_token,
        }, json={
            'user_pass': 'dwu'
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_on_bad_role_update_user(self):
        tester = app.test_client(self)
        response = tester.patch(f'chaddit/c/user/${self.test_user_id}', headers={
            'api_token': self.user_token,
        }, json={
            'user_pass': 'dwu'
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 403)


if __name__ == "__main__":
    unittest.main()
