"""import libraries."""
from datetime import datetime
from typing import Dict, Tuple, Optional
from dateutil.relativedelta import relativedelta
from DiscountType import DiscountType
from PaymentMethod import PaymentMethod
from FulfilmentType import FulfilmentType
from Transaction import Transaction
from Item import Item
from Customer import Customer
from Discount import Discount

from RestrictedItemException import RestrictedItemException
from PurchaseLimitExceededException import PurchaseLimitExceededException
from InsufficientStockException import InsufficientStockException
from FulfilmentException import FulfilmentException
from InsufficientFundsException import InsufficientFundsException

# You are to complete the implementation for the eight methods below:
# START


def _get_eighteenth_birthday(birth_date: datetime):
    nonleap = birth_date + relativedelta(years=18)
    # Handle birthdays, leap year is considered 18years + 1day
    if nonleap.day != birth_date.day:
        return nonleap + relativedelta(days=1)
    return nonleap


def purchase_not_allow(item: Item, customer: Customer, pur_date: str) -> bool:
    """
    Return True if the customer can't purchase item, return False otherwise.

    If an item or the purchase date is not provided, Exception will be raised.
    Items that are under the alcohol tobacco or knives category,
    It can only sell to customers who are aged 18+ and have their ID verified.
    An item potentially belongs to many categories
    if it belongs to at least one of the three categories above
    then restrictions apply to that item.
    The checking of an item's categories against restricted categories
    This should be done in a case-insensitive manner.
    For example, if an item A is in the category ['Alcohol'] and item B
    is in the category ['ALCOHOL'], both items A and B
    should be identified as restricted items.
    Even if the customer is aged 18+ and is verified
    they must provide/link their member account
    to the transaction when purchasing restricted items.
    Otherwise, if a member account is not provided
    they will not be allowed to purchase
    the restricted item even if normally allowed to.
    It is optional for customers
    to provide their date of birth in their profile.
    Purchase date string should be of the format dd/mm/yyyy.
    The age of the customer is calculated
    from their specified date of birth
    which is also of the format dd/mm/yyyy.
    If an item is a restricted item
    but the purchase or birth date is in the incorrect format
    an Exception should be raised.
    A customer whose date of birth is 01/08/2005 is only considered
    to be age 18+ on or after 01/08/2023.
    """
    res_cat = ["Alcohol", "Tobacco", "Knives"]
    # Check that an item object and purchase date string are actually provided.
    if item is None:
        raise RestrictedItemException()

    # Handle restricted items
    if any(c1.lower() == c2.lower()
           for c1 in item.categories
           for c2 in res_cat):
        # Defensive Check
        if customer is None:
            return True
        if customer.date_of_birth is None:
            return True
        if pur_date is None:
            return True
        # Check for valid dates
        cd = customer.date_of_birth
        f = r"%d/%m/%Y"
        try:
            cust_datetime = _get_eighteenth_birthday(datetime.strptime(cd, f))
            purch_datetime = datetime.strptime(pur_date, f)

        except ValueError as check:
            raise RestrictedItemException() from check

        return bool(not customer.id_verified or
                    (cust_datetime > purch_datetime))

    # Unrestricted items
    return False


ChanR = Dict[str, Tuple[Item, int, Optional[int]]]


def get_purch_quantity_limit(item: Item, items_dict: ChanR) -> Optional[int]:
    """
    For a given item, returns the integer purchase quantity limit.

    If an item object or items dictionary was not actually provided
    an Exception should be raised.
    If the item was not found in the items dictionary
    or if the item does not have a purchase quantity limit
    None should be returned.
    The items dictionary (which is a mapping from keys to values)
    contains string item IChanR as its keys,
    and tuples containing an item object, integer stock level and an optional
    integer purchase quantity limit (which may be None)
    that correspond to their respective item ID as values.
    """
    # Check that an item object and items dictionary are actually provided.
    if item is None or items_dict is None:
        raise InsufficientStockException()

    return items_dict[item.id][2] if item.id in items_dict else None


