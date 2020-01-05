import re
import requests

def sample_content(name):
    with open('tests/samples/%s' % name, encoding='utf-8') as f:
        return f.read()

class MenuListHandler:
    """
    Class to handle menu actions to provide mocked responses to requests. The menu
    has to be tracked because the API of the Yamaha receivers is stateful (jump to item,
    select it, ...). Returns individual responses based on the current state, which
    mimics a real menu list.

    Expects request_mock's matching convention and has to be installed as a custom matcher object.

    The responses are currently hardcoded, see __init__.

    Example:
        menu_list_handler = MenuListHandler()
        requests_mock.add_matcher(lambda r: menu_list_handler.match(r))
    """

    def __init__(self):
        """
        Initialize this object with following menu list state:
          SERVER
          - Fancy Server (Container)
            - Music
              - Some Performer
                - Song Title 1 (Item)
                - Song Title 2
            - Radio
              - Stream 1 (Item)
              - Stream 2
              - Stream 3
              - Stream ...
              - Stream 20
            - Some Fancy Song 1
            - Some Fancy Song 2
            - Some Fancy Song 3
            - Some Fancy Song 4
            - Some Fancy Song 5
            - Some Fancy Song 6
            - Some Fancy Song 7
          - Other Server
            - Nothing to see here (Unplayable Item)
        """
        self.current = (1, 'SERVER')
        self.cursor = (2, 'Fancy Server')
        self.selected = None
        self.current_line = 1

        self.line_matcher = re.compile('<List_Control><Jump_Line>(\\d+)</Jump_Line></List_Control>')

        # key = (layer, name)
        # value = XML response
        self.responses = {
            (1, 'SERVER'): sample_content('rx-v479/get_SERVER_list_info_1_SERVER.xml'),
            (2, 'Fancy Server'): {
                range(1, 9): sample_content('rx-v479/get_SERVER_list_info_2_1_FancyServer_Page0.xml'),
                range(9, 10): sample_content('rx-v479/get_SERVER_list_info_2_1_FancyServer_Page1.xml'),
            },
            (2, 'Other Server'): sample_content('rx-v479/get_SERVER_list_info_2_2_OtherServer.xml'),
            (3, 'Music'): sample_content('rx-v479/get_SERVER_list_info_2_1_1_Music.xml'),
            (3, 'Radio'): {
                range(1, 9): sample_content('rx-v479/get_SERVER_list_info_2_1_2_Radio_Page0.xml'),
                range(9, 17): sample_content('rx-v479/get_SERVER_list_info_2_1_2_Radio_Page1.xml'),
                range(17, 25): sample_content('rx-v479/get_SERVER_list_info_2_1_2_Radio_Page2.xml'),
            },
            (4, 'Some Performer'): sample_content('rx-v479/get_SERVER_list_info_2_1_1_1_SomePerformer.xml'),
        }

        self.items = {
            (1, 'SERVER'): {
                1: (2, 'Fancy Server'),
                2: (2, 'Other Server')
            },
            (2, 'Fancy Server'): {
                1: (3, 'Music'),
                2: (3, 'Radio'),
                3: (3, 'Some Fancy Song 1'),
                4: (3, 'Some Fancy Song 2'),
                5: (3, 'Some Fancy Song 3'),
                6: (3, 'Some Fancy Song 4'),
                7: (3, 'Some Fancy Song 5'),
                8: (3, 'Some Fancy Song 6'),
                9: (3, 'Some Fancy Song 7'),
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

    def go_to_home(self):
        self.current = (1, 'SERVER')
        self.cursor = (2, 'Fancy Server')
        self.jump_to(1)

    def jump_to(self, lineno):
        assert lineno <= len(self.items[self.current].keys())
        self.cursor = self.items[self.current][lineno]
        self.selected = None
        self.current_line = lineno

    def select(self):
        if self.cursor in self.items:
            # jump down to child item
            self.current = self.cursor
            self.jump_to(1)
        else:
            # otherwise we already are a child item, in this case
            # the menu doesn't change
            self.selected = self.cursor

    def resp(self):
        """
        Returns the response corresponding to current state.
        :return: Response as XML string
        """

        response = self.responses[self.current]
        if isinstance(response, dict):
            def find_current_line_in_range():
                nonlocal response
                for r in response.keys():
                    if self.current_line in r:
                        return r
                return None

            resp_key = find_current_line_in_range()
            response = response[resp_key]
        # replace <Current_Line>1</Current_Line> with the actual current line
        response = re.sub(
            r"<Current_Line>\d+</Current_Line>",
            "<Current_Line>{}</Current_Line>".format(self.current_line),
            response
        )
        return response

    def match(self, request):
        """
        Match and handle requests for menu actions.

        :param request: Request object
        :return: A response if the request was a menu action, None otherwise
        """
        request_text = request.text or ''
        line_match = self.line_matcher.search(request_text)

        def gen_response(content):
            resp = requests.Response()
            resp.status_code = 200
            resp._content = content
            return resp

        if '<List_Info>GetParam</List_Info>' in request_text:
            return gen_response(self.resp())
        elif '<Cursor>Return to Home</Cursor>' in request_text:
            self.go_to_home()
            return gen_response(sample_content('rx-v479/set_cursor_home.xml'))
        elif '<Cursor>Sel</Cursor>' in request_text:
            self.select()
            return gen_response(sample_content('rx-v479/cursor_select.xml'))
        elif line_match:
            self.jump_to(int(line_match.group(1)))
            return gen_response(sample_content('rx-v479/cursor_jump_to_line.xml'))
        return None
