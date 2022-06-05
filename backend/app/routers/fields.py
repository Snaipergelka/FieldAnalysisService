import logging
from fastapi import APIRouter

router = APIRouter(
    prefix="/fields",
    tags=["fields"],
    )

logger = logging.getLogger()


@router.post("/field")
def add_field(field):
    logger.info(f"Accepted {field} to add to db.")

    # Getting info about products to which user is subscribed.
    logger.info(f"Added {field} to db.")


@router.delete("/field")
def delete_field(field):
    logger.info(f"Accepted {field} to delete from db.")

    # Getting info about products to which user is subscribed.
    logger.info(f"Deleted {field} from db.")