def is_stock_suff(item: Item, purch_quantity: int, items_dict: ChanR) -> bool:
    """
    For a given item, returns True if the purchase quantity does not exceed.

    the currently available stock, or False if it exceeChanR
    or the item was not found in the items dictionary.
    If an item object, purchase quantity or
    items dictionary was not actually provided,
    an Exception should be raised.
    Purchase quantity should be a minimum of 1,
    and stock level is always a minimum of 0.
    Otherwise, an Exception should be raised for each of these situations.
    The items dictionary
    (which is a mapping from keys to values)
    contains string item IChanR as its keys,
    and tuples containing an item object,
    integer stock level and an optional integer purchase quantity limit
    (which may be None) that correspond to their respective item ID as values.
    """
    # Check that an item object,
    # purchase quantity,
    # and items dictionary are actually provided.
    if item is None or purch_quantity is None or items_dict is None:
        raise InsufficientStockException()
    # Check for purchase quantity too low or stock level too low for item
    if purch_quantity < 1:
        raise InsufficientStockException()
    if (item.id in items_dict and items_dict[item.id][1] < 0):
        raise InsufficientStockException()

    if item.id in items_dict:
        return purch_quantity <= items_dict[item.id][1]
    return False


RenameR = Dict[str, Discount]


def calculate_final_item_price(item: Item, discounts_dict: RenameR) -> float:
    """
    Return item's final price may change if.

    there is currently a discount available for it.
    If an item object or discounts dictionary was not actually provided,
    an Exception should be raised.
    There are two types of discounts - it may be a percentage off
    the original price, or a flat amount off the original price.
    Percentage-based discounts have a
    value defined between 1 and 100 inclusive.
    Otherwise, an Exception should be thrown.
    For example, a percentage-type discount of value 25 means a
    25% discount should be applied to that item.
    Flat-based discounts should not cause the item's final price to
    be more than its original price or be negative.
    Otherwise, an Exception should be thrown.
    For example, a flat-type discount of value 1.25 means a
    discount of $1.25 should be applied to that item.
    The discounts dictionary (which is a mapping from keys to values)
    contains string item IChanR as its keys,
    and discount objects that correspond to their respective item ID as values.
    If an item has an associated discount,
    the discounts dictionary
    (which is a mapping from keys to values)
    will contain a key corresponding to the ID of that item.
    Otherwise, if the item does not have an associated discount,
    its final price would be the same as its original price.
    """
    # Check that item object and discounts dictionary are actually provided
    if item is None or discounts_dict is None:
        raise InsufficientStockException()

    rounded_original_price = round(item.original_price, 2)

    if item.id in discounts_dict:
        discount = discounts_dict[item.id]

    if discount.type == DiscountType.PERCENTAGE:
        pct = discount.value
        if pct < 1.00 or pct > 100.00:
            raise InsufficientStockException()
        return round(
            rounded_original_price -
            (rounded_original_price * (pct/100)), 2)

    if discount.type == DiscountType.FLAT:
        rounded_price = round(rounded_original_price - discount.value, 2)
        if rounded_price > rounded_original_price or rounded_price < 0:
            raise InsufficientStockException()
        return rounded_price

    return rounded_original_price


def calculate_item_savings(i_o_p: float, item_final_price: float) -> float:
    """
    Return Savings on an item is defined as how much money.

    you would not need to spend on an item compared to
    if you bought it at its original price.
    If an item's original price or final price
    was not actually provided, an Exception should be raised.
    If the final price of the item is greater than
    its original price, an Exception should be raised.
    """
    if i_o_p is None or item_final_price is None:
        raise FulfilmentException()
    if item_final_price > i_o_p:
        raise FulfilmentException()

    return round(round(i_o_p, 2) - round(item_final_price, 2), 2)


def cfs(fulfilment_type: FulfilmentType, cus: Customer) -> float:
    """
    Return Currently, a fulfilment surcharge is only applicable for deliveries.

    There is no surcharge applied in any other case.
    The fulfilment surcharge is calculated as $5 or
    $0.50 for every kilometre, whichever is greater.
    Surcharge value returned should have at
    most two decimal places.
    If a fulfilment type was not actually provided,
    an Exception should be raised.
    Delivery fulfilment type can only be used if the
    customer has linked their member account to the transaction,
    and if delivery distance is specified in their member profile.
    Otherwise, a FulfilmentException should be raised.
    """
    # Check for fulfilment type
    if fulfilment_type is None:
        raise FulfilmentException()

    if fulfilment_type is FulfilmentType.DELIVERY:
        # Check for Customer and Customer distance if Delivery
        if cus is None:
            raise FulfilmentException()
        if cus.delivery_distance_km is None:
            raise FulfilmentException()
        if cus.delivery_distance_km <= 0:
            raise FulfilmentException()
        default = 5
        calculated = 0.5 * cus.delivery_distance_km
        return round(max(default, calculated), 2)

    return 0


