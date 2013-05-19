from zope.interface import Interface
from zope.component.hooks import getSite
from kagenomise.orders.interfaces import IOrderManager

def handle_checkout(event):
    site = getSite()
    order = IOrderManager(site).new_from_cart(event.data)
    event.context.REQUEST.response.redirect(
        '%s/checkout_success' % event.context.portal_url()
    )
