import unittest
import time

from python.tools.serial.serial import YueSerial, SerialConfig
import serial


class TestYueSerial(unittest.TestCase):
    def test_loopback(self):
        # use pyserial's loop:// URL which echoes back data
        cfg = SerialConfig(port="loop://", baudrate=9600, timeout=0.1)
        received = []

        def cb(data: bytes):
            received.append(data)

        with YueSerial(cfg, callback=cb) as s:
            # wait a moment for thread to start
            time.sleep(0.1)
            s.write(b"hello")
            # give time for data to arrive
            time.sleep(0.1)
        # callback should have been invoked with data
        self.assertTrue(any(b"hello" in chunk for chunk in received))

    def test_queue_read(self):
        cfg = SerialConfig(port="loop://", baudrate=9600, timeout=0.1)
        with YueSerial(cfg) as s:
            time.sleep(0.1)
            s.write(b"abc")
            time.sleep(0.1)
            data = s.read(timeout=0.5)
            self.assertIn(b"abc", data)


if __name__ == "__main__":
    unittest.main()