def round_off_subtotal(sub: float, payment_method: PaymentMethod) -> float:
    """
    Return Currently, subtotal rounding is only applicable when paying by cash.

    There is no rounding performed in any other case.
    If the subtotal value or payment method was not actually provided,
    an Exception should be raised.
    The subtotal is rounded off to the nearest multiple of 5 cents.
    Surcharge value returned should have at most two decimal places.
    Cent amounts which have their ones-place digit as 1 - 2
    or 6 - 7 will be rounded down. If it is 3 - 4 or 8 - 9,
    it will be rounded up instead.
    As the (monetary) subtotal value is provided as a float,
    ensure that it is first rounded off to two
    decimal places before doing the rounding.
    """
    # Check float and payment method is not None
    if sub is None or payment_method is None:
        raise InsufficientFundsException()

    rounded_subtotal = round(sub, 2)

    if payment_method is PaymentMethod.CASH:
        return round((5 * round(int(rounded_subtotal*100)/5))/100, 2)

    return rounded_subtotal


def checkout(trans: Transaction, i_d: ChanR, d_d: RenameR) -> Transaction:
    """
    Return this method will need to utilise all of the seven methoChanR above.

    As part of the checkout process, each of the transaction
    lines in the transaction should be processed.
    If a transaction object, items dictionary or discounts
    dictionary was not actually provided, an Exception should be raised.
    All items in the transaction should be checked against
    any restrictions, available stock levels and purchase quantity limits.
    If a restricted item in the transaction may not be
    purchased by the customer initiating the transaction,
    a RestrictedItemException should be raised.
    If an item in the transaction exceeChanR purchase quantity limits,
    a PurchaseLimitExceededException should be raised.
    If an item in the transaction is of insufficient stock,
    an InsufficientStockException should be raised.
    All of the transaction lines will need to be processed
    in order to calculate its respective final price
    after applicable discounts have been applied.
    The subtotal, surcharge and rounding amounts,
    as well as final total, total savings from discounts
    and total number of items purchased also
    need to be calculated for the transaction.
    Once the calculations are completed,
    the updated transaction object should be returned.
    """
    # Check that a transaction object,
    # items dictionary and discounts dictionary are actually provided.
    if trans is None:
        raise PurchaseLimitExceededException("debug transaction")
    if i_d is None:
        raise PurchaseLimitExceededException("debug item_dict")
    if d_d is None:
        raise PurchaseLimitExceededException("debug RenameR")
    if trans.customer is None:
        raise PurchaseLimitExceededException("debug customer")
    if trans.date is None:
        raise PurchaseLimitExceededException("debug transaction date")

    total_items, subtotal, surcharge, savings = 0, 0.00, 0.00, 0.00

    for line in trans.transaction_lines:
        item, qty = line.item, line.quantity
    if purchase_not_allow(item, trans.customer, trans.date):
        raise RestrictedItemException("debug purchase not allowed")
    if not is_stock_suff(item, qty, i_d):
        raise InsufficientStockException("debug no stock")

    limit = get_purch_quantity_limit(item, i_d)
    if limit and qty > limit:
        raise PurchaseLimitExceededException("debug quantity limit ")

    if i_d[item.id][2] is None:
        raise InsufficientStockException("debug entry[2]")
    first = i_d[item.id][1] - qty
    second = i_d[item.id][2]
    i_d[item.id] = (i_d[item.id][0],
                    first,
                    second - qty if second is not None and limit else second)

    price = calculate_final_item_price(item, d_d)
    savings += calculate_item_savings(item.original_price, price) * qty
    total_items += qty
    subtotal += price * qty
    if trans.fulfilment_type is None:
        raise InsufficientStockException("debug fulfilment_type")

    surcharge = cfs(trans.fulfilment_type, trans.customer)

    if trans.payment_method is None:
        raise InsufficientStockException()
    temp_total = subtotal + surcharge
    trans.final_total = round_off_subtotal(temp_total, trans.payment_method)
    trans.total_items_purchased = total_items
    trans.all_items_subtotal = round(subtotal, 2)
    trans.fulfilment_surcharge_amount = round(surcharge, 2)
    trans.amount_saved = round(savings, 2)
    trans.rounding_amount_applied = round(trans.final_total - (temp_total), 2)

    return trans

# END
