import asyncio
import logging
from app.seeds.seed_data import seed_database_if_empty

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

if __name__ == "__main__":
    asyncio.run(seed_database_if_empty())
