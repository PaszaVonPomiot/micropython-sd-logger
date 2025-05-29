from machine import Pin


class SDGPIO:
    SCK: int = 10
    MOSI: int = 11
    MISO: int = 12
    CS: int = 13


class SDPin:
    SCK: Pin = Pin(SDGPIO.SCK)
    MOSI: Pin = Pin(SDGPIO.MOSI)
    MISO: Pin = Pin(SDGPIO.MISO)
    CS: Pin = Pin(SDGPIO.CS, mode=Pin.OUT)
