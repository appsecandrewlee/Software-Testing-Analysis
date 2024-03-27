from typing import List


class Item:
  def __init__(self, id: str, name: str, original_price: float, categories: List[str]):
    self.id: str = id
    self.name: str = name
    self.original_price: float = original_price
    self.categories: List[str] = categories
