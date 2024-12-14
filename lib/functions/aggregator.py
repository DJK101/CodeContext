from logging import getLogger
from flask import Response, make_response
from lib.datamodels import DTO_Aggregator, DTO_Device
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from lib.constants import HTTP
from lib.models import Aggregator, Device
from lib.timed_session import TimedSession

logger = getLogger(__name__)


def create_aggregator(aggregator_data: DTO_Aggregator) -> Response:
    missing_devices: list[str] = []
    with TimedSession("create_aggregator") as session:
        aggregator = Aggregator(name=aggregator_data.name)

        for device_data in aggregator_data.devices:
            stmt = select(Device).where(Device.name == device_data.name)

            try:
                device = session.execute(stmt).scalar_one()
            except NoResultFound:
                missing_devices.append(device_data.name)
                device = Device(aggregator=aggregator, name=device_data.name)
            
            session.add(device)
            aggregator.devices.append(device)
        
        session.add(aggregator)
    
    logger.info("Created missing devices: %s", missing_devices)

    return make_response(
        {"message": f"Successfully created aggregator '{aggregator_data.name}'"},
        HTTP.STATUS.OK,
    )
