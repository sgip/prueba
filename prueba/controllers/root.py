# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect, tmpl_context, validate
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController
from repoze.what import predicates

from prueba.lib.base import BaseController
from prueba.model import DBSession, metadata
from prueba.model import User, Group, Permission, Proyecto, Fase, Tipoitem, Campo, Item, Relacion
from prueba import model
from prueba.controllers.secure import SecureController
from prueba.widgets.rol_form import crear_rol_form, editar_rol_form
from prueba.widgets.usuario_form import crear_usuario_form
from prueba.widgets.proyecto_form import crear_proyecto_form
from prueba.widgets.fase_form import crear_fase_form
from prueba.widgets.campo_form import crear_campo_form
from tw.forms.validators import NotEmpty, Int

from prueba.controllers.error import ErrorController
from repoze.what.predicates import not_anonymous
from repoze.what.predicates import Any, is_user, has_permission
from prueba.lib.authz import user_can_edit

from tgext.crud import CrudRestController
from sprox.tablebase import TableBase
from sprox.fillerbase import TableFiller
from sprox.formbase import EditableForm
from sprox.fillerbase import EditFormFiller

__all__ = ['RootController']

#Rol
class RolTable(TableBase):
    __model__ = Group
rol_table = RolTable(DBSession)

class RolTableFiller(TableFiller):
    __model__ = Group
rol_table_filler = RolTableFiller(DBSession)

class RolEditForm(EditableForm):
    __model__= Group
rol_edit_form = RolEditForm(DBSession)

class RolEditFiller(EditFormFiller):
    __model__ = Group
rol_edit_filler = RolEditFiller(DBSession)

class RolController(CrudRestController):
    model = Group
    table = rol_table
    table_filler = rol_table_filler
    new_form = crear_rol_form
    edit_filler = rol_edit_filler
    edit_form = rol_edit_form

#Usuario
class UserTable(TableBase):
    __model__ = User
    __omit_fields__ = ['_password']
user_table = UserTable(DBSession)

class UserTableFiller(TableFiller):
    __model__ = User
user_table_filler = UserTableFiller(DBSession)

class UserEditForm(EditableForm):
    __model__= User
    __omit_fields__ = ['_password']
user_edit_form = UserEditForm(DBSession)

class UserEditFiller(EditFormFiller):
    __model__ = User
user_edit_filler = UserEditFiller(DBSession)

class UserController(CrudRestController):
    model = User
    table = user_table
    table_filler = user_table_filler
    new_form = crear_usuario_form
    edit_filler = user_edit_filler
    edit_form = user_edit_form

#Proyecto
class ProyectoTable(TableBase):
    __model__ = Proyecto
proyecto_table = ProyectoTable(DBSession)

class ProyectoTableFiller(TableFiller):
    __model__ = Proyecto
proyecto_table_filler = ProyectoTableFiller(DBSession)

class ProyectoEditForm(EditableForm):
    __model__= Proyecto
proyecto_edit_form = ProyectoEditForm(DBSession)

class ProyectoEditFiller(EditFormFiller):
    __model__ = Proyecto
proyecto_edit_filler = ProyectoEditFiller(DBSession)

class ProyectoController(CrudRestController):
    model = Proyecto
    table = proyecto_table
    table_filler = proyecto_table_filler
    new_form = crear_proyecto_form
    edit_filler = proyecto_edit_filler
    edit_form = proyecto_edit_form


