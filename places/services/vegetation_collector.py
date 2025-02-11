from abc import ABC, abstractmethod
from typing import List, Dict, AnyStr, Union, TYPE_CHECKING
if TYPE_CHECKING:
    from places.models import Place


class IVegetationCollector(ABC):
    @abstractmethod
    def get_data(self, place: "Place"):
        pass

    @abstractmethod
    def save(self, data: Union[List[Dict], Dict], filename: AnyStr):
        pass
