import testtools
import time
import rxv

REAL_IP = '192.168.178.31'

class TestRXV479(testtools.TestCase):

    def test_live_action(self):
        rec = rxv.RXV(REAL_IP)
        #rec.server_select([1, 4, 18, 1])
        #time.sleep(1)
        #play_status = rec.play_status()
        #self.assertEqual("Rock Antenne", play_status.artist)

        print(rec.surround_programs())

        print(rec.surround_program)
        time.sleep(1)
        rec.surround_program = "Straight"
        time.sleep(1)
        rec.surround_program = "5ch Stereo"
        time.sleep(1)
        rec.surround_program = "Straight"
        time.sleep(1)
        rec.surround_program = "Surround Decoder"