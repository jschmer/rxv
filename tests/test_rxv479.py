import testtools
import rxv
import requests_mock
import time
from tests.menu_list_fakes import MenuListHandler

FAKE_IP = '10.0.0.0'
DESC_XML_URI = 'http://%s/YamahaRemoteControl/desc.xml' % FAKE_IP
CTRL_URI = 'http://%s/YamahaRemoteControl/ctrl' % FAKE_IP


def sample_content(name):
    with open('tests/samples/%s' % name, encoding='utf-8') as f:
        return f.read()


def match_request(request, text_match):
    return text_match in (request.text or '')


class TestRXV479(testtools.TestCase):

    @requests_mock.mock()
    def test_basic_object(self, m):
        m.get(DESC_XML_URI, text=sample_content('rx-v479-desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Power>On</Power>'), text=sample_content('rx-v479/set_power_on.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Power>GetParam</Power>'), text=sample_content('rx-v479/get_power.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>SERVER</Input_Sel>'), text=sample_content('rx-v479/set_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<List_Info>GetParam</List_Info>'), text=sample_content('rx-v479/get_SERVER_list_info.xml'))

        rec = rxv.RXV(FAKE_IP)
        rec.on = True
        while not rec.on is True:
            time.sleep(0.01)
            rec.on = True
        self.assertEqual(True, rec.on)

        rec.input = "SERVER"
        while not rec.input == "SERVER":
            time.sleep(0.01)
        self.assertEqual("SERVER", rec.input)

        while not rec.menu_status().ready:
            time.sleep(0.01)
        self.assertEqual(True, rec.menu_status().ready)

    @requests_mock.mock()
    def test_server_paths(self, m):
        menu_list_handler = MenuListHandler()
        m.add_matcher(lambda r: menu_list_handler.match(r))

        m.get(DESC_XML_URI, text=sample_content('rx-v479-desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))

        rec = rxv.RXV(FAKE_IP)
        actual = rec.server_paths()
        expected = [
            ("Fancy Server>Music>Some Performer>Song Title 1", "1>1>1>1"),
            ("Fancy Server>Music>Some Performer>Song Title 2", "1>1>1>2"),
            ("Fancy Server>Radio>Stream 1", "1>2>1"),
            ("Fancy Server>Radio>Stream 2", "1>2>2"),
            ("Fancy Server>Radio>Stream 3", "1>2>3"),
            ("Fancy Server>Radio>Stream 4", "1>2>4"),
            ("Fancy Server>Radio>Stream 5", "1>2>5"),
            ("Fancy Server>Radio>Stream 6", "1>2>6"),
            ("Fancy Server>Radio>Stream 7", "1>2>7"),
            ("Fancy Server>Radio>Stream 8", "1>2>8"),
            ("Fancy Server>Radio>Stream 9", "1>2>9"),
            ("Fancy Server>Radio>Stream 10", "1>2>10"),
            ("Fancy Server>Radio>Stream 11", "1>2>11"),
            ("Fancy Server>Radio>Stream 12", "1>2>12"),
            ("Fancy Server>Radio>Stream 13", "1>2>13"),
            ("Fancy Server>Radio>Stream 14", "1>2>14"),
            ("Fancy Server>Radio>Stream 15", "1>2>15"),
            ("Fancy Server>Radio>Stream 16", "1>2>16"),
            ("Fancy Server>Radio>Stream 17", "1>2>17"),
            ("Fancy Server>Radio>Stream 18", "1>2>18"),
            ("Fancy Server>Radio>Stream 19", "1>2>19"),
            ("Fancy Server>Radio>Stream 20", "1>2>20"),
            ("Fancy Server>Some Fancy Song 1", "1>3"),
            ("Fancy Server>Some Fancy Song 2", "1>4"),
            ("Fancy Server>Some Fancy Song 3", "1>5"),
            ("Fancy Server>Some Fancy Song 4", "1>6"),
            ("Fancy Server>Some Fancy Song 5", "1>7"),
            ("Fancy Server>Some Fancy Song 6", "1>8"),
            ("Fancy Server>Some Fancy Song 7", "1>9"),
            ("Other Server>Nothing to see here", "2>1"),
        ]
        self.assertEqual(expected, actual)

    @requests_mock.mock()
    def test_server_select_numbers(self, m):
        menu_list_handler = MenuListHandler()
        m.add_matcher(lambda r: menu_list_handler.match(r))

        m.get(DESC_XML_URI, text=sample_content('rx-v479-desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>SERVER</Input_Sel>'), text=sample_content('rx-v479/set_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))

        rec = rxv.RXV(FAKE_IP)
        self.assertIsNone(menu_list_handler.selected)
        rec.server_select([1, 2, 17])
        self.assertEqual((4, "Stream 17"), menu_list_handler.selected)

    @requests_mock.mock()
    def test_server_select_names(self, m):
        menu_list_handler = MenuListHandler()
        m.add_matcher(lambda r: menu_list_handler.match(r))

        m.get(DESC_XML_URI, text=sample_content('rx-v479-desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>SERVER</Input_Sel>'), text=sample_content('rx-v479/set_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))

        rec = rxv.RXV(FAKE_IP)
        self.assertIsNone(menu_list_handler.selected)
        rec.server_select("Fancy Server>Radio>Stream 17")
        self.assertEqual((4, "Stream 17"), menu_list_handler.selected)

    @requests_mock.mock()
    def test_server_select_incompatible_input(self, m):
        menu_list_handler = MenuListHandler()
        m.add_matcher(lambda r: menu_list_handler.match(r))

        m.get(DESC_XML_URI, text=sample_content('rx-v479-desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>SERVER</Input_Sel>'), text=sample_content('rx-v479/set_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))

        rec = rxv.RXV(FAKE_IP)
        self.assertRaises(NotImplementedError, rec.server_select, {1: "Hello"})


    @requests_mock.mock()
    def test_server_select_path_not_available(self, m):
        menu_list_handler = MenuListHandler()
        m.add_matcher(lambda r: menu_list_handler.match(r))

        m.get(DESC_XML_URI, text=sample_content('rx-v479-desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>SERVER</Input_Sel>'), text=sample_content('rx-v479/set_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))

        rec = rxv.RXV(FAKE_IP)
        self.assertRaises(FileNotFoundError, rec.server_select, "Fancy Server>Radio>Stream 66")
