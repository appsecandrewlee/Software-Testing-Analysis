class Customer:
  def __init__(self, membership_number: str, name: str, date_of_birth: str, id_verified: bool, delivery_distance_km: float):
    self.membership_number: str = membership_number
    self.name: str = name
    self.date_of_birth: str = date_of_birth
    self.id_verified: bool = id_verified
    self.delivery_distance_km: float = delivery_distance_km
