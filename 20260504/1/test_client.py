import unittest
import threading
from unittest.mock import Mock, patch

from mood.client.mud_client import MUDClient, Field_attributes


class TestMudClient(unittest.TestCase):
    def setUp(self):
        self.client = object.__new__(MUDClient)
        self.client.field = Field_attributes()
        self.client.print_lock = threading.Lock()
        self.client._send = Mock()

    def test_addmon_normal_order(self):
        self.client.field_addmon(
            'sheep hello "hello" hp 35 coords 1 2'
        )

        self.client._send.assert_called_once_with({
            "cmd": "addmon",
            "name": "sheep",
            "hp": 35,
            "x": 1,
            "y": 2,
            "hello": "hello",
        })

    def test_addmon_different_order(self):
        self.client.field_addmon(
            'sheep coords 3 4 hp 20 hello "hi there"'
        )

        self.client._send.assert_called_once_with({
            "cmd": "addmon",
            "name": "sheep",
            "hp": 20,
            "x": 3,
            "y": 4,
            "hello": "hi there",
        })

    def test_attack_default_weapon(self):
        self.client.player_attack("sheep")

        self.client._send.assert_called_once_with({
            "cmd": "attack",
            "name": "sheep",
            "weapon": "sword",
        })

    def test_attack_with_weapon(self):
        self.client.player_attack("sheep with axe")

        self.client._send.assert_called_once_with({
            "cmd": "attack",
            "name": "sheep",
            "weapon": "axe",
        })

    def test_addmon_invalid_hp(self):
        with self.assertRaises(ValueError):
            self.client.field_addmon(
                'sheep hello "hello" hp bad coords 1 2'
            )

        self.client._send.assert_not_called()

    def test_attack_unknown_weapon(self):
        with patch("builtins.print") as mock_print:
            self.client.player_attack("sheep with gun")

        self.client._send.assert_not_called()
        mock_print.assert_called_once_with("Unknown weapon")


if __name__ == "__main__":
    unittest.main()
