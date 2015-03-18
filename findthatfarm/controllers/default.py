# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

import logging

def index():
    title = request.args(0) or 'Find That Farm'
    content = form = ''
    editing = request.vars.edit == 'true'
    display_title = title.title()

    page = db(db.farmtable.title == title).select().first()
    if page is not None:
        code = db(db.farm.farm_id == page).select(orderby=~db.farm.date_posted).first()
        if code is not None:
            form = SQLFORM(db.farm, record=code, upload=URL('download'), readonly=True)
        else:
            form = 'This farm is not in our DB!'
    content = form
    return dict(display_title=display_title, title=title, content=content, editing=editing, page=page)

@auth.requires_login()
def edit():
    title = request.args(0) or ''
    form = None
    content = None
    display_title = title.title()

    page = db(db.farmtable.title == title).select().first()
    if page is None:
        db.farmtable.insert(title=title)
        page = db(db.farmtable.title == title).select().first()
    code = db(db.farm.farm_id == page).select(orderby=~db.farm.date_posted).first()

    editing = request.vars.edit == 'true'
    if editing:
        if code is not None:
            form = SQLFORM(db.farm, record=code, upload=URL('download'))
        else:
            form = SQLFORM(db.farm)
        form.add_button('Cancel', URL('default', 'index', args=[title]))
        if form.process().accepted:
            db.farm.insert(farm_id=page,
                           phone=form.vars.phone,
                           address=form.vars.address,
                           email=form.vars.email,
                           body=form.vars.body,
                           products=form.vars.products,
                           locations=form.vars.locations,
                           date_posted = datetime.utcnow(),
                           bkg_image=form.vars.bkg_image,
                           prf_image=form.vars.prf_image,
                           )
            redirect(URL('default', 'index', args=[title]))
        content = form

    return dict(display_title=display_title, content=content, editing=editing)

def all():
    page_entries = db().select(db.farmtable.ALL, orderby=db.farmtable.title)
    return dict(page_entries=page_entries)

def search():
    search_word = request.vars.search
    search_pages = []
    if search_word is not None:
        all_pages = db().select(db.farmtable.ALL, orderby=db.farmtable.title)
        for page in all_pages:
            if (search_word.lower() in repr(page.title).lower()):
                search_pages.append(page)
    return dict(search_word=search_word, search_pages=search_pages)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
