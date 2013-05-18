from five import grok
from plone.directives import dexterity, form
from kagenomise.orders.content.order import IOrder

grok.templatedir('templates')

class Index(dexterity.DisplayForm):
    grok.context(IOrder)
    grok.require('zope2.View')
    grok.template('order_view')
    grok.name('view')

