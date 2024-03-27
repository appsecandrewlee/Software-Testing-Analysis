import unittest
import megamart

from megamart import Item, Customer, Discount, DiscountType, FulfilmentType, PaymentMethod, Transaction, TransactionLine

from RestrictedItemException import RestrictedItemException
from PurchaseLimitExceededException import PurchaseLimitExceededException
from InsufficientStockException import InsufficientStockException
from FulfilmentException import FulfilmentException


class TestMegaMart(unittest.TestCase):
  def test_checkout_public_sample(self):
    item1 = (megamart.Item('1', 'Tim Tam - Chocolate', 4.50, ['Confectionery', 'Biscuits']), 20, None)

    items_dict = {
      '1': item1,
    }

    discounts_dict = {}

    transaction = megamart.Transaction('02/08/2023', '12:00:00')

    transaction.transaction_lines = [
      megamart.TransactionLine(item1[0], 2),
    ]

    transaction.payment_method = megamart.PaymentMethod.CASH
    transaction.fulfilment_type = megamart.FulfilmentType.PICKUP

    checkedout_transaction = megamart.checkout(transaction, items_dict, discounts_dict)
    self.assertEqual(checkedout_transaction.total_items_purchased, 2)

  # My Tests

  ## is_not_allowed_to_purchase_item() tests:

  def test_allowed_underage_restricted(self):
    category = "Alcohol"
    item = Item('1', "Whiskey", 50.00, [category])
    cust = Customer("12345", "John Doe", "02/08/2005", True, 5.0)
    purch_date = "01/08/2023"
    self.assertTrue(megamart.is_not_allowed_to_purchase_item(item, cust, purch_date),
                    f"Underage customer should not be able to purchase restricted item with category: {category}.")
    
  def test_allowed_underageleap_restricted(self):
    category = "Alcohol"
    item = Item('1', "Whiskey", 50.00, [category])
    cust = Customer("12345", "John Doe", "29/02/2004", True, 5.0)
    purch_date = "28/02/2022"
    self.assertTrue(megamart.is_not_allowed_to_purchase_item(item, cust, purch_date),
                    f"Underage customer should not be able to purchase restricted item with category: {category}.")

  def test_allowed_underage_restricted_case(self):
    category = "ALCOHOL"
    item = Item('1', "Whiskey", 50.00, [category])
    cust = Customer("12345", "John Doe", "02/08/2005", True, 5.0)
    purch_date = "01/08/2023"
    self.assertTrue(megamart.is_not_allowed_to_purchase_item(item, cust, purch_date),
                    f"Underage customer should not be able to purchase restricted item with category: {category}.")
    
  def test_allowed_underage_restricted_multicategory(self):
    categories = ["Beverage", "Drink", "Alcohol", "Health", "Fruit"]
    item = Item('1', "Cider", 50.00, categories)
    cust = Customer("12345", "John Doe", "02/08/2005", True, 5.0)
    purch_date = "01/08/2023"
    self.assertTrue(megamart.is_not_allowed_to_purchase_item(item, cust, purch_date),
                    f"Underage customer should not be able to purchase restricted item with categories: {categories}.")

  def test_allowed_adult_noid_restricted(self):
    category = "Alcohol"
    item = Item('1', "Whiskey", 50.00, [category])
    cust = Customer("12346", "Jane Doe", "02/08/2000", False, 5.0)
    purch_date = "02/08/2023"
    self.assertTrue(megamart.is_not_allowed_to_purchase_item(item, cust, purch_date),
                    f"Adult without ID verification should not be able to purchase restricted item with category: {category}.")
  
  def test_allowed_nodate_restricted(self):
    category = "Alcohol"
    item = Item('1', "Whiskey", 50.00, [category])
    cust = Customer("12346", "Jane Doe", None, False, 5.0)
    purch_date = "02/08/2023"
    self.assertTrue(megamart.is_not_allowed_to_purchase_item(item, cust, purch_date),
                    f"Customer without associated date of birth should not be able to purchase restricted item with category: {category}.")

  def test_allowed_adult_id_restricted(self):
    category = "Alcohol"
    item = Item('1', "Whiskey", 50.00, [category])
    cust = Customer("12347", "Jim Brown", "02/08/2000", True, 5.0)
    purch_date = "02/08/2023"
    self.assertFalse(megamart.is_not_allowed_to_purchase_item(item, cust, purch_date),
                    f"Adult with ID verification should be able to purchase restricted item with category: {category}.")

  def test_allowed_underage_unrestricted(self):
    category = "Beverage"
    item = Item('2', "Juice", 5.00, [category])
    cust = Customer("12345", "John Doe", "02/08/2005", True, 5.0)
    purch_date = "02/08/2023"
    self.assertFalse(megamart.is_not_allowed_to_purchase_item(item, cust, purch_date),
                     f"Underage customer should be able to purchase unrestricted item with category: {category}.")

  def test_allowed_noitem_exception(self):
    item = None
    cust = Customer("12347", "Jim Brown", "02/08/2000", True, 5.0)
    purch_date = "02/08/2023"
    with self.assertRaises(Exception, msg="Exception should be raised on None item object."):
      megamart.is_not_allowed_to_purchase_item(item, cust, purch_date)
  
  def test_allowed_invalidpurchdate_exception(self):
    category = "Alcohol"
    item = Item('2', "Beer", 5.00, [category])
    cust = Customer("12347", "Jim Brown", "02/08/2000", True, 5.0)
    purch_date = "123/456/789"
    with self.assertRaises(Exception, msg="Exception should be raised on invalid purchase date format."):
      megamart.is_not_allowed_to_purchase_item(item, cust, purch_date)

  def test_allowed_invalidDOB_exception(self):
    category = "Alcohol"
    item = Item('2', "Beer", 5.00, [category])
    cust = Customer("12347", "Jim Brown", "123/456/789", True, 5.0)
    purch_date = "02/08/2023"
    with self.assertRaises(Exception, msg="Exception should be raised on invalid Date of Birth format."):
      megamart.is_not_allowed_to_purchase_item(item, cust, purch_date)

  ## get_item_purchase_quantity_limit() tests:

  def test_qtylimit_haslimit(self):
    item1 = Item('1', "Whiskey", 50.00, ["Alcohol"])  # Test Item
    item2 = Item('2', "Juice", 5.00, ["Beverage"])
    limit = 2
    items_dict = { '1' : (item1, 10, limit), '2' : (item2, 20, None) }
    self.assertEqual(megamart.get_item_purchase_quantity_limit(item1, items_dict), limit,
                     f"Item that has limit should return the limit of {limit} provided in items_dict.")

  def test_qtylimit_nolimit_indict(self):
    item1 = Item('1', "Whiskey", 50.00, ["Alcohol"])
    item2 = Item('2', "Juice", 5.00, ["Beverage"])  # Test Item
    items_dict = { '1' : (item1, 10, 2), '2' : (item2, 20, None) }
    self.assertIsNone(megamart.get_item_purchase_quantity_limit(item2, items_dict),
                      "Item in items_dict with no limit should return None limit.")

  def test_qtylimit_nolimit_notindict(self):
    item1= Item('1', "Whiskey", 50.00, ["Alcohol"])
    item2 = Item('2', "Juice", 5.00, ["Beverage"])
    item3 = Item('3', "Soda", 2.00, ["Beverage"]) # Test Item
    items_dict = { '1' : (item1, 10, 2), '2' : (item2, 20, None) }
    self.assertIsNone(megamart.get_item_purchase_quantity_limit(item3, items_dict),
                      "Item not in items_dict should return None limit.")

  def test_qtylimit_noitem_exception(self):
    itemNone = None # Test Item
    item1 = Item('1', "Whiskey", 50.00, ["Alcohol"])
    items_dict = { '1' : (item1, 5, None) }
    with self.assertRaises(Exception, msg="Exception should be raised on None item provided."):
      megamart.get_item_purchase_quantity_limit(itemNone, items_dict)

  def test_qtylimit_nodict_exception(self):
    item1 = Item('1', "Tim Tam - Chocolate", 4.50, ["Confectionary", "Biscuits"])
    items_dict = None
    with self.assertRaises(Exception, msg="Exception should be raised on None items dictionary provided."):
      megamart.get_item_purchase_quantity_limit(item1, items_dict)

  ## is_item_sufficiently_stocked() tests:

  def test_stocked_sufficient(self):
    item1 = Item('1', "Apple", 0.50, ["Fruit"]) # Test Item
    item2 = Item('2', "Banana", 0.30, ["Fruit"])
    qty = 5
    stock = 10
    items_dict = { '1' : (item1, stock, None), '2' : (item2, 5, 3) }
    self.assertTrue(megamart.is_item_sufficiently_stocked(item1, qty, items_dict),
                    f"Item with stock {stock} should be sufficiently stocked when bought at quantity {qty}.")

  def test_stocked_insufficient(self):
    item1 = Item('1', "Apple", 0.50, ["Fruit"]) # Test Item
    item2 = Item('2', "Banana", 0.30, ["Fruit"])
    qty = 15
    stock = 10
    items_dict = { '1' : (item1, stock, None), '2' : (item2, 5, 3) }
    self.assertFalse(megamart.is_item_sufficiently_stocked(item1, qty, items_dict),
                    f"Item with stock {stock} should not be sufficiently stocked when bought at quantity {qty}.")

  def test_stocked_notindict(self):
    item1 = Item('2', "Banana", 0.30, ["Fruit"])
    qty = 3
    items_dict = { '1' : (item1, 10, None) }
    self.assertFalse(megamart.is_item_sufficiently_stocked(item1, qty, items_dict),
                     "Item not in item_dict should not be considered sufficiently stocked.")
    
  def test_stocked_noitem_exception(self):
    itemNone = None # Test Item
    item1 = Item('1', "Apple", 0.50, ["Fruit"]) 
    item2 = Item('2', "Banana", 0.30, ["Fruit"])
    qty = 2
    items_dict = { '1' : (item1, 10, None), '2' : (item2, 5, 3) }
    with self.assertRaises(Exception, msg="Exception should be raised on None item object provided."):
      megamart.is_item_sufficiently_stocked(itemNone, qty, items_dict)

  def test_stocked_noqty_exception(self):
    item1 = Item('1', "Apple", 0.50, ["Fruit"]) 
    item2 = Item('2', "Banana", 0.30, ["Fruit"])  # Test Item
    qty = None
    items_dict = { '1' : (item1, 10, None), '2' : (item2, 5, 3) }
    with self.assertRaises(Exception, msg="Exception should be raised on None quantity provided."):
      megamart.is_item_sufficiently_stocked(item1, qty, items_dict)

  def test_stocked_nodict_exception(self):
    item1 = Item('1', "Apple", 0.50, ["Fruit"]) 
    qty = 3
    items_dict = None
    with self.assertRaises(Exception, msg="Exception should be raised on None dictionary provided."):
      megamart.is_item_sufficiently_stocked(item1, qty, items_dict)

  def test_stocked_invalidqty_exception(self):
    item1 = Item('1', "Apple", 0.50, ["Fruit"]) # Test Item
    item2 = Item('2', "Banana", 0.30, ["Fruit"])  
    qty = 0
    items_dict = { '1' : (item1, 10, None), '2' : (item2, 5, 3) }
    with self.assertRaises(Exception, msg="Exception should be raised on quantity <1."):
      megamart.is_item_sufficiently_stocked(item1, qty, items_dict)

  def test_stocked_invalidstock_exception(self):
    item1 = Item('1', "Apple", 0.50, ["Fruit"]) # Test Item
    item2 = Item('2', "Banana", 0.30, ["Fruit"])  
    qty = 3
    items_dict = { '1' : (item1, -1, None), '2' : (item2, 5, 3) }
    with self.assertRaises(Exception, msg="Exception should be raised when checking item with negative stock value."):
      megamart.is_item_sufficiently_stocked(item1, qty, items_dict)

  ## calculate_final_item_price() tests:

  def test_itemprice_pctdiscount(self):
    item = Item('1', "Tim Tam - Chocolate", 4.50, ["Confectionary", "Biscuits"])
    discounts_dict = { '1' : Discount(DiscountType.PERCENTAGE, 20.00, '1') }
    self.assertAlmostEqual(megamart.calculate_final_item_price(item, discounts_dict), 3.6, 2,
                     "Item with percentage discount should be discounted properly.")

  def test_itemprice_flatdiscount(self):
    item = Item('2', "Coffee Powder", 16.00, ["Coffee", "Drinks"])
    discounts_dict = { '2' : Discount(DiscountType.FLAT, 1.50, '2') }
    self.assertAlmostEqual(megamart.calculate_final_item_price(item, discounts_dict), 14.5, 2,
                     "Item with flat discount should be discounted properly.")

  def test_itemprice_nodiscount(self):
    price = 5.00
    item = Item('5', "Kitchen Knife", price, ["Knives", "Cooking"])
    discounts_dict = { '1' : Discount(DiscountType.PERCENTAGE, 20.00, '1'), '2' : Discount(DiscountType.FLAT, 1.50, '2') }
    self.assertAlmostEqual(megamart.calculate_final_item_price(item, discounts_dict), price, 2,
                     f"Undiscounted item should stay at the same price: {price}.")

  def test_itemprice_nodict_exception(self):
    item = Item('1', "Tim Tam - Chocolate", 4.50, ["Confectionary", "Biscuits"])
    discounts_dict = None
    with self.assertRaises(Exception, msg="Exception should be raised on no discounts_dict,"):
      megamart.calculate_final_item_price(item, discounts_dict)

  def test_itemprice_noitem_exception(self):
    item = None
    discounts_dict = { '1' : Discount(DiscountType.PERCENTAGE, 20.00, '1') }
    with self.assertRaises(Exception, msg="Exception should be raised on no item."):
      megamart.calculate_final_item_price(item, discounts_dict)

  def test_itemprice_highpctdiscount_exception(self):
    item = Item('1', "Tim Tam - Chocolate", 4.50, ["Confectionary", "Biscuits"])
    discounts_dict = { '1' : Discount(DiscountType.PERCENTAGE, 100.01, '1') }
    with self.assertRaises(Exception, msg="Exception should be raised on percentage discount too high (>100.00)."):
      megamart.calculate_final_item_price(item, discounts_dict)

  def test_itemprice_lowpctdiscount_exception(self):
    item = Item('1', "Tim Tam - Chocolate", 4.50, ["Confectionary", "Biscuits"])
    discounts_dict = { '1' : Discount(DiscountType.PERCENTAGE, 0.99, '1') }
    with self.assertRaises(Exception, msg="Exception should be raised on percentage discount too low (<1.00)."):
      megamart.calculate_final_item_price(item, discounts_dict)

  def test_itemprice_highflatdiscount_exception(self):
    item = Item('2', "Coffee Powder", 16.00, ["Coffee", "Drinks"])
    discounts_dict = { '2' : Discount(DiscountType.FLAT, -1.00, '2') }
    with self.assertRaises(Exception, msg="Item with flat discount should raise exception if discount causes price increase."):
      megamart.calculate_final_item_price(item, discounts_dict)

  def test_itemprice_negflatdiscount_exception(self):
    item = Item('2', "Coffee Powder", 16.00, ["Coffee", "Drinks"])
    discounts_dict = { '2' : Discount(DiscountType.FLAT, 30, '2') }
    with self.assertRaises(Exception, msg="Item with flat discount should raise exception if discount causes price to be negative."):
      megamart.calculate_final_item_price(item, discounts_dict)

  ## calculate_item_savings() tests:

  def test_savings_valid(self):
    original_price = 5.25
    final_price = 4.32
    self.assertAlmostEqual(megamart.calculate_item_savings(original_price, final_price), 0.93, 2,
                     "Calculation for amount saved on valid values should provide correct result.")
    
  def test_savings_nooriginal_exception(self):
    original_price = None
    final_price = 93.24
    with self.assertRaises(Exception, msg="Exception should be raised on no original price provided."):
      megamart.calculate_item_savings(original_price, final_price)

  def test_savings_nofinal_exception(self):
    original_price = 29.65
    final_price = None
    with self.assertRaises(Exception, msg="Exception should be raised on no final price provided."):
      megamart.calculate_item_savings(original_price, final_price)

  def test_savings_pricegreater_exception(self):
    original_price = 63.20
    final_price = 500.25
    with self.assertRaises(Exception, msg="Exception should be raised when final price > original price."):
      megamart.calculate_item_savings(original_price, final_price)

  ## calculate_fulfilment_surcharge() tests:

  def test_fulfilment_deliver_low(self):
    type = FulfilmentType.DELIVERY
    distance = 3  # Km
    cust = Customer('1', "John Doe", "19/05/1990", True, distance)
    self.assertAlmostEqual(megamart.calculate_fulfilment_surcharge(type, cust), 5, 2,
                     f"Low distance of {distance}km should result in defaulting to price of $5.")
    
  def test_fulfilment_deliver_boundary(self):
    type = FulfilmentType.DELIVERY
    distance = 10  # Km
    cust = Customer('1', "John Doe", "19/05/1990", True, distance)
    self.assertAlmostEqual(megamart.calculate_fulfilment_surcharge(type, cust), 5, 2,
                     f"Boundary distance of {distance}km should result in price of $5.")

  def test_fulfilment_deliver_high(self):
    type = FulfilmentType.DELIVERY
    distance = 19.55  # Km
    cust = Customer('1', "John Doe", "19/05/1990", True, distance)
    self.assertAlmostEqual(megamart.calculate_fulfilment_surcharge(type, cust), 9.78, 2,
                     f"Higher distance of {distance}km should result in price of $9.78 (rounded) for 50c per km.")

  def test_fulfilment_pickup(self):
    type = FulfilmentType.PICKUP
    distance = 0  # Km
    cust = Customer('1', "John Doe", "19/05/1990", True, distance)
    self.assertAlmostEqual(megamart.calculate_fulfilment_surcharge(type, cust), 0, 2,
                     f"Pickup order should result in no fulfilment surcharge.")

  def test_fulfilment_notype_exception(self):
    type = None
    distance = 0  # Km
    cust = Customer('1', "John Doe", "19/05/1990", True, distance)
    with self.assertRaises(Exception):
      megamart.calculate_fulfilment_surcharge(type, cust)

  def test_fulfilment_nodistance_exception(self):
    type = FulfilmentType.DELIVERY
    distance = None  
    cust = Customer('1', "John Doe", "19/05/1990", True, distance)
    with self.assertRaises(FulfilmentException):
      megamart.calculate_fulfilment_surcharge(type, cust)

  ## round_off_subtotal() tests:

  def test_roundsubtotal_credit(self):
    subtotal = 10.2356
    method = PaymentMethod.CREDIT
    self.assertEqual(megamart.round_off_subtotal(subtotal, method), 10.24,
                     "No 5c rounding should occur on credit transactions.")

  def test_roundsubtotal_debit(self):
    subtotal = 10.2356
    method = PaymentMethod.DEBIT
    self.assertEqual(megamart.round_off_subtotal(subtotal, method), 10.24,
                     "No 5c rounding should occur on debit transactions.")

  def test_roundsubtotal_cash_0down(self):
    template_subtotal = "10.2"
    method = PaymentMethod.CASH
    cents = ["1", "2"]
    for i, cent in enumerate(cents):
      with self.subTest(i=i):
        subtotal = float(template_subtotal + cent)
        self.assertEqual(megamart.round_off_subtotal(subtotal, method), 10.20,
                         f"Cent values ending in {cent} should round down.")

  def test_roundsubtotal_cash_0up(self):
    template_subtotal = "10.2"
    method = PaymentMethod.CASH
    cents = ["8", "9"]
    for i, cent in enumerate(cents):
      with self.subTest(i=i):
        subtotal = float(template_subtotal + cent)
        self.assertEqual(megamart.round_off_subtotal(subtotal, method), 10.30,
                         f"Cent values ending in {cent} should round up.")

  def test_roundsubtotal_cash_5down(self):
    template_subtotal = "10.2"
    method = PaymentMethod.CASH
    cents = ["6", "7"]
    for i, cent in enumerate(cents):
      with self.subTest(i=i):
        subtotal = float(template_subtotal + cent)
        self.assertEqual(megamart.round_off_subtotal(subtotal, method), 10.25,
                         f"Cent values ending in {cent} should round down.")

  def test_roundsubtotal_cash_5up(self):
    template_subtotal = "10.2"
    method = PaymentMethod.CASH
    cents = ["3", "4"]
    for i, cent in enumerate(cents):
      with self.subTest(i=i):
        subtotal = float(template_subtotal + cent)
        self.assertEqual(megamart.round_off_subtotal(subtotal, method), 10.25,
                         f"Cent values ending in {cent} should round up.")

  def test_roundsubtotal_nosubtotal_exception(self):
    subtotal = None
    method = PaymentMethod.CASH
    with self.assertRaises(Exception, msg="Exception should be raised on None subtotal."):
      megamart.round_off_subtotal(subtotal, method)

  def test_roundsubtotal_nomethod_exception(self):
    subtotal = 10.29
    method = None
    with self.assertRaises(Exception, msg="Exception should be raised on None method."):
      megamart.round_off_subtotal(subtotal, method)

  ## checkout() tests:

  def test_checkout_basic(self):
    transaction = Transaction("20/08/2023", "02:24:00")
    transaction.customer = Customer('1', "John Doe", "10/09/1996", True, None)
    transaction.fulfilment_type = FulfilmentType.PICKUP
    transaction.payment_method = PaymentMethod.CASH
    item = Item('1', "Tim Tam - Chocolate", 4.50, ["Confectionary", "Biscuits"])
    transaction.transaction_lines = [TransactionLine(item, 1)]
    items_dict = { '1' : (item, 20, None) }
    discounts_dict = {  }

    checkout = megamart.checkout(transaction, items_dict, discounts_dict)
    self.assertEqual(checkout.final_total, 4.50, 
                     "Basic transaction with 1 item should produce the correct final price.")

  def test_checkout_advanced(self):
    transaction = Transaction("20/08/2023", "09:56:00")
    transaction.customer = Customer("123", "Daniel Gower", "10/09/2002", True, 109)
    transaction.fulfilment_type = FulfilmentType.DELIVERY
    transaction.payment_method = PaymentMethod.CASH
    item1 = Item("1", "Cookie", 7.27, ["Sweet", "Baked"])
    item2 = Item("8", "Apple Cider", 15.50, ["Fruit", "Alcohol"])
    transaction.transaction_lines = [
      TransactionLine(item1, 16),
      TransactionLine(item2, 2)
    ]
    items_dict = { '1' : (item1, 38, 16), '8' : (item2, 2, None) }
    discounts_dict = { '8' : Discount(DiscountType.PERCENTAGE, 65, '8') }

    checkout = megamart.checkout(transaction, items_dict, discounts_dict)
    expected_vs_actual = [
      [127.16, checkout.all_items_subtotal],
      [54.50, checkout.fulfilment_surcharge_amount], 
      [-0.01, checkout.rounding_amount_applied], 
      [181.65, checkout.final_total], 
      [20.16, checkout.amount_saved],
      [18, checkout.total_items_purchased]
    ]

    for i in range(len(expected_vs_actual)):
      with self.subTest(i=i):
        self.assertAlmostEqual(expected_vs_actual[i][0], expected_vs_actual[i][1], 2,
                         f"Advanced checkout test failed on subtest {i+1}. Comparing {expected_vs_actual[i][0]} and {expected_vs_actual[i][1]}")

  def test_checkout_agerestrict_exception(self):
    transaction = Transaction("20/08/2023", "02:24:00")
    transaction.customer = Customer('1', "John Doe", "10/09/2007", True, None)
    transaction.fulfilment_type = FulfilmentType.PICKUP
    transaction.payment_method = PaymentMethod.CASH
    item = Item('2', "Whiskey", 50.00, ["Alcohol"])
    transaction.transaction_lines = [TransactionLine(item, 1)]
    items_dict = { '1' : (item, 20, None) }
    discounts_dict = { }

    with self.assertRaises(RestrictedItemException, msg="RestrictedItemException should be raised on underage customer purchasing restricted item."):
      megamart.checkout(transaction, items_dict, discounts_dict)

  def test_checkout_stock_exception(self):
    transaction = Transaction("20/08/2023", "02:24:00")
    transaction.customer = Customer('1', "John Doe", "10/09/1996", True, None)
    transaction.fulfilment_type = FulfilmentType.PICKUP
    transaction.payment_method = PaymentMethod.CASH
    item = Item('2', "Whiskey", 50.00, ["Alcohol"])
    transaction.transaction_lines = [TransactionLine(item, 5)]
    items_dict = { '2' : (item, 4, None) }
    discounts_dict = { }

    with self.assertRaises(InsufficientStockException, msg="InsufficientStockException should be raised on item over purchase limit."):
      megamart.checkout(transaction, items_dict, discounts_dict)

  def test_checkout_limit_exception(self):
    transaction = Transaction("20/08/2023", "02:24:00")
    transaction.customer = Customer('1', "John Doe", "10/09/1996", True, None)
    transaction.fulfilment_type = FulfilmentType.PICKUP
    transaction.payment_method = PaymentMethod.CASH
    item = Item('2', "Whiskey", 50.00, ["Alcohol"])
    transaction.transaction_lines = [TransactionLine(item, 5)]
    items_dict = { '2' : (item, 50, 2) }
    discounts_dict = { }

    with self.assertRaises(PurchaseLimitExceededException, msg="PurchaseLimitExceededException should be raised on item over purchase limit."):
      megamart.checkout(transaction, items_dict, discounts_dict)

  def test_checkout_flatdiscount(self):
    transaction = Transaction("20/08/2023", "02:24:00")
    transaction.customer = Customer('1', "John Doe", "10/09/1996", True, None)
    transaction.fulfilment_type = FulfilmentType.PICKUP
    transaction.payment_method = PaymentMethod.CASH
    item = Item('3', "Coffee Powder", 16.00, ["Coffee", "Drinks"])
    transaction.transaction_lines = [TransactionLine(item, 2)]
    items_dict = { '3' : (item, 50, 2) }
    discounts_dict = { '3' : Discount(DiscountType.FLAT, 1.50, '3') }

    checkout = megamart.checkout(transaction, items_dict, discounts_dict)
    self.assertEqual(checkout.final_total, 29.00,
                     "Flat discounted item should have discount reflected in total.")

  def test_checkout_pctdiscount(self):
    transaction = Transaction("20/08/2023", "02:24:00")
    transaction.customer = Customer('1', "John Doe", "10/09/1996", True, None)
    transaction.fulfilment_type = FulfilmentType.PICKUP
    transaction.payment_method = PaymentMethod.CASH
    item = Item('3', "Coffee Powder", 16.00, ["Coffee", "Drinks"])
    transaction.transaction_lines = [TransactionLine(item, 2)]
    items_dict = { '3' : (item, 50, 2) }
    discounts_dict = { '3' : Discount(DiscountType.PERCENTAGE, 50, '3') }

    checkout = megamart.checkout(transaction, items_dict, discounts_dict)
    self.assertEqual(checkout.final_total, 16.00, 
                     "Percentage discounted item should have discount reflected in total.")

  def test_checkout_delivery(self):
    transaction = Transaction("20/08/2023", "02:24:00")
    transaction.customer = Customer('1', "John Doe", "10/09/1996", True, 10)
    transaction.payment_method = PaymentMethod.CASH
    transaction.fulfilment_type = FulfilmentType.DELIVERY
    item = Item('3', "Coffee Powder", 16.00, ["Coffee", "Drinks"])
    transaction.transaction_lines = [TransactionLine(item, 2)]
    items_dict = { '3' : (item, 50, 2) }
    discounts_dict = { }

    checkout = megamart.checkout(transaction, items_dict, discounts_dict)
    self.assertEqual(checkout.fulfilment_surcharge_amount, 5,
                     "Delivery fee should be correctly applied.")

  def test_checkout_rounding(self):
    transaction = Transaction("20/08/2023", "02:24:00")
    transaction.customer = Customer('1', "John Doe", "10/09/1996", True, 10)
    transaction.fulfilment_type = FulfilmentType.PICKUP
    transaction.payment_method = PaymentMethod.CASH
    item = Item('3', "Coffee Powder", 16.32, ["Coffee", "Drinks"])
    transaction.transaction_lines = [TransactionLine(item, 2)]
    items_dict = { '3' : (item, 50, 2) }
    discounts_dict = { }

    checkout = megamart.checkout(transaction, items_dict, discounts_dict)
    self.assertAlmostEqual(checkout.final_total, 32.65, 2,
                     "Rounding should be correctly applied.")
    self.assertAlmostEqual(checkout.rounding_amount_applied, 0.01, 2,
                  "Rounding should be correctly applied.")

  def test_checkout_notransaction_exception(self):
    transaction = None
    item = Item('2', "Whiskey", 50.00, ["Alcohol"])
    items_dict = { '2' : (item, 50, 2) }
    discounts_dict = { }

    with self.assertRaises(Exception, msg="Exception should be raised on None transaction."):
      megamart.checkout(transaction, items_dict, discounts_dict)

  def test_checkout_noitemsdict_exception(self):
    transaction = Transaction("20/08/2023", "02:24:00")
    transaction.customer = Customer('1', "John Doe", "10/09/1996", True, 10)
    transaction.fulfilment_type = FulfilmentType.PICKUP
    transaction.payment_method = PaymentMethod.CASH
    item = Item('3', "Coffee Powder", 16.32, ["Coffee", "Drinks"])
    transaction.transaction_lines = [TransactionLine(item, 2)]
    items_dict = None
    discounts_dict = { }

    with self.assertRaises(Exception, msg="Exception should be raised on None items dictionary."):
      megamart.checkout(transaction, items_dict, discounts_dict)

  def test_checkout_nodiscountdict_exception(self):
    transaction = Transaction("20/08/2023", "02:24:00")
    transaction.customer = Customer('1', "John Doe", "10/09/1996", True, 10)
    transaction.fulfilment_type = FulfilmentType.PICKUP
    transaction.payment_method = PaymentMethod.CASH
    item = Item('3', "Coffee Powder", 16.32, ["Coffee", "Drinks"])
    transaction.transaction_lines = [TransactionLine(item, 2)]
    items_dict = { '3' : (item, 50, 2) }
    discounts_dict = None

    with self.assertRaises(Exception, msg="Exception should be raised on None discounts dictionary."):
      megamart.checkout(transaction, items_dict, discounts_dict)

  def test_checkout_example1(self):
    transaction = Transaction("23/08/2023", "09:48:00")
    item1 = Item('1', "Tim Tams", 4.50, ["Chocolate"])      
    item2 = Item('2', "Coffee Powder", 16.00, ["Coffee"])
    item3 = Item('3', "Item 3", 9.98, [])
    transaction.transaction_lines = [ TransactionLine(item1, 2), TransactionLine(item2, 1), TransactionLine(item3, 1) ]
    transaction.fulfilment_type = FulfilmentType.PICKUP
    transaction.payment_method = PaymentMethod.CASH
    items_dict = { '1' : (item1, 20, None), '2' : (item2, 12, 2), '3' : (item3, 1000, None) }
    discounts_dict = { '1' : Discount(DiscountType.PERCENTAGE, 20, '1'), '2' : Discount(DiscountType.FLAT, 1.5, '2') }
    checkout = megamart.checkout(transaction, items_dict, discounts_dict)
    self.assertEqual(checkout.final_total, 31.70, 
                     "The checkout function should pass the first example given in the specification.")
    self.assertEqual(checkout.amount_saved, 3.30,
                     "The checkout function should pass the first example given in the specification.")
    

  def test_checkout_example2(self):
    transaction = Transaction("23/08/2023", "09:48:00")
    item1 = Item('1', "Tim Tams", 4.50, ["Chocolate"])      
    item2 = Item('2', "Coffee Powder", 16.00, ["Coffee"])
    item3 = Item('3', "Item 3", 9.98, [])
    transaction.customer = Customer('1', "Name", "10/09/2002", True, 15)
    transaction.transaction_lines = [ TransactionLine(item1, 2), TransactionLine(item2, 1), TransactionLine(item3, 1) ]
    transaction.fulfilment_type = FulfilmentType.DELIVERY
    transaction.payment_method = PaymentMethod.CREDIT
    items_dict = { '1' : (item1, 20, None), '2' : (item2, 12, 2), '3' : (item3, 1000, None) }
    discounts_dict = { '1' : Discount(DiscountType.PERCENTAGE, 20, '1'), '2' : Discount(DiscountType.FLAT, 1.5, '2') }
    checkout = megamart.checkout(transaction, items_dict, discounts_dict)
    self.assertEqual(checkout.final_total, 39.18, 
                     "The checkout function should pass the second example given in the specification.")
    
  def test_checkout_example3(self):
    transaction = Transaction("23/08/2023", "09:48:00")
    item1 = Item('1', "Tim Tams", 4.50, ["Chocolate"])      
    item2 = Item('2', "Coffee Powder", 16.00, ["Coffee"])
    item3 = Item('3', "Item 3", 9.98, [])
    transaction.transaction_lines = [ TransactionLine(item1, 2), TransactionLine(item2, 3), TransactionLine(item3, 1) ]
    transaction.fulfilment_type = FulfilmentType.PICKUP
    transaction.payment_method = PaymentMethod.CASH
    items_dict = { '1' : (item1, 20, None), '2' : (item2, 12, 2), '3' : (item3, 1000, None) }
    discounts_dict = { '1' : Discount(DiscountType.PERCENTAGE, 20, '1'), '2' : Discount(DiscountType.FLAT, 1.5, '2') }
    with self.assertRaises(Exception, msg="The checkout function should pass the third example given in the specification."):
        checkout = megamart.checkout(transaction, items_dict, discounts_dict)

  def test_checkout_example4(self):
    transaction = Transaction("23/08/2023", "09:48:00")
    item1 = Item('1', "Tim Tams", 4.50, ["Chocolate"])      
    item2 = Item('2', "Coffee Powder", 16.00, ["Coffee"])
    item3 = Item('3', "Item 3", 9.98, [])
    transaction.transaction_lines = [ TransactionLine(item1, 25), TransactionLine(item2, 1), TransactionLine(item3, 1) ]
    transaction.fulfilment_type = FulfilmentType.PICKUP
    transaction.payment_method = PaymentMethod.CASH
    items_dict = { '1' : (item1, 20, None), '2' : (item2, 12, 2), '3' : (item3, 1000, None) }
    discounts_dict = { '1' : Discount(DiscountType.PERCENTAGE, 20, '1'), '2' : Discount(DiscountType.FLAT, 1.5, '2') }
    with self.assertRaises(Exception, msg="The checkout function should pass the fourth example given in the specification."):
        checkout = megamart.checkout(transaction, items_dict, discounts_dict)

unittest.main()
