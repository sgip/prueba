from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref, relationship
from sqlalchemy.types import Integer, String, Text, Date
from prueba.model import DeclarativeBase, metadata, DBSession


#class Usuario(DeclarativeBase):
#    __tablename__ = 'usuario'
#    #column definitions
#    codusuario = Column(u'codusuario', Integer, primary_key=True)
#    nombre = Column(u'nombre', String(20), nullable=False)
#    apellido = Column(u'apellido', String(20), nullable=False)
#    contrasena = Column(u'contrasena', String(30), nullable=False)
#    telefono = Column(u'telefono', String(15), nullable=False)
#    direccion = Column(u'direccion', String(30), nullable=False)
#    email = Column(u'email', String(30), nullable=False)

#class Rol(DeclarativeBase):
#    __tablename__ = 'rol'
    #column definitions
#    codrol = Column(u'codrol', Integer, primary_key=True)
#    nombre = Column(u'nombre', String(20), nullable=False)   
#    descripcion = Column(u'descripcion', String(100), nullable=True)

class Proyecto(DeclarativeBase):
    __tablename__ = 'proyecto'
    #column definitions
    codproyecto = Column(u'codproyecto', Integer, primary_key=True)
    nombre = Column(u'nombre', String(20), nullable=False)
    estado = Column(u'estado', String(10), nullable=False)
    fecha = Column(u'fecha', Date, nullable=False)
    cantfases = Column(u'cantfases', Integer)
    def __repr__(self):
        return ('<Proyecto: id=%r, nombre=%r, estado=%r, fases=%r' % (
                self.codproyecto, self.nombre, self.estado, self.fases)).encode('utf-8')
    def __unicode__(self):
        return self.nombre

class Fase(DeclarativeBase):
    __tablename__ = 'fase'
    #column definitions
    codfase = Column(u'codfase', Integer, primary_key=True)
    codproyecto = Column(u'codproyecto', Integer, ForeignKey('proyecto.codproyecto'), nullable=False)
    #proyecto = relationship('Proyecto', backref='fases')
    proyecto = relation('Proyecto', backref='fases')
    nombre = Column(u'nombre', String(20), nullable=False)
    descripcion = Column(u'descripcion', String(100))
    estado = Column(u'estado', String(10), nullable=False)
    fecha = Column(u'fecha', Date, nullable=False)
    orden = Column(u'orden', Integer)
    def __repr__(self):
        return ('<Fase: id=%r, name=%r, descripcion=%r' % (
               self.codfase, self.nombre, self.descripcion)).encode('utf-8')
    def __unicode__(self):
        return self.nombre

class Lineabase(DeclarativeBase):
    __tablename__ = 'lineabase'
    #column definitions
    codlineabase = Column(u'codlineabase', Integer, primary_key=True)
    codfase = Column(u'codfase', Integer, ForeignKey('fase.codfase'))
    descripcion = Column(u'descripcion', String(100), nullable=True)
    estado = Column(u'estado', String(10), nullable=False)

class Tipoitem(DeclarativeBase):
    __tablename__ = 'tipoitem'
    #column definitions
    codtipoitem = Column(u'codtipoitem', Integer, primary_key=True)
    codfase = Column(u'codfase', Integer, ForeignKey('fase.codfase'), nullable=True)
    fase = relation('Fase', backref="tipos_de_items")
    nombre = Column(u'nombre', String(20), nullable=False)

class Item(DeclarativeBase):
    __tablename__ = 'item'
    #column definitions
    coditem = Column(u'coditem', Integer, primary_key=True)
    nombre = Column(u'nombre', String(20), nullable=False)
    complejidad = Column(u'complejidad', Integer, nullable=False)
    prioridad = Column(u'prioridad', Integer, nullable=False)
    version = Column(u'version', Integer, nullable=False)
    estado = Column(u'estado', String(10), nullable=False)
    fecha = Column(u'fecha', Date, nullable=False)
    codtipoitem = Column(u'tipoitem', Integer, ForeignKey('tipoitem.codtipoitem'))
    tipoitem = relation('Tipoitem', backref='items')
    codfase = Column(u'fase', Integer, ForeignKey('fase.codfase'))
    fase = relation('Fase', backref='items')

class ArchivoExterno(DeclarativeBase):
    __tablename__ = 'archivo_externo'
    #column definitions
    codarchivo = Column(u'codarchivo', Integer, primary_key=True)
    descripcion = Column(u'descripcion', String(100), nullable=False)
    vinculo = Column(u'vinculo', String(20), nullable=False)

