from collective.grok import gs
from kagenomise.orders import MessageFactory as _

@gs.importstep(
    name=u'kagenomise.orders', 
    title=_('kagenomise.orders import handler'),
    description=_(''))
def setupVarious(context):
    if context.readDataFile('kagenomise.orders.marker.txt') is None:
        return
    portal = context.getSite()

    # do anything here
