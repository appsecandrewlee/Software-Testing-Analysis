from datetime import datetime
from typing import Dict, Tuple, Optional
from PaymentMethod import PaymentMethod
from FulfilmentType import FulfilmentType
from TransactionLine import TransactionLine
from Transaction import Transaction
from Item import Item
from Customer import Customer
from Discount import Discount

from InsufficientFundsException import InsufficientFundsException

from megamart import calculate_final_item_price, calculate_item_savings, checkout


def scan_item(items_dict: Dict[str, Tuple[Item, int, Optional[int]]]) -> TransactionLine:
  item = None
  quantity = None

  while True:
    item_id = input("\n>>> What is the item code? (Enter 'quit' to cancel) \n")
    if item_id == 'quit':
      return None

    if item_id not in items_dict:
      print('Item with the provided ID was not found, please try again.')
      continue
    
    item = items_dict[item_id][0]
    print("Found item: '{}'".format(item.name))
    break

  while True:
    quantity = input("\n>>> What is the quantity? (Enter 'quit' to cancel)\n")
    if quantity == 'quit':
      return None
    
    try:
      quantity = int(quantity)
      if quantity <= 0:
        raise Exception()

    except:
      print('The provided quantity is not a whole number that is at least 1, please try again.')
      continue

    break

  return TransactionLine(item, quantity)


def list_items(transaction: Transaction, discounts_dict: Dict[str, Discount]) -> Tuple[int, str, str]:
  list_string = f"{'#':<5} {'ITEM NAME':<30} {'QUANTITY':<10} {'UNIT PRICE ($)':>20} {'TOTAL DISCOUNTS APPLIED ($)':>35} {'FINAL PRICE ($)':>20}\n"

  items_total = 0 
  for (index, transaction_line) in enumerate(transaction.transaction_lines):
    final_price = calculate_final_item_price(transaction_line.item, discounts_dict)
    discounts = calculate_item_savings(transaction_line.item.original_price, final_price)
    items_total += final_price * transaction_line.quantity
    list_string += f"{(index + 1):<5} {transaction_line.item.name :<30} {transaction_line.quantity:<10} {('{:.2f} {}'.format(transaction_line.item.original_price, 'each')):>20} {(discounts * transaction_line.quantity):>35.2f} {(final_price * transaction_line.quantity):>20.2f}\n"

  totals_string = f"{'':<5} {'':<30} {'':<10} {'':>20} {'===============================':>35}={'====================':>20}\n"
  totals_string += f"{'':<5} {'':<30} {'':<10} {'':>20} {'TOTAL PRICE ($)':>35} {items_total:>20.2f}\n"
  totals_string += f"{'':<5} {'':<30} {'':<10} {'':>20} {'===============================':>35}={'====================':>20}"

  return items_total, list_string, totals_string


def link_member_account(customers_dict: Dict[str, Customer]) -> Optional[Customer]:
  customer = None

  while True:
    customer_id = input("\n>>> What is your membership number? (Enter 'quit' to cancel) \n")
    if customer_id == 'quit':
      return None

    if customer_id not in customers_dict:
      print('The membership number you provided was not found, please try again.')
      continue

    customer = customers_dict[customer_id]
    print("Found member: '{}'".format(customer.name))
    return customer


def remove_transaction_line(transaction: Transaction) -> Tuple[Optional[int], Optional[Transaction]]:
  max_line_number = len(transaction.transaction_lines)
  if max_line_number == 0:
    return None, None

  line_number_to_remove = None

  while True:
    line_number_to_remove = input(">>> What is the line number of the item to remove? (Enter 'quit' to cancel)\n")
    if line_number_to_remove == 'quit':
      return None, None
    
    try:
      line_number_to_remove = int(line_number_to_remove)
      if not(0 < line_number_to_remove <= max_line_number):
        raise Exception()

    except:
      print('The provided line number is not a whole number between 1 and {} inclusive, please try again.'.format(max_line_number))
      continue

    break

  return line_number_to_remove, transaction.transaction_lines.pop(line_number_to_remove - 1)


def select_fulfilment_type() -> Optional[FulfilmentType]:
  num_fulfilment_types = len(FulfilmentType)
  if num_fulfilment_types == 0:
    return None

  selected_type = None
  fulfilment_types_list = [e for e in FulfilmentType]

  while True:
    print('\nFulfilment Types:')
    for (index, method) in enumerate(FulfilmentType):
      print('{}. {}'.format(index + 1, method.value))

    selected_type = input(">>> Which fulfilment type (1 to {}) would you like to use? (Enter 'quit' to cancel)\n".format(num_fulfilment_types))
    if selected_type == 'quit':
      return None
    
    try:
      selected_type = int(selected_type)
      if not(0 < selected_type <= num_fulfilment_types):
        raise Exception()

    except:
      print('The provided fulfilment type number is not a whole number between 1 and {} inclusive, please try again.'.format(num_fulfilment_types))
      continue

    break

  return fulfilment_types_list[selected_type - 1]


