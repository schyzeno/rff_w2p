# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------
from rff import Rff
from gluon.contrib.appconfig import AppConfig
# ---- example index page ----
def index():
    r = Rff()
    r.loadAppConfig()
    myconf = AppConfig(reload=False)
    client_id = myconf.take('app.clientid')
    client_secret = myconf.take('app.clientsecret')
    STATE = r.credentials['clientid']
    session.state = STATE
    host = 'http://127.0.0.1:8000'
    auth_url = 'https://www.reddit.com/api/v1/authorize?client_id='+client_id+'&response_type=code&state='+STATE+'&redirect_uri='+host+URL('friends')+'&duration=temporary&scope=mysubreddits'
    return dict(auth_link=A('authorize',_href=auth_url))

def friends():
    code = request.vars.code
    state = request.vars.state
    error = request.vars.error
    if error or (state != session.state):
        code = 'Access Denied'
    return dict(code=code, state=state, error=error)

# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
