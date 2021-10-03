from decimal import *

class CosmosUtil:
  @classmethod
  def get_attribute_value(cls, attributes, key):
    return list(filter(lambda x: x['key'] == key, attributes))[0]['value']

  @classmethod
  def get_event_value(cls, events, type):
    event = list(filter(lambda x: x['type'] == type, events))
    if len(event) == 0:
      return None
    else:
      return list(filter(lambda x: x['type'] == type, events))[0]

  @classmethod
  def convert_uamount_amount(cls, uatom):
    atom = Decimal(int(uatom.replace('uatom', ''))) / Decimal(1000000)
    return atom