class Atributo(DeclarativeBase):
    __tablename__ = 'atributo'
    #column definitions
    codatributo = Column(u'codatributo', Integer, primary_key=True)
    codcampo = Column(u'codcampo', Integer, nullable=False)
    coditem = Column(u'coditem', Integer, ForeignKey('item.coditem'), nullable=False)
    valoratributo = Column(u'valoratributo', String(20), nullable=False)

class Campo(DeclarativeBase):
    __tablename__ = 'campo'
    #column definitions
    codcampo = Column(u'codcampo', Integer, primary_key=True)
    codtipoitem = Column(u'codtipoitem', Integer, ForeignKey('tipoitem.codtipoitem'), nullable=False)
    tipoitem = relation('Tipoitem', backref="campos")
    nombre = Column(u'nombre', String(15), nullable=False)
    tipo = Column(u'tipo', String(10), nullable=False)

class HistorialItem(DeclarativeBase):
    __tablename__ = 'historial_item'
    #column definitions
    codhistorial = Column(u'codhistorial', Integer, primary_key=True)
    codlineabase = Column(u'codlineabase', Integer, ForeignKey('lineabase.codlineabase'))
    descripcion = Column(u'descripcion', String(100), nullable=False)
    fechacreacion = Column(u'fechacreacion', Date, nullable=False)
    fechamodificacion = Column(u'fechamodificacion', Date, nullable=False)

class HistorialLineabase(DeclarativeBase):
    __tablename__ = 'historial_lineabase'
    #column definitions
    cod_lineabase = Column(u'cod_lineabase', Integer, ForeignKey('lineabase.codlineabase'), nullable=False)
    codhistorial = Column(u'codhistorial', Integer, primary_key=True, nullable=False)
    descripcion = Column(u'descripcion', String(100), nullable=True)
    fecha = Column(u'fecha', Date, nullable=False)

class Relacion(DeclarativeBase):
    __tablename__ = 'relacion'
    #column definitions
    coditemfin = Column(u'coditemfin', Integer, ForeignKey('item.coditem'), nullable=False)
    #itemfin = relation('Item', backref='relaciones_fin')
    coditeminicio = Column(u'coditeminicio', Integer, ForeignKey('item.coditem'), nullable=False)
    #iteminicio = relation('Item', backref='relaciones_inicio')
    codrelacion = Column(u'codrelacion', Integer, primary_key=True)
    tipo = Column(u'tipo', String(20), nullable=False)

#class Permiso(DeclarativeBase):
#    __tablename__ = 'permiso'
    #column definitions
#    codpermiso = Column(u'codpermiso', Integer, primary_key=True)
#    descripcion = Column(u'descripcion', String(100), nullable=True)
#    nombre = Column(u'nombre', String(20), nullable=False)

#class UsuarioRolProyecto(DeclarativeBase):
#    __table__ = 'usuario_rol_proyecto'

#usuario_rol = Table(u'usuario_rol', metadata,
#    Column(u'codigousuario', Integer, ForeignKey('usuario.codusuario'), primary_key=True, nullable=False),
#    Column(u'codigorol', Integer, ForeignKey('rol.codrol'), primary_key=True, nullable=False),
#)

item_proyecto = Table(u'item_proyecto', metadata,
    Column(u'coditem', Integer, ForeignKey('item.coditem'), primary_key=True, nullable=False),
    Column(u'codproyecto', Integer, ForeignKey('proyecto.codproyecto'), primary_key=True, nullable=False),
)

#usuario_rol_proyecto = Table(u'usuario_rol_proyecto', metadata,
#    Column(u'codusuario', Integer, ForeignKey('usuario.codusuario'), primary_key=True, nullable=False),
#    Column(u'codproyecto', Integer, ForeignKey('proyecto.codproyecto'), primary_key=True, nullable=False),
#    Column(u'codrol', Integer, ForeignKey('rol.codrol'), primary_key=True, nullable=False),
#)

#permiso_fase = Table(u'permiso_fase', metadata,
#    Column(u'codpermiso', Integer, ForeignKey('permiso.codpermiso'), primary_key=True, nullable=False),
#    Column(u'codfase', Integer, ForeignKey('fase.codfase'), primary_key=True, nullable=False),
#)

#permiso_rol = Table(u'permiso_rol', metadata,
#    Column(u'codigorol', Integer, ForeignKey('rol.codrol'), primary_key=True, nullable=False),
#    Column(u'codigopermiso', Integer, ForeignKey('permiso.codpermiso'), primary_key=True, nullable=False),
#)

