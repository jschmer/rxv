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
        m.get(DESC_XML_URI, text=sample_content('rx-v479/desc.xml'))
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

        m.get(DESC_XML_URI, text=sample_content('rx-v479/desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))

        rec = rxv.RXV(FAKE_IP)
        actual = rec.server_paths()
        expected = eval("[(1, 'Fancy Server', [(1, 'Music', [(1, 'Some Performer', [(1, 'Song Title 1'), (2, 'Song Title 2')])]), (2, 'Radio', [(1, 'Stream 1'), (2, 'Stream 2'), (3, 'Stream 3'), (4, 'Stream 4'), (5, 'Stream 5'), (6, 'Stream 6'), (7, 'Stream 7'), (8, 'Stream 8'), (9, 'Stream 9'), (10, 'Stream 10'), (11, 'Stream 11'), (12, 'Stream 12'), (13, 'Stream 13'), (14, 'Stream 14'), (15, 'Stream 15'), (16, 'Stream 16'), (17, 'Stream 17'), (18, 'Stream 18'), (19, 'Stream 19'), (20, 'Stream 20')]), (3, 'Some Fancy Song 1'), (4, 'Some Fancy Song 2'), (5, 'Some Fancy Song 3'), (6, 'Some Fancy Song 4'), (7, 'Some Fancy Song 5'), (8, 'Some Fancy Song 6'), (9, 'Some Fancy Song 7')]), (2, 'Other Server', [(1, 'Nothing to see here')])]")
        self.assertEqual(expected, actual)

    @requests_mock.mock()
    def test_server_select_numbers(self, m):
        menu_list_handler = MenuListHandler()
        m.add_matcher(lambda r: menu_list_handler.match(r))

        m.get(DESC_XML_URI, text=sample_content('rx-v479/desc.xml'))
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

        m.get(DESC_XML_URI, text=sample_content('rx-v479/desc.xml'))
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

        m.get(DESC_XML_URI, text=sample_content('rx-v479/desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>SERVER</Input_Sel>'), text=sample_content('rx-v479/set_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))

        rec = rxv.RXV(FAKE_IP)
        self.assertRaises(NotImplementedError, rec.server_select, {1: "Hello"})


    @requests_mock.mock()
    def test_server_select_path_not_available(self, m):
        menu_list_handler = MenuListHandler()
        m.add_matcher(lambda r: menu_list_handler.match(r))

        m.get(DESC_XML_URI, text=sample_content('rx-v479/desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>SERVER</Input_Sel>'), text=sample_content('rx-v479/set_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: match_request(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))

        rec = rxv.RXV(FAKE_IP)
        self.assertRaises(FileNotFoundError, rec.server_select, "Fancy Server>Radio>Stream 66")
