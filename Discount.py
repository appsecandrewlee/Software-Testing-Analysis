from DiscountType import DiscountType


class Discount:
  def __init__(self, type: DiscountType, value: float, item_id: str):
    self.type: DiscountType = type
    self.value: float = value
    self.item_id: str = item_id
