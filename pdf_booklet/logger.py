import logging
import json
from datetime import datetime, timezone
import sys

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Merge extra fields if they exist and are not standard LogRecord fields
        if hasattr(record, "details") and isinstance(record.details, dict):
            log_record["details"] = record.details
            
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record, ensure_ascii=False)

class JsonLogger(logging.Logger):
    def _log(self, level, msg, args, **kwargs):
        # Extract custom 'details' keyword argument and inject into extra
        details = kwargs.pop("details", None)
        if details is not None:
            extra = kwargs.get("extra")
            if extra is None:
                extra = {}
            extra["details"] = details
            kwargs["extra"] = extra
        super()._log(level, msg, args, **kwargs)

# Set the custom logger class as default
logging.setLoggerClass(JsonLogger)

def get_logger(name="pdf-booklet-maker"):
    logger = logging.getLogger(name)
    
    # If logger already has handlers, don't add more (prevents duplicate logs)
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Send logs to stdout so they can be parsed easily by orchestration systems
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    
    return logger
