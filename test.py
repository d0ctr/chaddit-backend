import json
import unittest
from types import SimpleNamespace
from datetime import datetime

from dotenv import load_dotenv

from src.app import create_app
from src.config import app_config
from src.models import ChatModel, PostModel, RoleModel, ThreadModel, TopicModel, MessageModel, TopicTagModel, UserModel, db
from tests.schemas import ChatSchema, PostSchema, RoleSchema, ThreadSchema, TopicSchema, TopicTagSchema, UserSchema
from src.shared.authetification import Auth
from src.shared.constants import RoleId
from src.views.user import email_exists
from tests.utils.defaults import def_roles, add_admin, add_chat, add_messages, add_thread, add_topic, add_post, add_user

load_dotenv(override=False)
app = create_app('development')

def login(client, user_email, user_pass):
    response = client.post(
        '/api/chaddit/c/login',
        json={
            'user_email': user_email,
            'user_pass': user_pass
        })
    return json.loads(response.data).get('api_token')


class FlaskTest(unittest.TestCase):

    def setUp(self):
        with app.app_context():
            db.drop_all()
            db.create_all()
            def_roles()
            add_admin()
            add_user()
            add_topic()
            add_thread()
            add_post()
            add_chat()
            add_messages()
        self.maxDiff = None
        self.test_topic_id = 1
        self.test_thread_id = 1
        self.test_admin_id = 1
        self.test_user_id = 2
        self.test_chat_id = 1
        self.test_post_id = 1
        self.test_root_post_id = 1
        self.test_tag_id = 1
        self.test_message_id = 1
        self.tester = app.test_client(self)
        self.admin_token = login(self.tester, 'admin@chaddit.tk', 'admin')
        self.user_token = login(self.tester, 'user@chaddit.tk', 'user')

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
                'user_email': 'new_user@chaddit.tk',
                'user_pass': 'new_user',
                'user_name': 'new_user'
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
            '/api/chaddit/c/topic',
            headers={'api-token': str(self.admin_token)},
            json={
                'topic_title': "test topic title",
                'tags': [
                    {'tag': "test_tag"}
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
        self.assertEqual(statusCode, 201)

    def test_types_update_topic(self):
        response = self.tester.patch(
            '/api/chaddit/c/topic',
            headers={
                'topic_id': self.test_topic_id,
                'api_token': self.admin_token
            },
            json={
                'topic_title': "topic title after patch"
            },
            follow_redirects=True
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
            f'/api/chaddit/c/thread',
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
        self.assertEqual(type(response_json.get('posts')), list)
        self.assertEqual(type(response_json.get('author')), dict)
        self.assertEqual(type(response_json.get('posts_count')), int)
        self.assertEqual(type(response_json.get('views')), int)
        statusCode = response.status_code
        self.assertEqual(statusCode, 201)

    def test_types_update_thread(self):
        response = self.tester.patch(
            '/api/chaddit/c/thread',
            headers={
                'thread_id': self.test_thread_id,
                'api-token': self.admin_token
            },
            json={
                'views': 100
            },
            follow_redirects=True
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
        self.assertEqual(type(response_json.get('posts')), list)
        self.assertEqual(type(response_json.get('author')), dict)
        self.assertEqual(type(response_json.get('posts_count')), int)
        self.assertEqual(type(response_json.get('views')), int)
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_types_create_post(self):
        response = self.tester.post(
            '/api/chaddit/c/post',
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
        self.assertEqual(type(response_json.get('responses')), list)
        statusCode = response.status_code
        self.assertEqual(statusCode, 201)

    def test_types_create_message(self):
        response = self.tester.post(
            '/api/chaddit/c/message',
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
            f'/api/chaddit/c/chat',
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
        self.assertEqual(type(response_json.get('participants')), list)
        self.assertEqual(type(response_json.get('topic_id')), int)
        statusCode = response.status_code
        self.assertEqual(statusCode, 201)

    def test_post_topic_successful(self):
        response = self.tester.post(
            '/api/chaddit/c/topic',
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
        response = self.tester.get(
            '/api/chaddit/c/threads',
            headers={'topic_id': self.test_topic_id}
        )
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_chats(self):
        response = self.tester.get(
            '/api/chaddit/c/chats',
            headers={'api_token': self.admin_token})
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_search_request(self):
        response = self.tester.get("/api/chaddit/c/search/topic?query='Test'")
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_on_email_not_exists(self):
        with app.app_context():
            exists = email_exists("not_existing@chaddit.tk")
            self.assertEqual(exists, False)

    def test_on_email_exists(self):
        with app.app_context():
            exists = email_exists("admin@chaddit.tk")
            self.assertEqual(exists, True)

    def compare_db_and_endpoint_chats(self):
        with app.app_context():
            ser_db_chats = ChatSchema().dump(ChatModel.get_by_user(self.test_admin_id))
            response = self.tester.get(
                '/api/chaddit/c/chats',
                headers={'api_token': self.admin_token})
            ser_api_chats = json.loads(response.data)
            self.assertEqual(ser_db_chats, ser_api_chats)

    def test_get_non_exists_db_chat_by_id(self):
        with app.app_context():
            db_chat = ChatModel.get_by_id(-1)
        self.assertEqual(None, db_chat)

    def test_get_chat(self):
        response = self.tester.get(f"/api/chaddit/c/chat/{self.test_chat_id}", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_non_existing_chat(self):
        response = self.tester.get(f"/api/chaddit/c/chat/2", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    # posts
    def test_get_posts_from_thread(self):
        response = self.tester.get("/api/chaddit/c/posts", headers={
            'thread_id': self.test_thread_id
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_post(self):
        response = self.tester.get(f"/api/chaddit/c/post/{self.test_post_id}")
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_non_existing_post(self):
        response = self.tester.get(f"/api/chaddit/c/post/-1")
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_get_thread(self):
        response = self.tester.get('/api/chaddit/c/threads', headers={
            'topic_id': self.test_topic_id
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)


    def test_get_user(self):
        response = self.tester.get(f"/api/chaddit/c/user/{self.test_admin_id}", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_all_users(self):
        response = self.tester.get("/api/chaddit/c/users", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_all_users_bad_role(self):
        self.user_token = login(self.tester, 'user@chaddit.tk', 'user')
        response = self.tester.get("/api/chaddit/c/users", headers={
            'api_token': self.user_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 403)

    def test_get_not_existing_user(self):
        response = self.tester.get("/api/chaddit/c/user/-1", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_email_exists_register(self):
        response = self.tester.post("/api/chaddit/c/register", json={
            'user_email': 'admin@chaddit.tk',
            'user_pass': 'admin',
            'user_name':'admin'
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 400)

    def test_bad_delete_topic(self):
        response = self.tester.delete("/api/chaddit/c/topic/-1", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_bad_role_delete_topic(self):
        topic_to_delete = json.loads(self.tester.post('/api/chaddit/c/topic',
            headers={'api_token': self.admin_token},
            json={'topic_title':'Topic_to_delete'}).data).get('topic_id')

        self.user_token = login(self.tester, 'user@chaddit.tk', 'user')
        response = self.tester.delete(f"/api/chaddit/c/topic/{self.test_topic_id}", headers={
            'api_token': self.user_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 403)

    def test_get_all_topics_order_by_alphabet(self):
        response = self.tester.get("/api/chaddit/c/topics", headers={
            'orderby': "alphabet"
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_all_topics_order_by_desc_popularity(self):
        response = self.tester.get("/api/chaddit/c/topics", headers={
            'orderbydesc': "popularity"
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_messages_for_chat(self):
        response = self.tester.get(f"/api/chaddit/c/messages/{self.test_chat_id}", headers={
            'api_token' : self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_get_not_existing_thread(self):
        response = self.tester.get(f"/api/chaddit/c/thread/-1")
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_get_existing_thread(self):
        response = self.tester.get(f"/api/chaddit/c/thread/{self.test_thread_id}")
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_delete_non_existing_thread(self):
        response = self.tester.delete(f"/api/chaddit/c/thread/-1", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 404)

    def test_bad_role_delete_thread(self):
        response = self.tester.delete(f"/api/chaddit/c/thread/{self.test_thread_id}", headers={
            'api_token': self.user_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 403)

    def test_bad_role_update_thread(self):
        response = self.tester.patch(f"/api/chaddit/c/thread/{self.test_thread_id}", headers={
            'api_token': self.user_token
            }, json = {
                'thread_title' : 'New_thread_title'
            })
        statusCode = response.status_code
        self.assertEqual(statusCode, 403)

    def test_update_thread(self):
        response = self.tester.get(f"/api/chaddit/c/thread/{self.test_thread_id}", headers={
            'api_token': self.admin_token
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 200)

    def test_bad_data_update_thread(self):
        thread_before = json.loads(self.tester.get(f"/api/chaddit/c/thread/{self.test_thread_id}").data)
        response = self.tester.patch(f"/api/chaddit/c/thread/{self.test_thread_id}", headers={
            'api_token': self.admin_token
        }, json={
            'non_existing_field': 'not_a_value'
        })
        thread_after = json.loads(response.data)
        statusCode = response.status_code
        del thread_after['updated_at']
        del thread_before['updated_at']
        self.assertEqual(statusCode, 200)
        self.assertEqual(thread_before, thread_after)

    def test_on_generate_token(self):
        newToken = Auth().generate_token(60)
        self.assertTrue(str(newToken[0]))

    def test_on_decode_bad_token(self):
        newToken = Auth().decode_token("60")
        self.assertEqual(newToken['error'],{'message': 'Invalid token, please try again with a new token.'})

    # def test_on_decode_expired_token(self):
    #     newToken = Auth().decode_token("60")
    #     self.assertNotEqual(newToken['error'], {'message': 'Token expired, please login again.'})

    def test_on_decode_good_token(self):
        newToken = Auth().decode_token(self.admin_token)
        self.assertEqual(newToken['data'], {'user_id': self.test_admin_id})

    def test_on_get_created_chat(self):
        response = self.tester.post('/api/chaddit/c/chat', headers={
            'api_token': self.admin_token
        }, json={
            'topic_id': self.test_topic_id
        })
        data = json.loads(response.data)
        with app.app_context():
            chat = ChatModel.get_by_id(data["chat_id"])
            self.assertEqual(chat.chat_id, data["chat_id"])

    def test_on_get_created_post(self):
        response = self.tester.post('/api/chaddit/c/post', headers={
            'api_token': self.admin_token,
            'thread_id': self.test_thread_id,
            'root_post_id': self.test_root_post_id,
            'post_id': self.test_post_id
        }, json={
            'body': 'test_post'
        })
        with app.app_context():
            data = json.loads(response.data)
            chat = PostModel.get_by_id(data["post_id"])
            self.assertEqual(chat.thread_id, data["thread_id"])

    def test_on_get_created_thread_without_title(self):
        response = self.tester.post('/api/chaddit/c/thread', headers={
            'api_token': self.admin_token,
            'user_id': self.test_admin_id,
            'topic_id': self.test_topic_id
        }, json={})
        responseCode = response.status_code
        self.assertEqual(responseCode, 400)

    def test_on_get_created_thread_without_root_post(self):
        response = self.tester.post('/api/chaddit/c/thread', headers={
            'api_token': self.admin_token,
            'topic_id': self.test_topic_id
        }, json={
            'thread_title': "bad_test_thread",
            'posts': []
        })
        responseCode = response.status_code
        self.assertEqual(responseCode, 400)

    def test_on_get_created_thread(self):
        response = self.tester.post('/api/chaddit/c/thread', headers={
            'api_token': self.admin_token,
            'topic_id': self.test_topic_id
        }, json={
            'thread_title': 'test_thread',
            'posts': [
                {
                    'body': "test_post"
                }
            ]
        })
        with app.app_context():
            data = json.loads(response.data)
            chat = ThreadModel.get_by_id(data["thread_id"])
            self.assertEqual(chat.author_id, data["author_id"])

    def test_on_get_created_topic_without_title(self):
        response = self.tester.post('/api/chaddit/c/topic', headers={
            'api_token': self.admin_token,
            'user_id': self.test_admin_id,
        }, json={})
        with app.app_context():
            responseCode = response.status_code
            self.assertEqual(responseCode, 400)

    def test_on_get_created_topic_without_tags(self):
        response = self.tester.post('/api/chaddit/c/topic', headers={
            'api_token': self.admin_token,
            'user_id': self.test_admin_id,
        }, json={
            'topic_title': 'topic_withoud_tags'
        })
        with app.app_context():
            responseCode = response.status_code
            self.assertEqual(responseCode, 400)

    def test_on_update_topic_bad_role(self):
        response = self.tester.patch(f'/api/chaddit/c/topic/{self.test_topic_id}', headers={
            'api_token': self.admin_token
        }, json={
            'topic_title': 'no_access_to_this_topic'
        })
        data = json.loads(response.data)
        with app.app_context():
            topic = TopicModel.get_by_id(data["topic_id"])
            self.assertEqual(topic.author_id, data["author_id"])

    def test_on_get_existing_role(self):
        with app.app_context():
            role = RoleModel.get(RoleId.USER)
            self.assertEqual(RoleId.USER, role.role_id)

    def test_create_message_without_body(self):
        response = self.tester.post('/api/chaddit/c/message', headers={
            'api_token': self.admin_token
        }, json={
            'body': {}
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 400)

    def test_on_bad_update_user_password(self):
        response = self.tester.patch(f'/api/chaddit/c/user/{self.test_user_id}', headers={
            'api_token': self.user_token,
        }, json={
            'old_user_pass': 'wrong_old_pass',
            'user_pass': 'new_pass'
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 400)

    def test_on_bad_role_update_user(self):
        self.user_token = login(self.tester, 'user@chaddit.tk', 'user')
        response = self.tester.patch(f'/api/chaddit/c/user/{self.test_admin_id}', headers={
            'api_token': self.user_token,
        }, json={
            'user_pass': 'wrong_role'
        })
        statusCode = response.status_code
        self.assertEqual(statusCode, 403)


if __name__ == "__main__":
    unittest.main()
