from pydantic import BaseModel, Field


class DeviceIdentifiers(BaseModel):
    device_alias: str | None = Field(alias="devalias")
    serial_number: str = Field(alias="sn")
    wifi_pin: str = Field(alias="pn")
    device_address: int = Field(alias="devaddr")
    device_code: int = Field(alias="devcode")

    class Config:
        allow_population_by_field_name = True
