from five import grok
from plone.directives import dexterity, form

from zope import schema
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from zope.interface import invariant, Invalid

from z3c.form import group, field

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedImage, NamedFile
from plone.namedfile.field import NamedBlobImage, NamedBlobFile

from plone.app.textfield import RichText

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder

from kagenomise.orders import MessageFactory as _


# Interface class; used to define content-type schema.

class IOrderEntry(form.Schema, IImageScaleTraversable):
    """
    
    """

    item_reference = RelationChoice(
        title=_(u'Item'),
        source=ObjPathSourceBinder(),
        required=False
    )

    unit_price = schema.Float(
        title=_(u'Unit Price'),
        default=0.0
    )

    quantity = schema.Int(
        title=_(u'Quantity'),
        default=0
    )
