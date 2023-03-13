import sys
import requests
import json
import pandas as pd

from pydantic import BaseModel, Field
from typing import  Optional


class ItemResponse(BaseModel):
    """
    Clase que modela cada Item individual que retorna el endpoint
    """
    id: str = Field(...)
    title: str = Field(...)
    condition: str = Field(...)
    price: int = Field(...)
    domain_id: str = Field(...)
    attributes: list[dict] = Field(...)
    brand: Optional[str]

    def get_brand(self):
        self.brand = list(filter(lambda x:x["id"] == "BRAND",self.attributes))[0]["value_name"]
        return self


class ListItemsResponse(BaseModel):
    """ Clase que modela toda la lista de items que retorna el endpoint
    """
    results: list[ItemResponse] = Field(...)
    

class DatasetItemsGenerator():
    """Clase que Genera el dataset de items
    """
    def __init__(self, site: str, max_items_offset: int = 1000) -> None:
        self.site: str = site
        self.init_offset: int = 0
        self.items_response: list = []
        self.max_items_offset: int  = max_items_offset

    def get_raw_data(self):
        """
        Función que obtiene la data cruda del endpoint
        """
        while self.init_offset <= self.max_items_offset:
            url = f"https://api.mercadolibre.com/sites/{self.site}/search?q=tv%204k&offset={self.init_offset}"
            response = requests.get(url=url)
            raw_data = response.json()
            self.items_response += ListItemsResponse(**raw_data).results
            self.init_offset+=50

    def transform_data(self):
        """Función que transforma la data en una tabla y obtiene la marca de cada item
        """
        items = [item.get_brand().dict(exclude={'attributes'}) for item in self.items_response]
        structured_data = pd.DataFrame.from_records(items)
        self.data = structured_data[structured_data.condition == 'new']

    def save_dataset(self):
        """Función apra guardar el dataset en un archivo csv
        """
        self.data.to_csv("dataset.csv", columns=["id", "title" ,"price", "domain_id","brand"])


if __name__ == '__main__':
    # Se obtiene el site (MLA, MLM, MLB)
    site = sys.argv[1]
    dataset_generator = DatasetItemsGenerator(site)
    # Se obtiene la data cruda
    dataset_generator.get_raw_data()
    #Se transforma la data al formato requerido 
    dataset_generator.transform_data()
    # Se guarda la data en un archivo csv
    dataset_generator.save_dataset()