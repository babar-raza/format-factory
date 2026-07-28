"""SafeTensors-specific public errors."""

from format_factory.core import FormatParseError, FormatValidationError, FormatWriteError


class SafeTensorsError(FormatValidationError):
    code = "safetensors_error"


class SafeTensorsParseError(FormatParseError, SafeTensorsError):
    code = "safetensors_parse_error"


class SafeTensorsWriteError(FormatWriteError, SafeTensorsError):
    code = "safetensors_write_error"
