"""
For autofilling. Assumes IDs of html elements remain the same.
"""

enable_api = True
creds = None


def fill_default_box_values(data):
   """
   If dimensions, weight, and unit of box is undefined,
   substitute 0 and INCH as the default value.
   """
   if 'boxes' in data:
      # attributes are the dimensions, weight, units, etc.
      # of the box
      # see get_order_details in google_forms_autofill
      for box, attributes in data['boxes'].items():
        if 'length' not in attributes:
            attributes['length'] = 0
            print('updated length to 0')
        if 'width' not in attributes:
            attributes['width'] = 0
        if 'height' not in attributes:
            attributes['height'] = 0
        if 'weight' not in attributes:
            attributes['weight'] = 0
        if 'units' not in attributes:
           attributes['units'] = 'INCH'
   else:
      raise AssertionError("Key 'boxes' not found in data.")

def assign_customer_info(customer, data):
    """
    Updates customer information from a form request (data).
    Assumes name attributes of the input fields.

    Parameters:
    ----------
    customer: Customer
    data: form data sent as dict

    Returns
    ----------
    customer
    """
    customer.name = data['shipper_name']
    customer.email = data['shipper_email']
    customer.phone = data['shipper_phone']
    customer.address = data['shipper_address']
    customer.city = data['shipper_city']
    customer.state = data['shipper_state']
    customer.zip_code = data['shipper_zip']
    return customer

def assign_consignee_info(data, consignee=None):
    """
    Updates consignee information from a form request (data).
    Assumes name attributes of the input fields.

    Parameters:
    ----------
    data: form data sent as dict
    consignee: Consignee

    Returns
    ----------
    consignee
    """
    print(f'data: {data}')
    consignee.name = data['consignee_name']
    consignee.email = data['consignee_email']
    consignee.phone = data['consignee_phone']
    consignee.address = data['consignee_address']
    consignee.city = data['consignee_city']
    consignee.state = data['consignee_state']
    consignee.zip_code = data['consignee_zip']

    return consignee

def update_order_details(order, data):
    """
    Updates order details from a form request (data).
    Assumes name attributes of the input fields.

    Parameters:
    ----------
    order: CustomerOrder
    data: form data sent as dict

    Returns
    ----------
    order
    """
    if data.get('delivery-method') == 'office-office' or data.get('delivery-method') == 'office-door':
        office_dropoff = True
    else:
        office_dropoff = False
        order.pickup_address = data.get('pickup-address')
    # delivery address is consignee address by default
    office_pickup = data.get('delivery-method') == 'door-office' or data.get('delivery-method') == 'office-office'
    
    order.office_dropoff = office_dropoff
    order.office_pickup = office_pickup
    order.insurance = data.get('insurance') == 'on'
    order.notes = data.get('order-notes')
    return order

def assign_package_info(package, data):
    """
    Updates package information from a form request (data).
    Assumes name attributes of the input fields.

    Parameters:
    ----------
    package: Package
    data: form data sent as dict

    Returns
    ----------
    package
    """
    package.has_batteries = 'lithium_batteries' in data
    package.fragile = 'is_fragile' in data
    package.set_dimensions(
        length=float(data['length']),
        width=float(data['width']),
        height=float(data['height'])
    )
    package.dim_units = data['units']
    package.weight = float(''.join(filter(lambda char: char.isdigit() or char == '.', data['weight'])))
    package.description = data['package_description']
    return package

def autofill_from_form(form_data):
    # autofills ONE (1) order
    # keys defined in get_response_data from
    # google_forms_autofill
    # input is from google_forms_autofill.get_response_data(rows)
    data = {}
    #print(f'appending data from these dicts: ')
    #print(form_data)
    data.update(form_data["shipper"])
    data.update(form_data["consignee"])
    data.update(form_data["order_details"])
    fill_default_box_values(data)
    
    return data

