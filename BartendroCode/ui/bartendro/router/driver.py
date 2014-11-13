import sys
import os
import collections
import logging
from subprocess import call
from time import sleep, localtime, time
import serial
from struct import pack, unpack
import pack7
import dispenser_select
from bartendro.error import SerialIOError
import random

DISPENSER_DEFAULT_VERSION = 2
DISPENSER_DEFAULT_VERSION_SOFTWARE_ONLY = 3

BAUD_RATE       = 9600
DEFAULT_TIMEOUT = 2 # in seconds

MAX_DISPENSERS = 15
SHOT_TICKS     = 20

RAW_PACKET_SIZE      = 10
PACKET_SIZE          =  8

PACKET_ACK_OK               = 0
PACKET_CRC_FAIL             = 1
PACKET_ACK_TIMEOUT          = 2
PACKET_ACK_INVALID          = 3
PACKET_ACK_INVALID_HEADER   = 4
PACKET_ACK_HEADER_IN_PACKET = 5
PACKET_ACK_CRC_FAIL         = 6

PACKET_PING                   = 3
PACKET_SET_MOTOR_SPEED        = 4
PACKET_TICK_DISPENSE          = 5
PACKET_TIME_DISPENSE          = 6
PACKET_LED_OFF                = 7
PACKET_LED_IDLE               = 8
PACKET_LED_DISPENSE           = 9
PACKET_LED_DRINK_DONE         = 10
PACKET_IS_DISPENSING          = 11
PACKET_LIQUID_LEVEL           = 12
PACKET_UPDATE_LIQUID_LEVEL    = 13
PACKET_ID_CONFLICT            = 14
PACKET_LED_CLEAN              = 15
PACKET_SET_CS_THRESHOLD       = 16
PACKET_SAVED_TICK_COUNT       = 17
PACKET_RESET_SAVED_TICK_COUNT = 18
PACKET_GET_LIQUID_THRESHOLDS  = 19
PACKET_SET_LIQUID_THRESHOLDS  = 20
PACKET_FLUSH_SAVED_TICK_COUNT = 21
PACKET_TICK_SPEED_DISPENSE    = 22
PACKET_PATTERN_DEFINE         = 23
PACKET_PATTERN_ADD_SEGMENT    = 24
PACKET_PATTERN_FINISH         = 25
PACKET_SET_MOTOR_DIRECTION    = 26
PACKET_GET_VERSION            = 27
PACKET_COMM_TEST              = 0xFE

DEST_BROADCAST         = 0xFF

MOTOR_DIRECTION_FORWARD       = 1
MOTOR_DIRECTION_BACKWARD      = 0

LED_PATTERN_IDLE          = 0
LED_PATTERN_DISPENSE      = 1
LED_PATTERN_DRINK_DONE    = 2
LED_PATTERN_CLEAN         = 3
LED_PATTERN_CURRENT_SENSE = 4

MOTOR_DIRECTION_FORWARD         = 1
MOTOR_DIRECTION_BACKWARD        = 0

log = logging.getLogger('bartendro')

def crc16_update(crc, a):
    crc ^= a
    for i in xrange(0, 8):
        if crc & 1:
            crc = (crc >> 1) ^ 0xA001
        else:
            crc = (crc >> 1)
    return crc

