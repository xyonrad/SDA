from sda import auth
from loguru import logger

LOG_FILE = auth.DefaultDirectories.DATA / "logs" / "sda.log"

def configure_log(level: str = "INFO") -> None:
    if LOG_FILE.exists():
        LOG_FILE.unlink()
        
    logger.remove()
    logger.add(
        LOG_FILE,
        mode='w',
        encoding="utf-8",
        level=level,
        backtrace=True,
        diagnose=False
    )

def main():
    c = auth.get_config()
    configure_log(c.log_level)

if __name__ == "__main__":
    main()
