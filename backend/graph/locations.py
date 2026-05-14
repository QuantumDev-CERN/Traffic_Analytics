from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    name: str
    lat: float
    lng: float
    criticality: float
    free_flow_speed: float = 52.0


LOCATIONS: dict[str, Location] = {
    "Connaught Place": Location("Connaught Place", 28.6315, 77.2167, 0.96),
    "India Gate": Location("India Gate", 28.6129, 77.2295, 0.84),
    "Karol Bagh": Location("Karol Bagh", 28.6519, 77.1909, 0.78),
    "Lajpat Nagar": Location("Lajpat Nagar", 28.5677, 77.2433, 0.76),
    "Akshardham Route": Location("Akshardham Route", 28.6127, 77.2773, 0.81),
    "DND Flyway": Location("DND Flyway", 28.5688, 77.2831, 0.89),
    "IGI Airport T3": Location("IGI Airport T3", 28.5562, 77.1000, 0.73),
    "Dwarka Sector 21": Location("Dwarka Sector 21", 28.5523, 77.0583, 0.64),
    "Cyber Hub Gurgaon": Location("Cyber Hub Gurgaon", 28.4950, 77.0886, 0.86),
    "MG Road Gurgaon": Location("MG Road Gurgaon", 28.4796, 77.0806, 0.75),
    "Sector 18 Noida": Location("Sector 18 Noida", 28.5708, 77.3261, 0.82),
    "Sector 62 Noida": Location("Sector 62 Noida", 28.6278, 77.3649, 0.70),
    "Botanical Garden": Location("Botanical Garden", 28.5640, 77.3342, 0.77),
    "Greater Noida West": Location("Greater Noida West", 28.6060, 77.4262, 0.58),
    "Vaishali Ghaziabad": Location("Vaishali Ghaziabad", 28.6498, 77.3390, 0.67),
    "Pari Chowk": Location("Pari Chowk", 28.4650, 77.5130, 0.60),
}


def as_geojson_points() -> list[dict]:
    return [
        {
            "name": item.name,
            "lat": item.lat,
            "lng": item.lng,
            "criticality": item.criticality,
        }
        for item in LOCATIONS.values()
    ]