class RouterDriver(object):
    '''This object interacts with the bartendro router controller.'''

    def __init__(self, device, software_only):
        self.device = device
        self.ser = None
        self.msg = ""
        self.ret = 0
        self.software_only = software_only
        self.dispenser_select = None
        self.dispenser_version = DISPENSER_DEFAULT_VERSION
        self.startup_log = ""
        self.debug_levels = [ 200, 180, 120 ]

        # dispenser_ids are the ids the dispensers have been assigned. These are logical ids 
        # used for dispenser communication.
        self.dispenser_ids = [255 for i in xrange(MAX_DISPENSERS)]

        # dispenser_ports are the ports the dispensers have been plugged into.
        self.dispenser_ports = [255 for i in xrange(MAX_DISPENSERS)]

        if software_only:
            self.num_dispensers = MAX_DISPENSERS
        else:
            self.num_dispensers = 0 

    def get_startup_log(self):
        return self.startup_log
    
    def get_dispenser_version(self):
        return self.dispenser_version

    def reset(self):
        """Reset the hardware. Do this if there is shit going wrong. All motors will be stopped
           and reset."""
        if self.software_only: return

        self.close()
        self.open()

    def count(self):
        return self.num_dispensers

    def set_timeout(self, timeout):
        self.ser.timeout = timeout

    def open(self):
        '''Open the serial connection to the router'''

        if self.software_only: return

        self._clear_startup_log()

        try:
            log.info("Opening %s" % self.device)
            self.ser = serial.Serial(self.device, 
                                     BAUD_RATE, 
                                     bytesize=serial.EIGHTBITS, 
                                     parity=serial.PARITY_NONE, 
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout=.01)
        except serial.serialutil.SerialException, e:
            raise SerialIOError(e)

        log.info("Done.\n")

        import status_led
        self.status = status_led.StatusLED(self.software_only)
        self.status.set_color(0, 0, 1)

        self.dispenser_select = dispenser_select.DispenserSelect(MAX_DISPENSERS, self.software_only)
        self.dispenser_select.open()
        self.dispenser_select.reset()

        # This primes the communication line. 
        self.ser.write(chr(170) + chr(170) + chr(170))
        sleep(.001)

        log.info("Discovering dispensers")
        self.num_dispensers = 0
        for port in xrange(MAX_DISPENSERS):
            self._log_startup("port %d:" % port)
            self.dispenser_select.select(port)
            sleep(.01)
            while True:
                self.ser.flushInput()
                self.ser.write("???") 
                data = self.ser.read(3)
                ll = ""
                for ch in data:
                    ll += "%02X " % ord(ch)
                if len(data) == 3: 
                    if data[0] != data[1] or data[0] != data[2]:
                        self._log_startup("  %s -- inconsistent" % ll)
                        continue
                    id = ord(data[0])
                    self.dispenser_ids[self.num_dispensers] = id
                    self.dispenser_ports[self.num_dispensers] = port
                    self.num_dispensers += 1
                    self._log_startup("  %s -- Found dispenser with pump id %02X, index %d" % (ll, id, self.num_dispensers))
                    break
                elif len(data) > 1:
                    self._log_startup("  %s -- Did not receive 3 characters back. Trying again." % ll)
                    sleep(.5)
                else:
                    break

        self._select(0)
        self.set_timeout(DEFAULT_TIMEOUT)
        self.ser.write(chr(255));

        duplicate_ids = [x for x, y in collections.Counter(self.dispenser_ids).items() if y > 1]
        if len(duplicate_ids):
            for dup in duplicate_ids:
                if dup == 255: continue
                self._log_startup("ERROR: Dispenser id conflict!\n")
                sent = False
                for i, d in enumerate(self.dispenser_ids):
                    if d == dup: 
                        if not sent: 
                            self._send_packet8(i, PACKET_ID_CONFLICT, 0)
                            sent = True
                        self._log_startup("  dispenser %d has id %d\n" % (i, d))
                        self.dispenser_ids[i] = 255
                        self.num_dispensers -= 1

        self.dispenser_version = self.get_dispenser_version(0)
        if self.dispenser_version < 0:
            self.dispenser_version = DISPENSER_DEFAULT_VERSION 
        else:
            self.status.swap_blue_green()
        log.info("Detected dispensers version %d. (Only checked first dispenser)" % self.dispenser_version)

        self.led_idle()

    def close(self):
        if self.software_only: return
        self.ser.close()
        self.ser = None
        self.status = None
        self.dispenser_select = None

    def log(self, msg):
        return
        if self.software_only: return
        try:
            t = localtime()
            self.cl.write("%d-%d-%d %d:%02d %s" % (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, msg))
            self.cl.flush()
        except IOError:
            pass

    def make_shot(self):
        if self.software_only: return True
        self._send_packet32(0, PACKET_TICK_DISPENSE, 90)
        return True

    def ping(self, dispenser):
        if self.software_only: return True
        return self._send_packet32(dispenser, PACKET_PING, 0)

    def start(self, dispenser):
        if self.software_only: return True
        return self._send_packet8(dispenser, PACKET_SET_MOTOR_SPEED, 255, True)

    def set_motor_direction(self, dispenser, direction):
        if self.software_only: return True
        return self._send_packet8(dispenser, PACKET_SET_MOTOR_DIRECTION, direction)

    def stop(self, dispenser):
        if self.software_only: return True
        return self._send_packet8(dispenser, PACKET_SET_MOTOR_SPEED, 0)

    def dispense_time(self, dispenser, duration):
        if self.software_only: return True
        return self._send_packet32(dispenser, PACKET_TIME_DISPENSE, duration)

    def dispense_ticks(self, dispenser, ticks, speed=255):
        if self.software_only: return True
        return self._send_packet16(dispenser, PACKET_TICK_SPEED_DISPENSE, ticks, speed)

    def led_off(self):
        if self.software_only: return True
        self._sync(0)
        self._send_packet8(DEST_BROADCAST, PACKET_LED_OFF, 0)
        return True

    def led_idle(self):
        if self.software_only: return True
        self._sync(0)
        self._send_packet8(DEST_BROADCAST, PACKET_LED_IDLE, 0)
        sleep(.01)
        self._sync(1)
        return True

    def led_dispense(self):
        if self.software_only: return True
        self._sync(0)
        self._send_packet8(DEST_BROADCAST, PACKET_LED_DISPENSE, 0)
        sleep(.01)
        self._sync(1)
        return True

    def led_complete(self):
        if self.software_only: return True
        self._sync(0)
        self._send_packet8(DEST_BROADCAST, PACKET_LED_DRINK_DONE, 0)
        sleep(.01)
        self._sync(1)
        return True

    def led_clean(self):
        if self.software_only: return True
        self._sync(0)
        self._send_packet8(DEST_BROADCAST, PACKET_LED_CLEAN, 0)
        sleep(.01)
        self._sync(1)
        return True

    def led_error(self):
        if self.software_only: return True
        self._sync(0)
        self._send_packet8(DEST_BROADCAST, PACKET_LED_CLEAN, 0)
        sleep(.01)
        self._sync(1)
        return True

    def comm_test(self):
        self._sync(0)
        return self._send_packet8(0, PACKET_COMM_TEST, 0)

    def is_dispensing(self, dispenser):
        """
        Returns a tuple of (dispensing, is_over_current) 
        """

        if self.software_only: return (False, False)

        # Sometimes the motors can interfere with communications.
        # In such cases, assume the motor is still running and 
        # then assume the caller will again to see if it is still running
        self.set_timeout(.1)
        ret = self._send_packet8(dispenser, PACKET_IS_DISPENSING, 0)
        self.set_timeout(DEFAULT_TIMEOUT)
        if ret: 
            ack, value0, value1 = self._receive_packet8_2()
            if ack == PACKET_ACK_OK:
                return (value0, value1)
            if ack == PACKET_ACK_TIMEOUT:
                return (-1, -1)
        return (True, False)

    def update_liquid_levels(self):
        if self.software_only: return True
        return self._send_packet8(DEST_BROADCAST, PACKET_UPDATE_LIQUID_LEVEL, 0)

    def get_liquid_level(self, dispenser):
        if self.software_only: return 100
        if self._send_packet8(dispenser, PACKET_LIQUID_LEVEL, 0):
            ack, value, dummy = self._receive_packet16()
            if ack == PACKET_ACK_OK:
                # Returning a random value as below is really useful for testing. :)
                #self.debug_levels[dispenser] = max(self.debug_levels[dispenser] - 20, 50)
                #return self.debug_levels[dispenser]
                #return random.randint(50, 200)
                return value
        return -1

    def get_liquid_level_thresholds(self, dispenser):
        if self.software_only: return True
        if self._send_packet8(dispenser, PACKET_GET_LIQUID_THRESHOLDS, 0):
            ack, low, out = self._receive_packet16()
            if ack == PACKET_ACK_OK:
                return (low, out)
        return (-1, -1)
                
    def set_liquid_level_thresholds(self, dispenser, low, out):
        if self.software_only: return True
        return self._send_packet16(dispenser, PACKET_SET_LIQUID_THRESHOLDS, low, out)

    def set_motor_direction(self, dispenser, dir):
        if self.software_only: return True
        return self._send_packet8(dispenser, PACKET_SET_MOTOR_DIRECTION, dir)

    def get_dispenser_version(self, dispenser):
        if self.software_only: return DISPENSER_DEFAULT_VERSION_SOFTWARE_ONLY
        if self._send_packet8(dispenser, PACKET_GET_VERSION, 0):
            # set a short timeout, in case its a v2 dispenser
            self.set_timeout(.1)
            ack, ver, dummy = self._receive_packet16(True)
            self.set_timeout(DEFAULT_TIMEOUT)
            if ack == PACKET_ACK_OK:
                return ver
        return -1

    def set_status_color(self, red, green, blue):
        if self.software_only: return
        if not self.status: return
        self.status.set_color(red, green, blue)

    def get_saved_tick_count(self, dispenser):
        if self.software_only: return True
        if self._send_packet8(dispenser, PACKET_SAVED_TICK_COUNT, 0):
            ack, ticks, dummy = self._receive_packet16()
            if ack == PACKET_ACK_OK:
                return ticks
        return -1

    def flush_saved_tick_count(self):
        if self.software_only: return True
        return self._send_packet8(DEST_BROADCAST, PACKET_FLUSH_SAVED_TICK_COUNT, 0)

    def pattern_define(self, dispenser, pattern):
        if self.software_only: return True
        return self._send_packet8(dispenser, PACKET_PATTERN_DEFINE, pattern)

    def pattern_add_segment(self, dispenser, red, green, blue, steps):
        if self.software_only: return True
        return self._send_packet8(dispenser, PACKET_PATTERN_ADD_SEGMENT, red, green, blue, steps)

    def pattern_finish(self, dispenser):
        if self.software_only: return True
        return self._send_packet8(dispenser, PACKET_PATTERN_FINISH, 0)

    # -----------------------------------------------
    # Past this point we only have private functions. 
    # -----------------------------------------------

    def _sync(self, state):
        """Turn on/off the sync signal from the router. This signal is used to syncronize the LEDs"""

        if self.software_only: return
        self.dispenser_select.sync(state)

    def _select(self, dispenser):
        """Private function to select a dispenser."""

        if self.software_only: return True

        # If for broadcast, then ignore this select
        if dispenser == 255: return

        port = self.dispenser_ports[dispenser]
        self.dispenser_select.select(port)


    def _send_packet(self, dest, packet):
        if self.software_only: return True

        self._select(dest);
        self.ser.flushInput()
        self.ser.flushOutput()

        crc = 0
        for ch in packet:
            crc = crc16_update(crc, ord(ch))

        encoded = pack7.pack_7bit(packet + pack("<H", crc))
        if len(encoded) != RAW_PACKET_SIZE:
            log.error("send_packet: Encoded packet size is wrong: %d vs %s" % (len(encoded), RAW_PACKET_SIZE))
            return False

        try:
            t0 = time()
            written = self.ser.write(chr(0xFF) + chr(0xFF) + encoded)
            if written != RAW_PACKET_SIZE + 2:
                log.error("Send timeout")
                return False

            if dest == DEST_BROADCAST:
                return True

            ch = self.ser.read(1)
            t1 = time()
            log.debug("packet time: %f" % (t1 - t0))
            if len(ch) < 1:
                log.error("send packet: read timeout")
                return False
        except SerialException, err:
            log.error("SerialException: %s" % err);
            return False

        ack = ord(ch)
        if ack == PACKET_ACK_OK: 
            return True
        if ack == PACKET_CRC_FAIL: 
            log.error("send packet: packet ack crc fail")
            return False
        if ack == PACKET_ACK_TIMEOUT: 
            log.error("send_packet: ack timeout")
            return False
        if ack == PACKET_ACK_INVALID: 
            log.error("send_packet: dispenser received invalid packet")
            return False
        if ack == PACKET_ACK_INVALID_HEADER: 
            log.error("send_packet: dispenser received invalid header")
            return False
        if ack == PACKET_ACK_HEADER_IN_PACKET:
            log.error("send_packet: header in packet error")
            return False

        # if we get an invalid ack code, it might be ok. 
        log.error("send_packet: Invalid ACK code %d" % ord(ch))
        return False

    def _send_packet8(self, dest, type, val0, val1=0, val2=0, val3=0):
        if dest != DEST_BROADCAST: 
            dispenser_id = self.dispenser_ids[dest]
            if dispenser_id == 255: return False
        else:
            dispenser_id = dest

        return self._send_packet(dest, pack("BBBBBB", dispenser_id, type, val0, val1, val2, val3))

    def _send_packet16(self, dest, type, val0, val1):
        if dest != DEST_BROADCAST: 
            dispenser_id = self.dispenser_ids[dest]
            if dispenser_id == 255: return False
        else:
            dispenser_id = dest
        return self._send_packet(dest, pack("<BBHH", dispenser_id, type, val0, val1))

    def _send_packet32(self, dest, type, val):
        if dest != DEST_BROADCAST: 
            dispenser_id = self.dispenser_ids[dest]
            if dispenser_id == 255: return False
        else:
            dispenser_id = dest
        return self._send_packet(dest, pack("<BBI", dispenser_id, type, val))

    def _receive_packet(self, quiet = False):
        if self.software_only: return True

        header = 0
        while True:
            ch = self.ser.read(1)
            if len(ch) < 1:
                if not quiet:
                    log.error("receive packet: response timeout")
                return (PACKET_ACK_TIMEOUT, "")

            if (ord(ch) == 0xFF):
                header += 1
            else:
                header = 0

            if header == 2:
                break

        ack = PACKET_ACK_OK
        raw_packet = self.ser.read(RAW_PACKET_SIZE)
        if len(raw_packet) != RAW_PACKET_SIZE:
            if not quiet:
                log.error("receive packet: timeout")
            ack = PACKET_ACK_TIMEOUT

        if ack == PACKET_ACK_OK:
            packet = pack7.unpack_7bit(raw_packet)
            if len(packet) != PACKET_SIZE:
                ack = PACKET_ACK_INVALID
                if not quiet:
                    log.error("receive_packet: Unpacked length incorrect")

            if ack == PACKET_ACK_OK:
                received_crc = unpack("<H", packet[6:8])[0]
                packet = packet[0:6]

                crc = 0
                for ch in packet:
                    crc = crc16_update(crc, ord(ch))

                if received_crc != crc:
                    if not quiet:
                        log.error("receive_packet: CRC fail")
                    ack = PACKET_ACK_CRC_FAIL

        # Send the response back to the dispenser
        if self.ser.write(chr(ack)) != 1:
            if not quiet:
                log.error("receive_packet: Send ack timeout!")
            ack = PACKET_ACK_TIMEOUT

        if ack == PACKET_ACK_OK:
            return (ack, packet)
        else:
            return (ack, "")

    def _receive_packet8(self, quiet = False):
        ack, packet = self._receive_packet(quiet)
        if ack == PACKET_ACK_OK:
            data = unpack("BBBBBB", packet)
            return (ack, data[2])
        else:
            return (ack, 0)

    def _receive_packet8_2(self, quiet = False):
        ack, packet = self._receive_packet(quiet)
        if ack == PACKET_ACK_OK:
            data = unpack("BBBBBB", packet)
            return (ack, data[2], data[3])
        else:
            return (ack, 0, 0)

    def _receive_packet16(self, quiet = False):
        ack, packet = self._receive_packet(quiet)
        if ack == PACKET_ACK_OK:
            data = unpack("<BBHH", packet)
            return (ack, data[2], data[3])
        else:
            return (ack, 0, 0)

    def _clear_startup_log(self):
        self.startup_log = ""

    def _log_startup(self, txt):
        log.info(txt)
        self.startup_log += "%s\n" % txt
