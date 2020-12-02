import testtools
import time
import logging
import rxv

REAL_IP = '192.168.178.31'

class TestRXV479Live(testtools.TestCase):
    def __init__(self, *args, **kwargs):
        FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
        logging.basicConfig(format=FORMAT, level=logging.INFO)

        super(TestRXV479Live, self).__init__(*args, **kwargs)

    def test_live_action(self):
        rec = rxv.RXV(REAL_IP)
        rec.on = True
        #print(rec.server_paths())

        #rec.server_select([1, 4, 18, 1])
        #time.sleep(1)
        play_status = rec.play_status()
        print(play_status)
        #self.assertEqual("Rock Antenne", play_status.artist)

        print(rec.surround_programs())
        print("***")
        print(rec.surround_program)
        if rec.surround_program == "Direct":
            rec.surround_program = "Straight"
        else:
            rec.surround_program = "Direct"

        #assert True == False
        # time.sleep(1)
        # rec.surround_program = "Straight"
        # time.sleep(1)
        # rec.surround_program = "5ch Stereo"
        # time.sleep(1)
        # rec.surround_program = "Straight"
        # time.sleep(1)
        # rec.surround_program = "Surround Decoder"