def select_payment_method() -> Optional[PaymentMethod]:
  num_payment_methods = len(PaymentMethod)
  if num_payment_methods == 0:
    return None

  selected_method = None
  payment_methods_list = [e for e in PaymentMethod]

  while True:
    print('\nPayment Methods:')
    for (index, method) in enumerate(PaymentMethod):
      print('{}. {}'.format(index + 1, method.value))

    selected_method = input(">>> Which payment method (1 to {}) would you like to use? (Enter 'quit' to cancel)\n".format(num_payment_methods))
    if selected_method == 'quit':
      return None
    
    try:
      selected_method = int(selected_method)
      if not(0 < selected_method <= num_payment_methods):
        raise Exception()

    except:
      print('The provided payment method number is not a whole number between 1 and {} inclusive, please try again.'.format(num_payment_methods))
      continue

    break

  return payment_methods_list[selected_method - 1]


def tender_variable_payment(transaction: Transaction) -> Transaction:
  while True:
    amount = input("\n>>> How much would you like to pay using {}? ${:.2f} is currently due. (Enter 'quit' to cancel)\n".format(transaction.payment_method.value, transaction.final_total))
    if amount == 'quit':
      return transaction

    try:
      split_amount_string = amount.split(".")
      if len(split_amount_string) == 2 and len(split_amount_string[1]) > 2:
        raise Exception('Amount tendered is invalid, it cannot be more than two decimal places.')

      amount = float(amount)
      if amount < 0:
        raise Exception('Amount tendered is invalid, it cannot be negative.')

    except:
      print('The tendered amount cannot be negative and cannot be more than two decimal places, please try again.')
      continue

    break

  transaction.amount_tendered = amount

  # Check amount tendered covers final order total
  if transaction.amount_tendered < transaction.final_total:
    raise InsufficientFundsException('Amount tendered (${:.2f}) is less than the total price of the ordered items (${:.2f}).'.format(transaction.amount_tendered, transaction.final_total))

  change_amount = transaction.amount_tendered - transaction.final_total
  transaction.change_amount = change_amount
  transaction.finalised = True

  return transaction


def tender_exact_payment(transaction: Transaction) -> Transaction:
  while True:
    response = input("\n>>> ${:.2f} is currently due. Enter 'Y' to pay exact amount by {}. (Enter 'N' or 'quit' to cancel)\n".format(transaction.final_total, transaction.payment_method.value))
    if response == 'quit' or response.lower() == 'n':
      return transaction

    if response.lower() == 'y':
      transaction.amount_tendered = transaction.final_total
      transaction.change_amount = 0
      transaction.finalised = True

      return transaction

    print('Invalid input, please try again.')


def generate_receipt(transaction: Transaction, discounts_dict: Dict[str, Discount]) -> str:
  if not transaction.finalised:
     raise Exception('Cannot print a receipt for an unfinalised transaction.')

  receipt_border = f"{'=====':<5}={'==============================':<30}={'==========':<10}={'====================':>20}={'===================================':>35}={'====================':>20}\n"

  # Build header
  receipt_text = receipt_border
  receipt_text += 'MONASH MEGAMART RECEIPT\n'
  receipt_text += receipt_border

  receipt_text += 'Transaction time: {} {}\n'.format(transaction.date, transaction.time)
  receipt_text += 'Fulfilment type: {}\n'.format(transaction.fulfilment_type.value)

  if (transaction.customer):
    receipt_text += 'Customer: {}\n'.format(transaction.customer.name)
    receipt_text += 'Membership #: {}\n'.format(transaction.customer.membership_number)

  receipt_text += receipt_border

  item_total, list_string, totals_string = list_items(transaction, discounts_dict)

  receipt_text += "Purchased items:\n"
  receipt_text += list_string

  receipt_text += "\n"
  receipt_text += receipt_border
  receipt_text += f"{'':<5} {'':<30} {'':<10} {'':>20} {'SUBTOTAL ($)':>35} {(transaction.all_items_subtotal or 0):>20.2f}\n"
  receipt_text += f"{'':<5} {'':<30} {'':<10} {'':>20} {'FULFILMENT SURCHARGE ($)':>35} {(transaction.fulfilment_surcharge_amount or 0):>20.2f}\n"
  receipt_text += f"{'':<5} {'':<30} {'':<10} {'':>20} {'ROUNDING ($)':>35} {(transaction.rounding_amount_applied or 0):>20.2f}\n\n"
  receipt_text += f"{'':<5} {'':<30} {'':<10} {'':>20} {'===============================':>35}={'====================':>20}\n"
  receipt_text += f"{'':<5} {'':<30} {'':<10} {'':>20} {'FINAL TOTAL ($)':>35} {(transaction.final_total or 0):>20.2f}\n"
  receipt_text += f"{'':<5} {'':<30} {'':<10} {'':>20} {'===============================':>35}={'====================':>20}\n\n"
  receipt_text += f"{'':<5} {'':<30} {'':<10} {'':>20} {'PAYMENT METHOD':>35} {transaction.payment_method.value:>20}\n"
  receipt_text += f"{'':<5} {'':<30} {'':<10} {'':>20} {'AMOUNT TENDERED ($)':>35} {(transaction.amount_tendered or 0):>20.2f}\n"
  receipt_text += f"{'':<5} {'':<30} {'':<10} {'':>20} {'CHANGE ($)':>35} {(transaction.change_amount or 0):>20.2f}\n"
  receipt_text += f"{'':<5} {'':<30} {'':<10} {'':>20} {'# ITEMS PURCHASED':>35} {(transaction.total_items_purchased or 0):>20}\n\n"
  receipt_text += f"{'':<5} {'':<30} {'':<10} {'':>20} {'MONEY SAVED WITH US ($)':>35} {(transaction.amount_saved or 0):>20.2f}\n"

  # Build footer
  receipt_text += receipt_border
  receipt_text += 'Thank you for shopping at Monash MegaMart, please come again!\n'
  receipt_text += receipt_border

  return receipt_text


