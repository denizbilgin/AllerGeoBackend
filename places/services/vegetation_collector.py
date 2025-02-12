from abc import ABC, abstractmethod
from typing import List, Dict, AnyStr, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from places.models import Place, Vegetation


class IVegetationCollector(ABC):
    @abstractmethod
    def get_data(self, place: "Place") -> List["Vegetation"]:
        pass

    @abstractmethod
    def save(self, data: List[Dict], is_city: bool, place: "Place"):
        pass
