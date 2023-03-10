import sys
import requests
import json
import pandas as pd

from loguru import logger
from pydantic import BaseModel, Field
from typing import Union, Optional


class ItemResponse(BaseModel):
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
    results: list[ItemResponse] = Field(...)
    

class DatasetItemsGenerator():

    def __init__(self, site: str, max_items_offset: int = 5000) -> None:
        self.site: str = site
        self.init_offset: int = 0
        self.items_response: list = []
        self.max_items_offset: int  = max_items_offset

    def get_raw_data(self):
        while self.init_offset <= self.max_items_offset:
            url = f"https://api.mercadolibre.com/sites/{self.site}/search?q=tv%204k&offset={self.init_offset}"
            response = requests.get(url=url)
            raw_data = response.json()
            self.items_response += ListItemsResponse(**raw_data).results
            self.init_offset+=50

    def transform_data(self):
        items = [item.get_brand().dict(exclude={'attributes'}) for item in self.items_response]
        structured_data = pd.DataFrame.from_records(items)
        self.data = structured_data[structured_data.condition == 'new']

    def save_dataset(self):
        self.data.to_csv("dataset.csv", columns=["id", "title" ,"price", "domain_id","brand"])


if __name__ == '__main__':
    site = sys.argv[1]
    dataset_generator = DatasetItemsGenerator(site)
    dataset_generator.get_raw_data()
    dataset_generator.transform_data()
    dataset_generator.save_dataset()