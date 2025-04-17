from pydantic import BaseModel


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class Route(BaseModel):
    id: int
    name: str
    destinationStationId: int
    originStationId: int


class Station(BaseModel):
    id: int
    name: str
    coordinates: Coordinates
    arrivingRoutes: list[Route] = []
