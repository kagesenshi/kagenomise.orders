from kagenomise.orders.interfaces import IOrderManager
from kagenomise.cart.interfaces import IItemTitle
from zope.component.hooks import getSite
from zope.container.interfaces import INameChooser
from Products.CMFPlone.utils import _createObjectByType
from five import grok
from zope.interface import Interface
import time
import transaction
from zope.intid.interfaces import IIntIds
from z3c.relationfield import RelationValue
from zope.component import getUtility
import datetime
from Products.CMFCore.interfaces import IContentish

class Orders(grok.Adapter):
    grok.implements(IOrderManager)
    grok.context(Interface)

    def __init__(self, context):
        self.context = getSite()

    def repository(self):
        if 'cart_orders' not in self.context.keys():
            _createObjectByType('Folder', self.context, 'cart_orders')
        return self.context._getOb('cart_orders')

    def new_from_cart(self, data):

        orders = self.repository()
        
        tempid = str(time.time())
        order = _createObjectByType('kagenomise.orders.order',
                    orders, tempid)

        now = datetime.datetime.today()
        title = u'%s : %s' % (now.strftime('%Y%m%d'), data['recipient_name'])
    
        transaction.savepoint(optimistic=True)
        oid = INameChooser(orders).chooseName(title, order)
        
        order.unindexObject()
        order._setId(oid)
        orders._delObject(tempid, suppress_events=True)
        orders._setObject(oid, order, set_owner=0, suppress_events=True)
        
        order.setTitle(oid)

        for k in ['recipient_name','shipping_address','recipient_email',
                'recipient_phone']:
            setattr(order, k, data[k])
        order.reindexObject()

        self._add_items(order, data['items'])

        return order

    def _add_items(self, order, items):
        for item in items:
            self._add_item(order, item)

    def _add_item(self, order, item):

        item_ref = None
        if item.get('path', None):
            item_ref = self.context.restrictedTraverse(str(item['path']))
            title = IItemTitle(item_ref).getTitle(item)
        elif item['meta_type'] == 'shipment':
            title = item['name']
        else:
            raise Exception(u'Invalid data')

        tempid = str(time.time())
        obj = _createObjectByType('kagenomise.orders.orderentry',
                order, tempid)
        transaction.savepoint(optimistic=True)
        oid = INameChooser(order).chooseName(title, obj)

        obj.unindexObject()
        obj._setId(oid)
        order._delObject(tempid, suppress_events=True)
        order._setObject(oid, obj, set_owner=0, suppress_events=True)

        if item_ref:
            obj.unit_price = item_ref.price
        else:
            obj.unit_price = item['price']

        obj.quantity = item['quantity']
        obj.setTitle(title)

        intids = getUtility(IIntIds)
        obj.item_reference = RelationValue(intids.queryId(item_ref))

        obj.reindexObject()

        return obj
