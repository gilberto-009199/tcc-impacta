import logging

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from app.application import Application

if __name__ == "__main__":
    logging.info("O aplicativo iniciou!")
    app = Application()
    app.config()
    app.run()
