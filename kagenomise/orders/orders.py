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
from zope.event import notify
from zope.lifecycleevent import (
        ObjectCreatedEvent, ObjectModifiedEvent,
        ObjectAddedEvent, ObjectMovedEvent
)

class Orders(grok.Adapter):
    grok.implements(IOrderManager)
    grok.context(Interface)

    def __init__(self, context):
        self.context = getSite()

    def repository(self):
        if 'cart_orders' not in self.context.keys():
            _createObjectByType('Folder', self.context, 'cart_orders')
            orders = self.context._getOb('cart_orders')
            notify(ObjectCreatedEvent(orders))
            notify(ObjectAddedEvent(orders))
        return self.context._getOb('cart_orders')

    def new_from_cart(self, data):

        orders = self.repository()
        
        tempid = str(time.time())
        order = _createObjectByType('kagenomise.orders.order',
                    orders, tempid)
        notify(ObjectCreatedEvent(order))
        notify(ObjectAddedEvent(order))
        now = datetime.datetime.today()
        title = u'%s : %s' % (now.strftime('%Y%m%d'), data['recipient_name'])
    
        transaction.savepoint(optimistic=True)
        oid = INameChooser(orders).chooseName(title, order)
        
        order.unindexObject()
        order._setId(oid)
        orders._delObject(tempid, suppress_events=True)
        orders._setObject(oid, order, set_owner=0, suppress_events=True)
        
        notify(ObjectMovedEvent(order, oldParent=orders, oldName=tempid, 
            newParent=orders, newName=oid))
        order.setTitle(title)

        for k in ['recipient_name','shipping_address','recipient_email',
                'recipient_phone']:
            setattr(order, k, data[k])
        order.reindexObject()

        entries = self._add_items(order, data['items'])

        notify(ObjectModifiedEvent(order))
        for entry in entries:
            notify(ObjectModifiedEvent(entry))

        return order

    def _add_items(self, order, items):
        result = []
        for item in items:
            obj = self._add_item(order, item)
            if obj:
                result.append(obj)
        return result

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
        notify(ObjectCreatedEvent(obj))
        notify(ObjectAddedEvent(obj))
        transaction.savepoint(optimistic=True)
        oid = INameChooser(order).chooseName(title, obj)

        obj.unindexObject()
        obj._setId(oid)
        order._delObject(tempid, suppress_events=True)
        order._setObject(oid, obj, set_owner=0, suppress_events=True)
        notify(ObjectMovedEvent(obj, oldParent=order, oldName=tempid,
            newParent=order, newName=oid))
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