def get_autofill_dict(customer=None, consignee=None, order=None, debugging=False):
    """
    Returns data (dict) for the HTML template to use.
    If order is None and debugging is false, returns blank dict.
    debugging autofills the data with fake testing values.

    Parameters:
    ----------
    customer: Customer
    consignee: Consignee
    order: CustomerOrder
    debugging: bool

    Returns
    ----------
    data: dict
    """
    if debugging:
      autofill_dict = {
        'shipper_name': 'John Doe',
        'shipper_address': '123 street',
        'shipper_city': 'Johns city',
        'shipper_state': 'Johns state',
        'shipper_zip': 'zip code',
        'shipper_phone': '2983748932',
        'shipper_email': 'john@gmail.com',
        'consignee_name': 'somebody',
        'consignee_address': 'address',
        'consignee_city': 'sombody city',
        'consignee_state': 'somebody state',
        'consignee_zip': 'somebody zip',
        'consignee_phone': '4873983',
        'consignee_email': '',
        'office_dropoff': True,
        'office_pickup': True,
        'insurance': False,
        'box_num': 2,
        'boxes': {
            '1': {
                'length': 2,
                'width': 10,
                'height': 3,
                'units': 'INCH',
                'weight': 234,
                'description': 'contains items',
                'batteries': True,
                'fragile': False,
            },
            '2': {
                'length': 4,
                'width': 10,
                'height': 12,
                'units': 'INCH',
                'weight': 14.5,
                'description': 'contains items',
                'batteries': True,
                'fragile': True,
            }
        }
    }
      return autofill_dict
    elif order is None:
      blank_dict = {
          'shipper_name': '',
          'shipper_address': '',
          'shipper_city': '',
          'shipper_state': '',
          'shipper_zip': '',
          'shipper_phone': '',
          'shipper_email': '',
          'consignee_name': '',
          'consignee_address': '',
          'consignee_city': '',
          'consignee_state': '',
          'consignee_zip': '',
          'consignee_phone': '',
          'consignee_email': '',
          'office_dropoff': "",
          'office_pickup': "",
          'insurance': "",
          'box_num': "",
          'boxes': {
              'length': "",
              'width': "",
              'height': "",
              'units': '',
              'weight': "",
              'description': '',
              'batteries': "",    # make this required in the html template
              'fragile': "",
          }
      }
      return blank_dict
    
    data = {}
    data_list = []

    if customer is not None:
      customer_dict = {
          'shipper_name': customer.name,
          'shipper_address': customer.address,
          'shipper_city': customer.city,
          'shipper_state': customer.state,
          'shipper_zip': customer.zip_code,
          'shipper_phone': customer.phone,
          'shipper_email': customer.email,
      }
      data_list.append(customer_dict)

    if consignee is not None:
      consignee_dict = {
          'consignee_name': consignee.name,
          'consignee_address': consignee.address,
          'consignee_city': consignee.city,
          'consignee_state': consignee.state,
          'consignee_zip': consignee.zip_code,
          'consignee_phone': consignee.phone,
          'consignee_email': consignee.email
      }
    else:
      consignee_dict = {
          'consignee_name': None,
          'consignee_address': None,
          'consignee_city': None,
          'consignee_state': None,
          'consignee_zip': None,
          'consignee_phone': None,
          'consignee_email': None
      }
    data_list.append(consignee_dict)

    order_dict = {
        'office_dropoff': order.delivery_option[0],
        'office_pickup': order.delivery_option[1],
        'insurance': order.insurance,
        'box_num': len(order.packages),
        'boxes': {
            'length': "",
            'width': "",
            'height': "",
            'units': "",
            'weight': "",
            'description': "",
            'batteries': "",
            'fragile': "",
        }
        #'boxes': {}
    }
    data_list.append(order_dict)
    """
    # currently no option to autofill package information
    for pk in order.packages:
        pk_dict = {
            'length': pk.dimensions[0],
            'width': pk.dimensions[1],
            'height': pk.dimensions[2],
            'units': pk.dim_units,
            'weight': pk.weight,
            'description': pk.description,
            'batteries': pk.has_batteries,
            'fragile': pk.fragile
        }
        order_dict["boxes"] = pk_dict
    """
    for d in data_list:
       data.update(d)
    return data