class RootController(BaseController):
    """
    The root controller for the prueba application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()

    admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    usuarios = UserController(DBSession)
    roles = RolController(DBSession)
    proyectos = ProyectoController(DBSession)

    @expose('prueba.templates.index')
    def index(self):
        """Handle the front-page."""
	op = ('roles', 'usuarios', 'proyectos')
        return dict(page='index', opciones=op)

    #################### INICIO_ROLES ####################
    ##### Crear rol
    @expose('prueba.templates.rol_form')
    @require(not_anonymous(msg='Debe estar logueado'))
    @require(Any(has_permission('crear_rol'), msg='Solo los usuarios con permisos pueden crear roles'))
    def NuevoRol(self, **kw):
    	"""Show form to add new movie data record."""
    	tmpl_context.form = crear_rol_form
    	return dict(modelname='Rol', value=kw)

    ##### Crear rol
    #@expose('prueba.templates.rol_edit_form')
    #def editar_rol(self, rol_id, **kw):
    #	tmpl_context.form = editar_rol_form
    #	rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
    #	value = {'nombre':"", 'description':""}
    #	value['nombre']=rol.group_name
    #	value['descripcion']=rol.group_description
    #	return dict(modelname='Rol', value=value)

    @validate(crear_rol_form, error_handler=NuevoRol)
    @expose()
    def crearRol(self, **kw):
    	rol = Group()
	rol.group_name = kw['nombre']
	rol.group_description = kw['descripcion']
    	DBSession.add(rol)
	#Agregar los permisos
	permisos = kw[u'permiso']
	for permiso_id in permisos:
	    permiso = DBSession.query(Permission).filter_by(permission_id=permiso_id).one()
            permiso.groups.append(rol)
	# Se crean los permisos de consulta, edicion y eliminacion de este rol
	
	rol = DBSession.query(Group).filter_by(group_name=kw['nombre']).one()
	
	permiso_consultar = Permission()
	permiso_consultar.permission_name='ConsultarRol' + str(rol.group_id)
	DBSession.add(permiso_consultar)

	permiso_editar = Permission()
	permiso_editar.permission_name='EditarRol' + str(rol.group_id)
	DBSession.add(permiso_editar)
	
	permiso_eliminar = Permission()
	permiso_eliminar.permission_name='EliminarRol' + str(rol.group_id)
	DBSession.add(permiso_eliminar)

	#grupo = DBSession.query(Group).filter_by(group_id='2').one()
	#permiso_editar.groups.append(grupo)
	#permiso_eliminar.groups.append(grupo)

	#Agregar los permisos de consulta, edicion y eliminacion al rol por defecto del usuario creador del rol
	identity = request.environ['repoze.who.identity']
	usuario_creador_de_usuario = identity['user']
	rol = DBSession.query(Group).filter_by(group_name='RolPorDefecto' + str(usuario_creador_de_usuario.user_id)).one()
	rol.permissions.append(permiso_consultar)
	rol.permissions.append(permiso_editar)
	rol.permissions.append(permiso_eliminar)
	flash("El rol fue creado con exito")
    	redirect("ListarRoles")

    @expose('prueba.templates.editar_rol')
    def EditarRol(self, rol_id, **kw):
	rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
	permisos_del_rol = rol.permissions #Permisos del rol
	todos_los_permisos = DBSession.query(Permission).all() #Todos los permisos de la BD
	return dict(page='Edicion de roles', rol_id=rol_id, rol=rol, pdr= permisos_del_rol, tlp=todos_los_permisos, value=kw)

    @expose()
    @validate({"nombre": NotEmpty()}, error_handler=EditarRol)
    def editarRol(self, rol_id, nombre, descripcion, permisos=None, **kw):
	rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
	rol.group_name = nombre
	rol.group_description = descripcion
	
	if permisos is not None:
		if not isinstance(permisos, list):
			permisos = [permisos]
		permisos = [DBSession.query(Permission).get(permiso) for permiso in permisos]
	else:
		permisos=list()
	rol.permissions = permisos
	DBSession.flush()
	flash("El rol fue actualizado con exito")
	redirect("/ListarRoles")

    @expose()
    def EliminarRol(self, rol_id, **kw):
	DBSession.delete(DBSession.query(Group).get(rol_id))
	#DBSession.query(Permission).filter_by(permission_name=('EditarRol' + rol_id)).one()
	DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('ConsultarRol' + rol_id)).one())
	DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EditarRol' + rol_id)).one())
	DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EliminarRol' + rol_id)).one())
	redirect("/ListarRoles")

    @expose('prueba.templates.listar_roles')
    def ListarRoles(self, **kw):
    	roles = DBSession.query(Group).order_by(Group.group_id)
	### Para determinar si el usuario actualmente loggeado tiene permiso para crear nuevos roles
	permiso_para_crear = has_permission('crear_rol')
	### Para determinar si el usuario actualmente loggeado tiene permiso para editar roles existentes
	r=list()
	editar=list()
	identity = request.environ['repoze.who.identity']
	usuario = identity['user']
	cant=0
	for rol in roles:
		permiso = 'ConsultarRol' + str(rol.group_id)
		if has_permission(permiso):
			r.append(rol)
		permiso = 'EditarRol' + str(rol.group_id)
		if has_permission(permiso):
			editar.append(True)
		else:
			editar.append(False)
		cant = cant +1
		#can_edit = has_permission(permiso)
		#print can_edit
		#checker = user_can_edit(rol.group_id)
		#can_edit = checker.is_met(request.environ)
		#if can_edit != Nonw
		#	my_list.append(True)
		#if can_edit == None
		#	my_list.append(False)
	print type(roles)
	print type(r)
	## Paginacion
	from webhelpers import paginate
	count = cant
	page = int(kw.get('page', '1'))
	currentPage = paginate.Page(r, page, item_count=count, items_per_page=5,)
	r = currentPage.items
	
	
	return dict(page='Listado de Roles', roles=r, currentPage = currentPage, p=permiso_para_crear, editar=editar)
    #################### FIN_ROLES ####################

    #################### INICIO_USUARIOS ####################
    ### Crear usuario
    @expose('prueba.templates.usuario_form')
    @require(not_anonymous(msg='Debe estar logueado'))
    @require(Any(has_permission('crear_usuario'), msg='Solo los usuarios con permisos pueden crear usuarios'))
    def NuevoUsuario(self, **kw):
    	"""Show form to add new movie data record."""
    	tmpl_context.form = crear_usuario_form
    	return dict(modelname='Usuario', value=kw)

    @validate(crear_usuario_form, error_handler=NuevoUsuario)
    @expose()
    def crearUsuario(self, **kw):
    	usuario = User()
	usuario.user_name = kw['nombre']
	usuario.user_fullname = kw[u'apellido']
	usuario.password = kw[u'contrasena']
	usuario.user_telefono = kw[u'telefono']
	usuario.user_direccion = kw[u'direccion']
	usuario.email_address = kw[u'email']
	DBSession.add(usuario)
	#Agregar los roles
	roles = kw[u'rol']
	for rol_id in roles:
	    rol = DBSession.query(Group).filter_by(group_id=rol_id).one()
            rol.users.append(usuario)
	#Crear el rol por defecto para este usuario
	rol_por_defecto = Group()
	rol_por_defecto.group_name = 'RolPorDefecto' + str(usuario.user_id)
	DBSession.add(rol_por_defecto)
	rol_por_defecto.users.append(usuario) #Asociar el rol por defecto con el usuario
	# Se crean los permisos de consulta, edicion y eliminacion de este usuario
	permiso_consultar = Permission()
	permiso_consultar.permission_name='ConsultarUsuario' + str(usuario.user_id)
	DBSession.add(permiso_consultar)
	permiso_editar = Permission()
	permiso_editar.permission_name='EditarUsuario' + str(usuario.user_id)
	DBSession.add(permiso_editar)
	permiso_eliminar = Permission()
	permiso_eliminar.permission_name='EliminarUsuario' + str(usuario.user_id)
	DBSession.add(permiso_eliminar)
	#Asociar el rol por defecto con el usuario
	#rol_por_defecto.users.append(usuario)
	#rol_por_defecto.permissions.append()
	#Agregar los permisos de consulta, edicion y eliminacion al rol por defecto del usuario creador de usuario
	identity = request.environ['repoze.who.identity']
	usuario_creador_de_usuario = identity['user']
	rol = DBSession.query(Group).filter_by(group_name='RolPorDefecto' + str(usuario_creador_de_usuario.user_id)).one()
	rol.permissions.append(permiso_consultar)
	rol.permissions.append(permiso_editar)
	rol.permissions.append(permiso_eliminar)
	#Asignarle al usuario recien creado el permiso de consulta de sus datos
	rol_por_defecto.permissions.append(permiso_consultar)
    	flash("El usuario fue creado satisfactoriamente")
    	redirect("NuevoUsuario")

    @expose('prueba.templates.editar_usuario')
    def EditarUsuario(self, usuario_id, **kw):
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	roles_del_usuario = usuario.groups #Roles del usuario
	todos_los_roles = DBSession.query(Group).all() #Todos los roles de la BD
	return dict(page='Edicion de usuarios', usuario_id=usuario_id, usuario=usuario, rdu= roles_del_usuario, tlr=todos_los_roles, value=kw)

    @expose()
    @validate({"username": NotEmpty(), "contrasena": NotEmpty(), "nombre_completo": NotEmpty(), "telefono": NotEmpty(), "direccion": NotEmpty(), "email": NotEmpty()}, error_handler=EditarUsuario)
    def editarUsuario(self, usuario_id, username, contrasena, nombre_completo, telefono, direccion, email, roles=None, **kw):
	usuario = DBSession.query(User).filter_by(user_id=usuario_id).one()
	usuario.user_name = username
	usuario.password = contrasena
	usuario.user_fullname = nombre_completo
	usuario.user_telefono = telefono
	usuario.user_direccion = direccion
	usuario.email_address = email
		
	if roles is not None:
		if not isinstance(roles, list):
			roles = [roles]
		roles = [DBSession.query(Group).get(rol) for rol in roles]
	else:
		roles=list()
	usuario.groups = roles 
	DBSession.flush()
	flash("El usuario fue actualizado con exito")
	redirect("/ListarUsuarios")

    @expose()
    def EliminarUsuario(self, usuario_id, **kw):
	DBSession.delete(DBSession.query(User).get(usuario_id))
	DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('ConsultarUsuario' + usuario_id)).one())
	DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EditarUsuario' + usuario_id)).one())
	DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EliminarUsuario' + usuario_id)).one())
	DBSession.delete(DBSession.query(Group).filter_by(group_name=('RolPorDefecto' + usuario_id)).one())
	redirect("/ListarUsuarios")

    @expose('prueba.templates.listar_usuarios')
    def ListarUsuarios(self, **kw):
    	usuarios = DBSession.query(User).order_by(User.user_id)
	## Paginacion
	from webhelpers import paginate
	count = usuarios.count()
	page = int(kw.get('page', '1'))
	currentPage = paginate.Page(usuarios, page, item_count=count, items_per_page=5,)
	usuarios = currentPage.items
	### Para determinar si el usuario actualmente loggeado tiene permiso para crear nuevos roles
	permiso_para_crear = has_permission('crear_usuario')
	### Para determinar si el usuario actualmente loggeado tiene permiso para editar roles existentes
	return dict(page='Listado de Usuarios', usuarios=usuarios, currentPage = currentPage, p=permiso_para_crear)
    #################### FIN_USUARIOS ####################

    #################### INICIO_PROYECTOS ####################
    ### Crear proyecto
    @expose('prueba.templates.proyecto_form')
    def NuevoProyecto(self, **kw):
	tmpl_context.form = crear_proyecto_form
    	return dict(modelname='Proyecto', value=kw)

    @validate(crear_proyecto_form, error_handler=NuevoProyecto)
    @expose()
    def crearProyecto(self, **kw):
    	proyecto = Proyecto()
	proyecto.nombre = kw['nombre']
	proyecto.estado = 'definicion'
	proyecto.fecha = kw['fecha']
	DBSession.add(proyecto)
	proyecto = DBSession.query(Proyecto).filter_by(nombre=kw['nombre']).one()
	# Se crean los permisos de consulta, edición y eliminación del proyecto
	permiso_consultar = Permission()
	permiso_consultar.permission_name='ConsultarProyecto' + str(proyecto.codproyecto)
	DBSession.add(permiso_consultar)
	permiso_editar = Permission()
	permiso_editar.permission_name='EditarProyecto' + str(proyecto.codproyecto)
	DBSession.add(permiso_editar)
	permiso_eliminar = Permission()
	permiso_eliminar.permission_name='EliminarProyecto' + str(proyecto.codproyecto)
	DBSession.add(permiso_eliminar)
	permiso_definir_fases = Permission()
	permiso_definir_fases.permission_name='DefinirFases' + str(proyecto.codproyecto)
	DBSession.add(permiso_definir_fases)
	#Agregar los permisos de consulta, edicion y eliminacion al rol por defecto del usuario creador de proyecto
	identity = request.environ['repoze.who.identity']
	usuario_creador_de_proyecto = identity['user']
	rol = DBSession.query(Group).filter_by(group_name='RolPorDefecto' + str(usuario_creador_de_proyecto.user_id)).one()
	rol.permissions.append(permiso_consultar)
	rol.permissions.append(permiso_editar)
	rol.permissions.append(permiso_eliminar)
	rol.permissions.append(permiso_definir_fases)
	flash("El proyecto fue creado con exito")
    	redirect("ListarProyectos")

    @expose('prueba.templates.definir_fases')
    def DefinirFases(self, proyecto_id, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	fases = list()
	#for fase in proyecto.fases:
	#	fases.append(int(fase.codfase));
	#print proyecto.nombre
	#print proyecto.codproyecto
	#print proyecto.estado
	#print proyecto.fecha
	#print proyecto.fases
	#print type(proyecto.fases)
	fases = proyecto.fases
	if not isinstance(fases, list):
		fases = [fases]
	return dict(page='Definicion de fases', proyecto_id=proyecto_id, proyecto=proyecto, fases=fases, value=kw)

    @expose('')
    def IniciarProyecto(self, proyecto_id, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	proyecto.cantfases=len(proyecto.fases)
	proyecto.estado="desarrollo"
	fases = DBSession.query(Fase).filter_by(codproyecto=proyecto_id).order_by(Fase.codfase).all()
	i=1
	for fase in fases:
		fase.orden=i;
		if i==1:
			fase.estado="desarrollo"
		else:
			fase.estado="inicial"
		i=i+1
	DBSession.flush()
	redirect("/ListarProyectos")

    @expose('prueba.templates.ingresar_proyecto')
    def IngresarProyecto(self, proyecto_id, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	fases = proyecto.fases
	if not isinstance(fases, list):
		fases = [fases]
	return dict(modelname='Proyecto', proyecto=proyecto, fases=fases, value=kw)

    @expose('prueba.templates.ingresar__proyecto')
    def Ingresar_Proyecto(self, proyecto_id, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	fases = proyecto.fases
	if not isinstance(fases, list):
		fases = [fases]
	return dict(modelname='Proyecto', proyecto=proyecto, fases=fases, value=kw)

    @expose()
    def EliminarProyecto(self, proy_id, **kw):
	proyecto = DBSession.query(Proyecto).get(proy_id)
	fases = proyecto.fases
	if not isinstance(fases, list):
		fases = [fases]
	for fase in fases:
		DBSession.delete(fase)	
	DBSession.delete(DBSession.query(Proyecto).get(proy_id))
	DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('ConsultarProyecto' + proy_id)).one())
	DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EditarProyecto' + proy_id)).one())
	DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EliminarProyecto' + proy_id)).one())
	redirect("/ListarProyectos/")

    @expose('prueba.templates.listar_proyectos')
    def ListarProyectos(self, **kw):
    	proyectos = DBSession.query(Proyecto).order_by(Proyecto.codproyecto)
	## Paginacion
	from webhelpers import paginate
	count = proyectos.count()
	page = int(kw.get('page', '1'))
	currentPage = paginate.Page(proyectos, page, item_count=count, items_per_page=5,)
	proyectos = currentPage.items
	### Para determinar si el usuario actualmente loggeado tiene permiso para crear nuevos roles
	permiso_para_crear = has_permission('crear_usuario')
	return dict(page='Listado de Proyectos', proyectos=proyectos, currentPage = currentPage, p=permiso_para_crear)  

    #################### INICIO_FASES ####################
    ### Crear fase
    @expose('prueba.templates.crear_fase')
    def NuevaFase(self, proy_id, **kw):
	nombre="" 
	descripcion=""
	if ('nombre' in kw or 'description' in kw):
		nombre=kw['nombre']
		descripcion=kw['descripcion'] 
	return dict(page='Creacion de Fases', proy_id=proy_id, nombre=nombre, descripcion=descripcion, value=kw)

    @expose()
    @validate({"nombre": NotEmpty()}, error_handler=NuevaFase)
    def crearFase(self, proy_id, **kw):
	fase = Fase()
	fase.nombre = kw['nombre']
	fase.descripcion = kw['descripcion']
	fase.estado = "definicion"
	import datetime
	fase.fecha = datetime.date.today()
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proy_id).one()
	fase.proyecto = proyecto
	proyecto.fases.append(fase)
	#fase.codproyecto=int(proy_id)
	DBSession.add(fase)
	self.CrearTipoItemBasico(proy_id, fase)
    	flash("La fase fue creada con exito")
    	redirect("/DefinirFases/"+proy_id)

    @expose('prueba.templates.ingresar_fase')
    def IngresarFase(self, proyecto_id, fase_id, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
	items = fase.items
	if not isinstance(items, list):
		items = [items]
	return dict(modelname='Proyecto', proyecto=proyecto, fase=fase, items=items, value=kw)
    
    @expose()
    def CrearTipoItemBasico(self, proyecto_id, fase):
	t = Tipoitem()
	t.nombre='Basico'
	t.fase=fase
	c1 = Campo()
	c1.nombre = 'Nombre'
	c1.tipo = 'String'
	c2 = Campo()
	c2.nombre = 'Complejidad'
	c2.tipo = 'Int'
	c3 = Campo()
	c3.nombre = 'Prioridad'
	c3.tipo = 'Int'
	c4 = model.Campo()
	c4.nombre = 'Version'
	c4.tipo = 'Int'
	c5 = model.Campo()
	c5.nombre = 'Estado'
	c5.tipo = 'String'
	c6 = model.Campo()
	c6.nombre = 'Fecha'
	c6.tipo = 'Date'
	t.campos.append(c1)
	t.campos.append(c2)
	t.campos.append(c3)
	t.campos.append(c4)
	t.campos.append(c5)
	t.campos.append(c6)
	DBSession.flush()

    @expose('prueba.templates.editar_fase')
    def EditarFase(self, proyecto_id, fase_id, **kw):
	fase=Fase()
	if ('nombre' in kw or 'description' in kw):
		fase.nombre=kw['nombre']
		fase.descripcion=kw['descripcion'] 
	else:
		fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
	#roles_del_usuario = usuario.groups #Roles del usuario
	#todos_los_roles = DBSession.query(Group).all() #Todos los roles de la BD
	return dict(page='Edicion de fases', fase_id=fase_id, proy_id=proyecto_id, fase=fase, value=kw)

    @expose()
    @validate({"nombre": NotEmpty(),}, error_handler=EditarFase)
    def editarFase(self, proy_id, fase_id, nombre="", descripcion="", **kw):
	fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
	fase.nombre = nombre
	fase.descripcion = descripcion
	DBSession.flush()
	flash("La fase fue actualizada con exito")
	redirect("/DefinirFases/"+proy_id)

    @expose()
    def EliminarFase(self, proy_id, fase_id, **kw):
	DBSession.delete(DBSession.query(Fase).get(fase_id))
	#DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('ConsultarUsuario' + usuario_id)).one())
	#DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EditarUsuario' + usuario_id)).one())
	#DBSession.delete(DBSession.query(Permission).filter_by(permission_name=('EliminarUsuario' + usuario_id)).one())
	#DBSession.delete(DBSession.query(Group).filter_by(group_name=('RolPorDefecto' + usuario_id)).one())
	redirect("/DefinirFases/"+proy_id)

    #################### INICIO_TIPO_ITEMS ####################
    ### Crear Tipo de Ítems
    @expose('prueba.templates.crear_tipoitem')
    def NuevoTipoDeItem(self, proyecto_id, fase_id, **kw):
	#print kw
	#nombre=""
	#atributos=list()	
	#if 'nombre' in kw:
	#	nombre=kw['nombre']
	#if 'atributos' in kw:
	#	if not isinstance(fases, list):
	#		atributos=[atributos]
	#	atributos=atributos
	return dict(page='Creacion de tipos de item', value=kw)
    
    @expose()
    def crearTipoDeItem(self, **kw):
	print kw
	#Fase = Fase()
	#fase.nombre = kw['nombre']
	#fase.descripcion = kw['descripcion']
	#fase.estado = "definicion"
	#import datetime
	#fase.fecha = datetime.date.today()
	#proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proy_id).one()
	#fase.proyecto = proyecto
	#proyecto.fases.append(fase)
	#fase.codproyecto=int(proy_id)
	#DBSession.add(fase)
    	flash("El tipo de item fue creado con exito")
    	#redirect("/NuevoTipoDeItem/"+proyecto_id+fase_id+atributo)

    @expose('prueba.templates.tipos_de_items')
    def TipoDeItem(self, proyecto_id, fase_id, **kw):
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
	fases = proyecto.fases
	if not isinstance(fases, list):
		fases = [fases]
	return dict(page='Tipos de item', proyecto=proyecto, fases=fases, fase=fase, value=kw)

    @expose('prueba.templates.campo_form')
    def NuevoCampo(self, proyecto_id, fase_id, **kw):
    	tmpl_context.form = crear_campo_form
    	return dict(modelname='Campo de Tipo de Item', value=kw)

    @expose('prueba.templates.elegir_tipoitem')
    def ElegirTipoItem(self, proyecto_id, fase_id, **kw):
	tipos_item = DBSession.query(Tipoitem).filter_by(codfase=fase_id).all()
	if not isinstance(tipos_item, list):
		tipos_item = [tipos_item]
	return dict(page='Creacion de Items', proyecto_id=proyecto_id, fase_id=fase_id, tipos_item=tipos_item, value=kw)

    @expose('prueba.templates.crear_item')
    def NuevoItem(self, proyecto_id, fase_id, tipo_item, **kw):
	#en caso de error de validacion al crear item
	if 'nombre' in kw:
		nombre = kw['nombre']
	else:	
		nombre=""
	if 'complejidad' in kw:
		complejidad=kw['complejidad']
	else: 
		complejidad=""
	if 'prioridad' in kw:
		prioridad=kw['prioridad']
	else:
		prioridad=""
	tipoitem = DBSession.query(Tipoitem).filter_by(codtipoitem=tipo_item).one()
	return dict(page='Creacion de Items', proyecto_id=proyecto_id, fase_id=fase_id, tipo_item=tipoitem, nombre=nombre, complejidad=complejidad, prioridad=prioridad, value=kw)

    @expose('')
    @validate({"nombre": NotEmpty(), "complejidad": Int(min=1, max=10), "prioridad": Int(min=1, max=10), }, error_handler=NuevoItem)
    def crearItem(self, proyecto_id, fase_id, tipoitem_id, **kw):
	#print tipoitem_id
	item = Item()
	item.nombre=kw['nombre']
	item.complejidad=kw['complejidad']
	item.prioridad=kw['prioridad']
	item.version=1
	item.estado='desarrollo'
	import datetime
	item.fecha=datetime.date.today()
	tipoitem = DBSession.query(Tipoitem).filter_by(codtipoitem=tipoitem_id).one()
	item.tipoitem = tipoitem
	fase = DBSession.query(Fase).filter_by(codfase=fase_id).one()
	#print fase
	#print item.fase
	item.fase = fase
	#print tipoitem
	DBSession.add(item)
	fase.items.append(item)
	tipoitem.items.append(item)
	redirect("/IngresarFase/"+proyecto_id+"/"+fase_id)

    @expose('prueba.templates.editar_item')
    def ModificarItem(self, proyecto_id, fase_id, item_id, **kw):
	print kw
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	tipoitem = item.tipoitem
	###Listar items de la fase anterior y de la fase posterior
	proyecto = DBSession.query(Proyecto).filter_by(codproyecto=proyecto_id).one()
	orden_fase = item.fase.orden
	orden_izq = orden_fase-1
	orden_der =  orden_fase+1
	items_izq=list()
	items_der=list()
	if orden_fase > 1:
		fase_izq = DBSession.query(Fase).filter_by(codproyecto=proyecto_id).filter_by(orden=orden_izq).one()
		items_izq = fase_izq.items
	if orden_fase < proyecto.cantfases:
		fase_der = DBSession.query(Fase).filter_by(codproyecto=proyecto_id).filter_by(orden=orden_der).one()
		items_der = fase_der.items
	return dict(page='Edicion de Items', proyecto_id=proyecto_id, fase_id=fase_id, item=item, tipoitem=tipoitem, items_izq=items_izq, items_der=items_der, value=kw)

    @expose('')
    @validate({"nombre": NotEmpty(), "complejidad": Int(min=1, max=10), "prioridad": Int(min=1, max=10), }, error_handler=ModificarItem)
    def editarItem(self, proyecto_id, fase_id, item_id, **kw):
	item = DBSession.query(Item).filter_by(coditem=item_id).one()
	item.nombre=kw['nombre']
	item.complejidad=kw['complejidad']
	item.prioridad=kw['prioridad']
	item.version=1
	item.estado='definicion'
	import datetime
	item.fecha=datetime.date.today()
	DBSession.flush()
	##Crear las relaciones
	if 'items_izq' in kw:
		items_izq = kw['items_izq']
		if not isinstance(items_izq, list):
			items_izq = [items_izq]
	else:
		items_izq=list()
	if 'items_der' in kw:
		items_der = kw['items_der']
		if not isinstance(items_der, list):
			items_der = [items_der]
	else:
		items_der=list()
	for item in items_izq:
		relacion = Relacion()
		relacion.coditeminicio= int(item)
		relacion.coditemfin=item_id
		relacion.tipo='antecesor-sucesor'
		DBSession.add(relacion)
	for item in items_der:
		relacion = Relacion()
		relacion.coditeminicio= item_id
		relacion.coditemfin=int(item)
		relacion.tipo='antecesor-sucesor'
		DBSession.add(relacion)
	redirect("/IngresarFase/"+proyecto_id+"/"+fase_id)

    @expose('prueba.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('prueba.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(environment=request.environ)

    @expose('prueba.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(params=kw)

    @expose('prueba.templates.authentication')
    def auth(self):
        """Display some information about auth* on this application."""
        return dict(page='auth')

    @expose('prueba.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('prueba.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('prueba.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from='/'):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login', came_from=came_from, __logins=login_counter)
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
