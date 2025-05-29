import gc
import os


class SDNotMountedError(Exception): ...


class InvalideRecordError(ValueError): ...


class LoggerCSV:
    """
    CSV logger for data storage on an SD card.

    Provide file name and optionally SD Card mount point, CSV header line and buffer size.
    The logger will write to the specified file on the mounted SD card (`/sd_mountpoint/file_name`).
    Use `write_record_with_buffer()` method to use buffering (writes to SD card once the buffer is full).
    Use `write_record()` method to write immediately without buffering.
    """

    def __init__(
        self,
        file_name: str,
        sd_mountpoint: str = "sd",  # default mount point for sd card, change if different
        buffer_size: int = 60,
        csv_headers: list[str] | None = None,
    ) -> None:
        self.file_name = file_name
        self.sd_mountpoint = sd_mountpoint
        self.file_path = f"{self.sd_mountpoint}/{self.file_name}"
        self.csv_headers = csv_headers  # first line of csv file, optional
        self.delimiter = ";"
        self.buffer_size = buffer_size
        self.buffer: list[str] = []
        self._post_init()

    def __del__(self) -> None:
        """Flush buffer in case of object deletion."""
        if self.buffer:
            self._write_buffer_to_file()

    def _post_init(self) -> None:
        """Verify SD mount and create CSV headers if needed."""
        self._verify_sd_mounted()
        self._create_csv_with_headers()

    def _create_csv_with_headers(self) -> None:
        """Create file with CSV headers if it doesn't exist"""
        if self._file_exists() or self.csv_headers is None:
            return
        with open(self.file_path, mode="w", encoding="utf-8") as file:
            file.write(self.delimiter.join(self.csv_headers) + "\n")

    def _verify_sd_mounted(self) -> None:
        """Verify that SD card is mounted as folder in filesystem"""
        try:
            os.stat(self.sd_mountpoint)
        except OSError:
            raise SDNotMountedError(f"Mount point '{self.sd_mountpoint}' not found")

    def _file_exists(self) -> bool:
        """Check if CSV file exists"""
        try:
            os.stat(self.file_path)
        except OSError:
            return False
        return True

    def _buffer_full(self) -> bool:
        """Check if buffer is full"""
        return len(self.buffer) >= self.buffer_size

    def _add_record_to_buffer(self, record: str) -> None:
        """
        Use buffer to reduce flash wear.
        Record should not containe newline characters.
        """
        self.buffer.append(record)

    def _serialize_buffer(self) -> str:
        """
        Convert buffer list into string with newline characters between each record.
        Clear the buffer after serialization.
        """
        buffer_serialized = "\n".join(self.buffer) + "\n"
        self.buffer.clear()
        return buffer_serialized

    def _write_buffer_to_file(self) -> None:
        """Serialize buffer and write it to a file"""
        serialized_buffer = self._serialize_buffer()
        with open(self.file_path, mode="a", encoding="utf-8") as file:
            file.write(serialized_buffer)
        gc.collect()

    def _validate_record(self, record: str) -> None:
        """Validate if record does not contain newline characters"""
        if "\n" in record:
            raise InvalideRecordError("Record cannot contain newline characters")

    def write_record_with_buffer(self, record: str) -> None:
        """
        Add record to a buffer and write it to a file when the buffer is full to reduce flash wear.
        Use this method for normal logging operations where data loss can be tolerated.
        """
        self._add_record_to_buffer(record)
        if self._buffer_full():
            self._write_buffer_to_file()
        gc.collect()

    def write_record(self, record: str) -> None:
        """
        Skip buffer and write the record directly to file.
        Use this method for critical records that should not be lost.
        It will wear out the flash faster, but ensures that critical records are saved.
        """
        with open(self.file_path, mode="a", encoding="utf-8") as file:
            file.write(record + "\n")
