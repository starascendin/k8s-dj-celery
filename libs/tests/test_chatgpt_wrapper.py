import unittest
from unittest.mock import patch, Mock
from revChatGPT.V1 import Chatbot
from libs.chatgpt_wrapper import RevChatGPTWrapper

class TestRevChatGPTWrapper(unittest.TestCase):
    def setUp(self):
        self.email = "test@example.com"
        self.password = "password"
        self.prompt = "Hello, how are you?"
        self.chatbot_config = {"email": self.email, "password": self.password}
        self.chatbot = Chatbot(config=self.chatbot_config)
        self.chatbot_response = [{"message": "Hi there!"}]
        self.chatbot_mock = Mock()
        self.chatbot_mock.ask.return_value = self.chatbot_response
        self.rev_chat_gpt_wrapper = RevChatGPTWrapper(email=self.email, password=self.password)

    @patch.object(Chatbot, 'ask')
    def test_generate_response(self, mock_ask):
        mock_ask.return_value = self.chatbot_response
        result = self.rev_chat_gpt_wrapper.generate_response(self.prompt)
        self.assertEqual(result, "Hi there!")
        mock_ask.assert_called_once_with(self.prompt)
