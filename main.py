from machine import SPI
from config.storage import SDGPIO
from config.storage import SDPin
from lib.sdcard import SDCard
import uos
from core.sd_logger import LoggerCSV


def main() -> None:
    spi = SPI(1, sck=SDGPIO.SCK, mosi=SDGPIO.MOSI, miso=SDGPIO.MISO)
    sd = SDCard(spi=spi, cs=SDPin.CS)
    vfs = uos.VfsFat(sd)
    uos.mount(vfs, "/sd")
    print(uos.listdir("/sd"))
    sensor_logger = LoggerCSV(
        file_name="sensor.csv", csv_headers=["date", "value"], buffer_size=3
    )
    sensor_logger.write_record_with_buffer("record buffered")
    sensor_logger.write_record_with_buffer("record buffered")
    sensor_logger.write_record_with_buffer("record buffered and buffer written to file")
    sensor_logger.write_record("record written to file directly")


if __name__ == "__main__":
    main()
