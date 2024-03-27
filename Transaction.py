from typing import List, Optional
from TransactionLine import TransactionLine
from Customer import Customer
from FulfilmentType import FulfilmentType
from PaymentMethod import PaymentMethod
from datetime import datetime



class Transaction:
  date: Optional[str] = None # format: dd/mm/YYYY e.g. 01/08/2023
  time: Optional[str] = None # format: HH:MM:SS e.g. 12:45:00
  transaction_lines: List[TransactionLine] = []
  customer: Optional[Customer] = None
  fulfilment_type: Optional[FulfilmentType] = None
  payment_method: Optional[PaymentMethod] = None
  amount_tendered: Optional[float] = None
  
  total_items_purchased: Optional[int] = None
  all_items_subtotal: Optional[float] = None
  fulfilment_surcharge_amount: Optional[float] = None
  rounding_amount_applied: Optional[float] = None
  final_total: Optional[float] = None
  change_amount: Optional[float] = None
  amount_saved: Optional[float] = None

  finalised: bool = False

  def __init__(self, date: str, time: str):
    self.date: str = date
    self.time: str = time

    self.date_as_datetime = datetime.strptime(date, "%d/%m/%Y")
