import testtools
import rxv
import requests_mock
import time
from tests.menu_list_fakes import MenuListHandler

REAL_IP = '192.168.178.31'
FAKE_IP = '10.0.0.0'
USED_IP = FAKE_IP
DESC_XML_URI = 'http://%s/YamahaRemoteControl/desc.xml' % USED_IP
CTRL_URI = 'http://%s/YamahaRemoteControl/ctrl' % USED_IP


def sample_content(name):
    with open('tests/samples/%s' % name, encoding='utf-8') as f:
        return f.read()


def request_text_matcher(request, text_match):
    return text_match in (request.text or '')


class TestRXV479(testtools.TestCase):

    def test_live_action(self):
        rec = rxv.RXV(REAL_IP)
        rec.server_select([1, 4, 6, 2]) # die neue welle Stream 2
        #rec.server_select([1, 4, 18, 1])  # Rock Antenne Stream
        play_status = rec.play_status()
        pass

    @requests_mock.mock()
    def test_basic_object(self, m):
        m.get(DESC_XML_URI, text=sample_content('rx-v479/desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Power>On</Power>'), text=sample_content('rx-v479/set_power_on.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Power>GetParam</Power>'), text=sample_content('rx-v479/get_power.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel>SERVER</Input_Sel>'), text=sample_content('rx-v479/set_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<List_Info>GetParam</List_Info>'), text=sample_content('rx-v479/get_SERVER_list_info.xml'))

        rec = rxv.RXV(USED_IP)
        rec.on = True
        while not rec.on is True:
            time.sleep(0.01)
            rec.on = True
        assert rec.on is True

        rec.input = "SERVER"
        while not rec.input == "SERVER":
            time.sleep(0.01)
        assert rec.input == "SERVER"

        while not rec.menu_status().ready:
            time.sleep(0.01)
        assert rec.menu_status().ready

    @requests_mock.mock()
    def test_server_paths(self, m):
        menu_list_handler = MenuListHandler()
        m.add_matcher(lambda r: menu_list_handler.match(r))

        m.get(DESC_XML_URI, text=sample_content('rx-v479/desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))

        rec = rxv.RXV(USED_IP)
        expected = eval("[(1, 'Fancy Server', [(1, 'Music', [(1, 'Some Performer', [(1, 'Song Title 1'), (2, 'Song Title 2')])]), (2, 'Radio', [(1, 'Stream 1'), (2, 'Stream 2'), (3, 'Stream 3'), (4, 'Stream 4'), (5, 'Stream 5'), (6, 'Stream 6'), (7, 'Stream 7'), (8, 'Stream 8'), (9, 'Stream 9'), (10, 'Stream 10'), (11, 'Stream 11'), (12, 'Stream 12'), (13, 'Stream 13'), (14, 'Stream 14'), (15, 'Stream 15'), (16, 'Stream 16'), (17, 'Stream 17'), (18, 'Stream 18'), (19, 'Stream 19'), (20, 'Stream 20')])]), (2, 'Other Server', [])]")
        actual = rec.server_paths()
        assert expected == actual

    @requests_mock.mock()
    def test_server_select_numbers(self, m):
        menu_list_handler = MenuListHandler()
        m.add_matcher(lambda r: menu_list_handler.match(r))

        m.get(DESC_XML_URI, text=sample_content('rx-v479/desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel>SERVER</Input_Sel>'), text=sample_content('rx-v479/set_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))

        rec = rxv.RXV(USED_IP)
        assert menu_list_handler.selected is None
        rec.server_select([1, 2, 17])
        assert menu_list_handler.selected == (4, "Stream 17")

    @requests_mock.mock()
    def test_server_select_names(self, m):
        menu_list_handler = MenuListHandler()
        m.add_matcher(lambda r: menu_list_handler.match(r))

        m.get(DESC_XML_URI, text=sample_content('rx-v479/desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel>SERVER</Input_Sel>'), text=sample_content('rx-v479/set_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))

        rec = rxv.RXV(USED_IP)
        assert menu_list_handler.selected is None
        rec.server_select("Fancy Server>Radio>Stream 17")
        assert menu_list_handler.selected == (4, "Stream 17")

