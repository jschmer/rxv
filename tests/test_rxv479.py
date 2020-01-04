import testtools
import rxv
import requests_mock
import time
import logging
import requests
import re
from unittest.mock import Mock

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

    @requests_mock.mock(real_http=True)
    def disabled_test_server_paths_live(self, m):
        rec = rxv.RXV(REAL_IP)
        rec.server_paths()

    @requests_mock.mock()
    def test_server_paths_mock(self, m):
        class MenuState:
            current = (1, 'SERVER')
            cursor = (2, 'Fancy Server')
            current_line = 1

            # key = (layer, name)
            # value = XML response
            responses = {
                (1, 'SERVER'): sample_content('rx-v479/get_SERVER_list_info_1_SERVER.xml'),
                (2, 'Fancy Server'): sample_content('rx-v479/get_SERVER_list_info_2_1_FancyServer.xml'),
                (2, 'Other Server'): sample_content('rx-v479/get_SERVER_list_info_2_2_OtherServer.xml'),
                (3, 'Music'): sample_content('rx-v479/get_SERVER_list_info_2_1_1_Music.xml'),
                (3, 'Radio'): {
                    1: sample_content('rx-v479/get_SERVER_list_info_2_1_2_Radio_Page0.xml'),
                    9: sample_content('rx-v479/get_SERVER_list_info_2_1_2_Radio_Page1.xml'),
                    17: sample_content('rx-v479/get_SERVER_list_info_2_1_2_Radio_Page2.xml'),
                },
                (4, 'Some Performer'): sample_content('rx-v479/get_SERVER_list_info_2_1_1_1_SomePerformer.xml'),
            }

            # SERVER
            # - Fancy Server (Container)
            #   - Music
            #     - Some Performer
            #       - Song Title 1 (Item)
            #       - Song Title 2
            #   - Radio
            #     - Stream 1 (Item)
            #     - Stream 2
            #     - Stream 3
            #     - Stream ...
            #     - Stream 20
            # - Other Server
            #   - Nothing to see here (Unplayable Item)

            items = {
                (1, 'SERVER'): {
                    1: (2, 'Fancy Server'),
                    2: (2, 'Other Server')
                },
                (2, 'Fancy Server'): {
                    1: (3, 'Music'),
                    2: (3, 'Radio')
                },
                (2, 'Other Server'): {
                    1: (3, 'Nothing to see here')
                },
                (3, 'Music'): {
                    1: (4, 'Some Performer')
                },
                (3, 'Radio'): {
                    1: (4, 'Stream 1'),
                    2: (4, 'Stream 2'),
                    3: (4, 'Stream 3'),
                    4: (4, 'Stream 4'),
                    5: (4, 'Stream 5'),
                    6: (4, 'Stream 6'),
                    7: (4, 'Stream 7'),
                    8: (4, 'Stream 8'),
                    9: (4, 'Stream 9'),
                    10: (4, 'Stream 10'),
                    11: (4, 'Stream 11'),
                    12: (4, 'Stream 12'),
                    13: (4, 'Stream 13'),
                    14: (4, 'Stream 14'),
                    15: (4, 'Stream 15'),
                    16: (4, 'Stream 16'),
                    17: (4, 'Stream 17'),
                    18: (4, 'Stream 18'),
                    19: (4, 'Stream 19'),
                    20: (4, 'Stream 20'),
                },
                (4, 'Some Performer'): {
                    1: (4, 'Song Title 1'),
                    2: (4, 'Song Title 2')
                }
            }

            @staticmethod
            def go_to_home():
                MenuState.current = (1, 'SERVER')
                MenuState.selected = (2, 'Fancy Server')

            @staticmethod
            def jump_to(lineno):
                assert lineno <= len(MenuState.items[MenuState.current].keys())
                MenuState.cursor = MenuState.items[MenuState.current][lineno]
                MenuState.current_line = lineno

            @staticmethod
            def select():
                MenuState.current = MenuState.cursor
                MenuState.jump_to(1)

            @staticmethod
            def resp():
                # replace <Current_Line>1</Current_Line> with the actual current line
                response = MenuState.responses[MenuState.current]
                if isinstance(response, dict):
                    response = response[MenuState.current_line]
                response = re.sub(
                    r"<Current_Line>\d+</Current_Line>",
                    "<Current_Line>{}</Current_Line>".format(MenuState.current_line),
                    response
                )
                return response

        line_matcher = re.compile('<List_Control><Jump_Line>(\\d+)</Jump_Line></List_Control>')
        def menu_list_matcher(request):
            request_text = request.text or ''
            line_match = line_matcher.search(request_text)

            if '<List_Info>GetParam</List_Info>' in request_text:
                resp = requests.Response()
                resp.status_code = 200
                resp._content = MenuState.resp()
                return resp
            elif '<Cursor>Return to Home</Cursor>' in request_text:
                MenuState.go_to_home()

                resp = requests.Response()
                resp.status_code = 200
                resp._content = sample_content('rx-v479/set_cursor_home.xml')
                return resp
            elif '<Cursor>Sel</Cursor>' in request_text:
                MenuState.select()

                resp = requests.Response()
                resp.status_code = 200
                resp._content = sample_content('rx-v479/cursor_select.xml')
                return resp
            elif line_match:
                lineno = int(line_match.group(1))
                MenuState.jump_to(lineno)

                resp = requests.Response()
                resp.status_code = 200
                resp._content = sample_content('rx-v479/cursor_jump_to_line.xml')
                return resp
            return None

        m.get(DESC_XML_URI, text=sample_content('rx-v479/desc.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel>GetParam</Input_Sel>'), text=sample_content('rx-v479/get_current_input_SERVER.xml'))
        m.post(CTRL_URI, additional_matcher=lambda r: request_text_matcher(r, '<Input_Sel_Item>GetParam</Input_Sel_Item>'), text=sample_content('rx-v479/get_inputs.xml'))
        m.add_matcher(menu_list_matcher)

        rec = rxv.RXV(USED_IP)
        expected = eval("[(1, 'Fancy Server', [(1, 'Music', [(1, 'Some Performer', [(1, 'Song Title 1'), (2, 'Song Title 2')])]), (2, 'Radio', [(1, 'Stream 1'), (2, 'Stream 2'), (3, 'Stream 3'), (4, 'Stream 4'), (5, 'Stream 5'), (6, 'Stream 6'), (7, 'Stream 7'), (8, 'Stream 8'), (9, 'Stream 9'), (10, 'Stream 10'), (11, 'Stream 11'), (12, 'Stream 12'), (13, 'Stream 13'), (14, 'Stream 14'), (15, 'Stream 15'), (16, 'Stream 16'), (17, 'Stream 17'), (18, 'Stream 18'), (19, 'Stream 19'), (20, 'Stream 20')])]), (2, 'Other Server', [])]")
        actual = rec.server_paths()
        assert expected == actual

    @requests_mock.mock()
    def test_server_select(self, m):
        m.get(DESC_XML_URI, text=sample_content('rx-v479/desc.xml'))

        rec = rxv.RXV(REAL_IP)
        rec.server_select([1, 4, 18, 1])