def terminal(items_dict: Dict[str, Tuple[Item, int, Optional[int]]], discounts_dict: Dict[str, Discount], customers_dict: Dict[str, Customer]) -> None:
  print("===========================")
  print("Welcome to Monash MegaMart!")
  print("===========================\n")

  now = datetime.now()
  current_datetime = now.strftime("%d/%m/%Y %H:%M:%S")

  transaction = Transaction(current_datetime.split(" ")[0], current_datetime.split(" ")[1])

  while True:
    print()
    if transaction.customer:
      print(':: {} - Member #{} ::'.format(transaction.customer.name, transaction.customer.membership_number))
    print("MAIN MENU")
    print("1. Scan items")
    print("2. List scanned items")
    print("3. Link member account")
    print("4. Checkout")
    print("5. Remove item")
    print("6. Cancel transaction\n")

    option = input(">>> Please enter an option number (between 1 to 6) to continue:\n")
    if option == "1":
        while True:
          transaction_line = scan_item(items_dict)
          
          if transaction_line is None:
            break
          
          transaction.transaction_lines.append(transaction_line)
          print("\nItem '{}' added, adding next item...\n".format(transaction_line.item.name))

    elif option == "2":
      if len(transaction.transaction_lines) == 0:
        print('No items are currently scanned!')
        continue

      print('Current items:\n')
      item_total, list_string, totals_string = list_items(transaction, discounts_dict)

      print("")
      print(list_string)
      print(totals_string)
      print("Note: Price shown excludes any surcharges and roundings.")

    elif option == "3":
      if transaction.customer:
        print('{}, entering another membership number other than your own will cause your current account to be unlinked from this transaction.'.format(transaction.customer.name))

      customer = link_member_account(customers_dict)
      
      if customer is None:
        continue

      transaction.customer = customer
      print('Hi {}! Your member account (membership #{}) is now linked to this transaction.'.format(customer.name, customer.membership_number))

    elif option == "4":
      if len(transaction.transaction_lines) == 0:
        print('There are no items to checkout!')
        continue

      print('Current items:\n')
      item_total, list_string, totals_string = list_items(transaction, discounts_dict)

      print("")
      print(list_string)
      print(totals_string)
      print("Note: Price shown excludes any surcharges and roundings.")

      fulfilment_type = select_fulfilment_type()
      if fulfilment_type is None:
        print('Fulfilment type not selected. Returning to main menu.')
        continue

      transaction.fulfilment_type = fulfilment_type

      payment_method = select_payment_method()
      if payment_method is None:
        print('Payment method not selected. Returning to main menu.')
        continue

      transaction.payment_method = payment_method

      try:
        transaction = checkout(transaction, items_dict, discounts_dict)

        if transaction.final_total is None or transaction.final_total <= 0:
          transaction.finalised = True
        elif transaction.payment_method == PaymentMethod.CASH:
          transaction = tender_variable_payment(transaction)
        else:
          # Assume exact amount will always be tendered when paying by credit/debit card
          transaction = tender_exact_payment(transaction)

        if transaction.finalised is False:
          print('Payment cancelled. Returning to main menu.')
          continue

        print("Transaction successful! Generating receipt...\n")        
        print(generate_receipt(transaction, discounts_dict))
        break

      except Exception as e:
        print("{}:".format(type(e).__name__), str(e))
        # Uncomment to print out stack trace if required for debugging
        # import traceback
        # traceback.print_exc()
        continue

    elif option == "5":
      if len(transaction.transaction_lines) == 0:
        print('No items are available to remove!')
        continue

      print('Current items:\n')
      item_total, list_string, totals_string = list_items(transaction, discounts_dict)

      print("")
      print(list_string)

      line_number, removed_transaction_line = remove_transaction_line(transaction)
      if line_number is None or removed_transaction_line is None:
        print("\nNo item was removed.\n")
        continue

      print("\nItem #{} - '{}' removed.\n".format(line_number, removed_transaction_line.item.name))

    elif option == "6":
        print("Transaction cancelled.")
        print("Thank you for shopping at Monash MegaMart!")
        break

    else:
        print("Your input is invalid. Please try again.")
