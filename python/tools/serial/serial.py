import os
import sys
import threading
import queue
import time
import logging

try:
    import serial
    import serial.serialutil
except ImportError:
    # attempt to install pyserial if missing
    os.system(f"{sys.executable} -m pip install pyserial")
    import serial
    import serial.serialutil

from typing import NamedTuple, Optional, Callable


class SerialConfig(NamedTuple):
    """Configuration for a serial port."""

    port: str
    baudrate: int = 9600
    bytesize: int = serial.EIGHTBITS
    parity: str = serial.PARITY_NONE
    stopbits: int = serial.STOPBITS_ONE
    timeout: Optional[float] = 1.0
    write_timeout: Optional[float] = None
    descript: Optional[str] = None


class SerialData(NamedTuple):
    """Information returned about a port state or event.

    ``config`` is the configuration used to open the port. ``init`` is set to
    ``True`` when the port has been successfully initialised, ``error`` is set
    to ``True`` if an error occurred during operation.
    """

    config: SerialConfig
    init: bool
    error: bool


class YueSerial:
    """Simple multi-threaded serial reader/writer.

    ``YueSerial`` manages a :class:`serial.Serial` instance and spawns a
    background thread that constantly reads any available data.  Data may be
    retrieved by registering a callback or by pulling it from the internal
    queue with :meth:`read`.
    """

    def __init__(
        self,
        config: SerialConfig,
        callback: Optional[Callable[[bytes], None]] = None,
    ):
        self._config = config
        self._callback = callback
        self._serial: Optional[serial.Serial] = None
        self._thread: Optional[threading.Thread] = None
        self._running = threading.Event()
        self._queue: "queue.Queue[bytes]" = queue.Queue()
        self._logger = logging.getLogger(__name__)

    def open(self) -> None:
        """Open the serial port.  The reader thread is created but not started.
        """
        if self._serial and self._serial.is_open:
            return
        self._serial = serial.Serial(
            port=self._config.port,
            baudrate=self._config.baudrate,
            bytesize=self._config.bytesize,
            parity=self._config.parity,
            stopbits=self._config.stopbits,
            timeout=self._config.timeout,
            write_timeout=self._config.write_timeout,
        )
        self._running.clear()
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._logger.debug("Opened serial port %s", self._config.port)

    def start(self) -> None:
        """Start the background reader thread.  ``open`` is called implicitly if
        the port is not yet open.
        """
        if not self._serial or not self._serial.is_open:
            self.open()
        if self._thread and not self._thread.is_alive():
            self._running.set()
            self._thread.start()
            self._logger.debug("Started reader thread for %s", self._config.port)

    def _reader_loop(self) -> None:
        assert self._serial is not None
        while self._running.is_set():
            try:
                available = self._serial.in_waiting or 1
                data = self._serial.read(available)
                if data:
                    self._queue.put(data)
                    if self._callback:
                        try:
                            self._callback(data)
                        except Exception as exc:  # keep reader alive
                            self._logger.exception("Callback raised: %s", exc)
            except (serial.SerialException, OSError) as exc:
                self._logger.error("Serial read error: %s", exc)
                break
        self._logger.debug("Reader thread exiting for %s", self._config.port)

    def write(self, data: bytes) -> int:
        """Write bytes to the serial port."""
        if not self._serial or not self._serial.is_open:
            raise serial.SerialException("Port not open")
        return self._serial.write(data)

    def read(self, timeout: Optional[float] = None) -> Optional[bytes]:
        """Read data from the internal queue.

        If ``timeout`` is provided the call blocks for at most that many seconds.
        If ``timeout`` is ``None`` the call is non-blocking and will raise
        :class:`queue.Empty` on no data.
        """
        return self._queue.get(timeout=timeout)

    def close(self) -> None:
        """Stop the reader thread and close the port."""
        self._running.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None
        self._logger.debug("Closed serial port %s", self._config.port)

    def __enter__(self) -> "YueSerial":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
