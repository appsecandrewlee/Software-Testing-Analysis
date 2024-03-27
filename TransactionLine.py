from typing import Optional
from Item import Item

class TransactionLine:
  final_cost: Optional[float]

  def __init__(self, item: Item, quantity: int):
    self.item: Item = item
    self.quantity: int = quantity
