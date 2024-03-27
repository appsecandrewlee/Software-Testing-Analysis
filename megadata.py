from typing import Dict, List, Tuple, Optional
from Item import Item
from Customer import Customer
from Discount import Discount
from DiscountType import DiscountType

# Feel free to add your own data to the below lists: _items, _customers and _discounts.

# Tuple format: (Item, Current Stock Level, Purchase Quantity Limit)
_items: List[Tuple[Item, int, Optional[int]]] = [
  (Item('1', 'Tim Tam - Chocolate', 4.50, ['Confectionery', 'Biscuits']), 20, None),
  (Item('2', 'Coffee Powder', 16.00, ['Coffee', 'Drinks']), 12, 2),
  (Item('3', 'Laundry Detergent', 9.98, ['Household', 'Cleaning']), 5, None),
  (Item('4', 'Beer', 5.00, ['Alcohol', 'Drinks']), 7, None),
  (Item('5', 'Kitchen Knife', 5.00, ['Knives', 'Cooking']), 3, 1),
]

_customers = [
  Customer('123', 'Alice', '01/08/2005', True, None),
  Customer('456', 'Bob', '20/04/2010', True, 21),
  Customer('789', 'Carol', None, False, 15),
]

_discounts = [
  Discount(DiscountType.PERCENTAGE, 20.00, '1'),
  Discount(DiscountType.FLAT, 1.50, '2'),
]

## The below code should not be modified.

"""
Maps string item IDs to a tuple containing the corresponding item object, its current integer stock level and optionally, any integer purchase quantity limits.
E.g.:
{
  '1': (Item('1', 'Tim Tam - Chocolate', 4.50, ['Confectionery', 'Biscuits']), 20, None),
}
"""
items: Dict[str, Tuple[Item, int, Optional[int]]] = { item[0].id: item for item in _items }

"""
Maps string customer membership ID numbers to its corresponding customer object
E.g.:
{
  '123': Customer('123', 'Alice', '01/08/2005', True, None),
}
"""
customers: Dict[str, Customer] = { customer.membership_number: customer for customer in _customers }

"""
Maps string item IDs to its corresponding discount object
E.g.:
{
  '1': Discount(DiscountType.PERCENTAGE, 20.00, '1'),
}
"""
discounts: Dict[str, Discount] = { discount.item_id: discount for discount in _discounts }
