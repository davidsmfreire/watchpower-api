from typing import Optional
from pydantic import BaseModel, Field

from pydantic.version import VERSION as _PYDANTIC_VERSION

PYDANTIC_VERSION: str = str(_PYDANTIC_VERSION)

if PYDANTIC_VERSION.startswith("2."):
    from pydantic import ConfigDict


class DeviceIdentifier(BaseModel):
    device_alias: Optional[str] = Field(default=None, alias="devalias")
    serial_number: str = Field(..., alias="sn")
    wifi_pin: str = Field(..., alias="pn")
    device_address: int = Field(..., alias="devaddr")
    device_code: int = Field(..., alias="devcode")

    if PYDANTIC_VERSION.startswith("2."):
        model_config = ConfigDict(populate_by_name=True)
    else:

        class Config:
            allow_population_by_field_name = True
