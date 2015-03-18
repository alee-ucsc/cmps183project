# coding: utf8
from datetime import datetime
import re
import unittest

# Format for wiki links.
RE_LINKS = re.compile('(<<)(.*?)(>>)')

db.define_table('farmtable',
                Field('title'),
                )

db.define_table('farm',
                Field('farm_id', 'reference farmtable'),
                Field('phone'),
                Field('address'),
                Field('email'),
                Field('date_posted', 'datetime'),
                Field('body', 'text'),
                Field('products', 'text'),
                Field('locations', 'text'),
                Field('bkg_image', 'upload'),
                Field('prf_image', 'upload'),
                )

db.farm.id.readable = False
db.farm.farm_id.writable = db.farm.farm_id.readable = False
db.farm.phone.requires = IS_MATCH('^1?((-)\d{3}-?|\(\d{3}\))\d{3}-?\d{4}$',
                                  error_message='Must be of following format: 1(234)5678910')
db.farm.email.requires = IS_EMAIL()
db.farm.date_posted.default = datetime.utcnow()
db.farm.date_posted.writable = db.farm.date_posted.readable = False
db.farm.body.label = 'Content'
db.farm.bkg_image.label = ''
db.farm.prf_image.label = ''

def create_wiki_links(s):
    """This function replaces occurrences of '<<polar bear>>' in the 
    wikitext s with links to default/page/polar%20bear, so the name of the 
    page will be urlencoded and passed as argument 1."""
    def makelink(match):
        # The tile is what the user puts in
        title = match.group(2).strip()
        # The page, instead, is a normalized lowercase version.
        page = title.lower()
        return '[[%s %s]]' % (title, URL('default', 'index', args=[page]))
    return re.sub(RE_LINKS, makelink, s)

def represent_wiki(s):
    """Representation function for wiki pages.  This takes a string s
    containing markup language, and renders it in HTML, also transforming
    the <<page>> links to links to /default/index/page"""
    return MARKMIN(create_wiki_links(s))

def represent_content(v, r):
    """In case you need it: this is similar to represent_wiki, 
    but can be used in db.table.field.represent = represent_content"""
    return represent_wiki(v)

# We associate the wiki representation with the body of a revision.
db.farm.body.represent = represent_content
