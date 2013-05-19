from five import grok
from plone.directives import dexterity, form
from kagenomise.orders.content.orderentry import IOrderEntry

grok.templatedir('templates')

class Index(dexterity.DisplayForm):
    grok.context(IOrderEntry)
    grok.require('zope2.View')
    grok.template('orderentry_view')
    grok.name('view')

