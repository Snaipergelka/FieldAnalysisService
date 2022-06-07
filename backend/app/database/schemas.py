from geojson_pydantic import FeatureCollection
from pydantic import BaseModel


class FieldCreate(BaseModel):
    geo_json: FeatureCollection


class AddNDVI(FieldCreate):
    id: int
