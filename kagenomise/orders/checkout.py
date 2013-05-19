from zope.interface import Interface
from zope.component.hooks import getSite
from kagenomise.orders.interfaces import IOrderManager

def handle_checkout(event):
    site = getSite()

    IOrderManager(site).new_from_cart(event.data)
