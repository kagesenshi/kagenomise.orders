from five import grok
from plone.directives import dexterity, form
from kagenomise.orders.content.order import IOrder
from kagenomise.orders.content.orderentry import IOrderEntry

grok.templatedir('templates')

class Index(dexterity.DisplayForm):
    grok.context(IOrder)
    grok.require('zope2.View')
    grok.template('order_view')
    grok.name('view')

    def items(self):
        results = []
        for i in self.context.values():
            if IOrderEntry.providedBy(i):
                results.append(i)
        return sorted(results, key=lambda x: x.getId())

