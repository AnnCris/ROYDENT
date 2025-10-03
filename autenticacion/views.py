"""
Vistas para el sistema de autenticación de Roy Representaciones
Sistema completo con JWT para Bolivia - VERSIÓN CORREGIDA
"""
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Permiso, RolPermiso, Usuario, Persona, Rol, UsuarioRol
from .serializers import (
    LoginSerializer, RegistroSerializer, UsuarioSerializer,
    CambiarPasswordSerializer
)
import re
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from django.db.models import Q

from autenticacion import models

# Vistas web tradicionales
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente')
    return redirect('index')

# Vistas API REST con JWT
class LoginAPIView(APIView):
    """API para login de usuarios con JWT"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            usuario = serializer.validated_data['usuario']
            
            # Actualizar último login
            usuario.ultimo_login = timezone.now()
            usuario.save()
            
            # Generar tokens JWT
            refresh = RefreshToken.for_user(usuario)
            
            # Obtener roles activos del usuario
            roles_activos = usuario.usuario_roles.filter(estado='ACTIVO')
            roles_info = []
            
            for ur in roles_activos:
                roles_info.append({
                    'id': ur.rol.id,
                    'nombre': ur.rol.nombre_rol,
                    'descripcion': ur.rol.descripcion,
                    'sucursal': ur.get_sucursal_asignada()
                })
            
            return Response({
                'message': 'Login exitoso',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'usuario': {
                    'id': usuario.id,
                    'nombre_usuario': usuario.nombre_usuario,
                    'nombre_completo': usuario.get_nombre_completo(),
                    'correo': usuario.persona.correo,
                    'cedula': usuario.persona.cedula_identidad,
                    'celular': usuario.persona.numero_celular,
                    'roles': roles_info,
                    'ultimo_login': usuario.ultimo_login
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Credenciales inválidas',
            'detalles': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)

class RegistroAPIView(APIView):
    """API para registro de nuevos usuarios"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                # Crear usuario
                usuario = serializer.save()
                
                # NUEVO: Crear automáticamente el cliente asociado
                from .models import TipoCliente, Cliente
                
                # Obtener tipo de cliente o usar uno por defecto
                tipo_cliente_id = request.data.get('tipo_cliente_id')
                
                if tipo_cliente_id:
                    tipo_cliente = TipoCliente.objects.get(id=tipo_cliente_id)
                else:
                    # Buscar tipo "Particular" o crear uno por defecto
                    tipo_cliente, _ = TipoCliente.objects.get_or_create(
                        codigo='PARTICULAR',
                        defaults={
                            'nombre_tipo': 'Particular',
                            'descripcion': 'Cliente particular'
                        }
                    )
                
                # Crear el cliente
                Cliente.objects.create(
                    usuario=usuario,
                    tipo_cliente=tipo_cliente,
                    estado='ACTIVO'
                )
                
                # Generar tokens JWT para auto-login
                refresh = RefreshToken.for_user(usuario)
                
                # Obtener información del rol asignado
                rol_usuario = usuario.usuario_roles.filter(estado='ACTIVO').first()
                
                rol_info = None
                if rol_usuario:
                    rol_info = {
                        'nombre': rol_usuario.rol.nombre_rol,
                        'descripcion': rol_usuario.rol.descripcion,
                        'sucursal': rol_usuario.get_sucursal_asignada()
                    }
                
                return Response({
                    'message': 'Usuario y cliente registrados exitosamente',
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'usuario': {
                        'id': usuario.id,
                        'nombre_usuario': usuario.nombre_usuario,
                        'nombre_completo': usuario.get_nombre_completo(),
                        'correo': usuario.persona.correo,
                        'cedula': usuario.persona.cedula_identidad,
                        'rol': rol_info
                    }
                }, status=status.HTTP_201_CREATED)
                
            except TipoCliente.DoesNotExist:
                return Response({
                    'error': 'Tipo de cliente no válido'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'error': 'Error interno del servidor',
                    'detalles': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'error': 'Datos de registro inválidos',
            'detalles': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class PerfilAPIView(APIView):
    """API para obtener y actualizar perfil de usuario"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtener perfil del usuario autenticado"""
        serializer = UsuarioSerializer(request.user)
        return Response({
            'usuario': serializer.data
        })
    
    def put(self, request):
        """Actualizar datos del perfil"""
        usuario = request.user
        persona = usuario.persona
        
        # Actualizar datos de persona
        datos_permitidos = [
            'nombre', 'apellido_paterno', 'apellido_materno',
            'numero_celular', 'correo'
        ]
        
        for campo in datos_permitidos:
            if campo in request.data:
                setattr(persona, campo, request.data[campo])
        
        try:
            persona.full_clean()
            persona.save()
            
            serializer = UsuarioSerializer(usuario)
            return Response({
                'message': 'Perfil actualizado exitosamente',
                'usuario': serializer.data
            })
            
        except Exception as e:
            return Response({
                'error': 'Error al actualizar perfil',
                'detalles': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class CambiarPasswordAPIView(APIView):
    """API para cambiar contraseña"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = CambiarPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Contraseña cambiada exitosamente'
            })
        
        return Response({
            'error': 'Error al cambiar contraseña',
            'detalles': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class RolesUsuarioAPIView(APIView):
    """API para obtener roles disponibles"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Obtener lista de roles disponibles para registro"""
        roles_publicos = Rol.objects.filter(
            nombre_rol__in=['CLIENTE']  # Solo permitir registro como cliente
        )
        
        roles_data = []
        for rol in roles_publicos:
            roles_data.append({
                'id': rol.id,
                'nombre': rol.nombre_rol,
                'descripcion': rol.descripcion
            })
        
        return Response({
            'roles': roles_data
        })

class ValidarUsuarioAPIView(APIView):
    """API para validar disponibilidad de nombre de usuario"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        nombre_usuario = request.data.get('nombre_usuario')
        
        if not nombre_usuario:
            return Response({
                'error': 'Nombre de usuario requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        existe = Usuario.objects.filter(nombre_usuario=nombre_usuario).exists()
        
        return Response({
            'disponible': not existe,
            'nombre_usuario': nombre_usuario
        })

class ValidarCedulaAPIView(APIView):
    """API para validar cédula de identidad"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        cedula = request.data.get('cedula_identidad')
        
        if not cedula:
            return Response({
                'error': 'Cédula de identidad requerida'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Limpiar formato
        cedula_clean = cedula.strip().upper()
        
        # Validar formato
        if not re.match(r'^\d{7,8}(-[A-Z]{1,3})?$', cedula_clean):
            return Response({
                'valida': False,
                'error': 'Formato de cédula inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya existe
        existe = Persona.objects.filter(cedula_identidad=cedula_clean).exists()
        
        return Response({
            'valida': not existe,
            'disponible': not existe,
            'cedula': cedula_clean
        })

class ValidarCorreoAPIView(APIView):
    """API para validar correo electrónico"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        correo = request.data.get('correo')
        
        if not correo:
            return Response({
                'error': 'Correo electrónico requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si ya existe
        existe = Persona.objects.filter(correo=correo).exists()
        
        return Response({
            'disponible': not existe,
            'correo': correo
        })

class EstadisticasAPIView(APIView):
    """API para estadísticas del sistema"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtener estadísticas básicas"""
        # Solo usuarios con rol de administrador pueden ver estadísticas completas
        usuario_admin = request.user.usuario_roles.filter(
            rol__nombre_rol='ADMINISTRADOR',
            estado='ACTIVO'
        ).exists()
        
        if usuario_admin:
            stats = {
                'total_usuarios': Usuario.objects.filter(is_active=True).count(),
                'total_personas': Persona.objects.count(),
                'usuarios_por_rol': {},
                'registros_recientes': Usuario.objects.filter(
                    fecha_creacion__date=timezone.now().date()
                ).count()
            }
            
            # Estadísticas por rol
            for rol in Rol.objects.all():
                count = UsuarioRol.objects.filter(
                    rol=rol, 
                    estado='ACTIVO'
                ).count()
                stats['usuarios_por_rol'][rol.nombre_rol] = count
                
        else:
            # Solo estadísticas básicas para usuarios normales
            stats = {
                'mi_perfil': {
                    'nombre_completo': request.user.get_nombre_completo(),
                    'fecha_registro': request.user.fecha_creacion,
                    'ultimo_login': request.user.ultimo_login
                }
            }
        
        return Response(stats)

class VerificarTokenAPIView(APIView):
    """API para verificar si un token JWT es válido"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Verificar token y retornar información del usuario"""
        usuario = request.user
        
        # Obtener roles activos
        roles_activos = usuario.usuario_roles.filter(estado='ACTIVO')
        roles_info = []
        
        for ur in roles_activos:
            roles_info.append({
                'id': ur.rol.id,
                'nombre': ur.rol.nombre_rol,
                'descripcion': ur.rol.descripcion,
                'sucursal': ur.get_sucursal_asignada()
            })
        
        return Response({
            'valido': True,
            'usuario': {
                'id': usuario.id,
                'nombre_usuario': usuario.nombre_usuario,
                'nombre_completo': usuario.get_nombre_completo(),
                'correo': usuario.persona.correo,
                'roles': roles_info
            }
        })

class RefreshTokenAPIView(APIView):
    """API para refrescar token JWT"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return Response({
                    'error': 'Token de refresh requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear nuevo token de acceso
            refresh = RefreshToken(refresh_token)
            nuevo_access = refresh.access_token
            
            return Response({
                'access': str(nuevo_access)
            })
            
        except Exception as e:
            return Response({
                'error': 'Token de refresh inválido',
                'detalles': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        

# ============ VISTA PARA COMPONENTE SIDEBAR ============
from django.views.generic import TemplateView

class SidebarView(TemplateView):
    """Vista para servir el componente del sidebar"""
    template_name = 'components/sidebar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['usuario'] = self.request.user
            context['roles'] = self.request.user.usuario_roles.filter(estado='ACTIVO')
        return context
    

# ============ CRUD DE USUARIOS - SIN AUTENTICACIÓN ============

from rest_framework.decorators import api_view
from django.db.models import Q

@api_view(['GET'])
def listar_usuarios(request):
    """API para listar usuarios con filtros mejorados"""
    busqueda = request.GET.get('busqueda', '').strip()
    rol = request.GET.get('rol', '').strip()
    estado = request.GET.get('estado', '').strip()
    sucursal = request.GET.get('sucursal', '').strip()

    # Iniciar con todos los usuarios
    usuarios = Usuario.objects.select_related('persona').prefetch_related('usuario_roles__rol')
    
    # Filtro por búsqueda de texto (nombre, usuario, email)
    if busqueda:
        usuarios = usuarios.filter(
            Q(nombre_usuario__icontains=busqueda) |
            Q(persona__nombre__icontains=busqueda) |
            Q(persona__apellido_paterno__icontains=busqueda) |
            Q(persona__apellido_materno__icontains=busqueda) |
            Q(persona__correo__icontains=busqueda)
        )
    
    # Filtro por estado (activo/inactivo)
    if estado and estado != 'todos':
        if estado == 'activo':
            usuarios = usuarios.filter(is_active=True)
        elif estado == 'inactivo':
            usuarios = usuarios.filter(is_active=False)
    
    # Filtro por rol
    if rol and rol != 'todos':
        usuarios = usuarios.filter(
            usuario_roles__rol__nombre_rol=rol,
            usuario_roles__estado='ACTIVO'
        ).distinct()
    
    # Filtro por sucursal
    if sucursal and sucursal != 'todas':
        # Mapeo de sucursales a roles
        if sucursal == 'roydent':
            usuarios = usuarios.filter(
                usuario_roles__rol__nombre_rol='VENDEDOR_ROYDENT',
                usuario_roles__estado='ACTIVO'
            ).distinct()
        elif sucursal == 'mundo_medico':
            usuarios = usuarios.filter(
                usuario_roles__rol__nombre_rol='VENDEDOR_MUNDO_MEDICO',
                usuario_roles__estado='ACTIVO'
            ).distinct()
        elif sucursal == 'deposito':
            usuarios = usuarios.filter(
                usuario_roles__rol__nombre_rol='ADMINISTRADOR',
                usuario_roles__estado='ACTIVO'
            ).distinct()
    
    # Ordenar por fecha de creación descendente
    usuarios = usuarios.order_by('-fecha_creacion')
    
    # Construir respuesta
    usuarios_data = []
    for usuario in usuarios:
        roles = usuario.usuario_roles.filter(estado='ACTIVO')
        roles_info = [
            {
                'id': ur.rol.id,
                'nombre': ur.rol.nombre_rol,
                'descripcion': ur.rol.descripcion,
                'sucursal': ur.get_sucursal_asignada()
            }
            for ur in roles
        ]
        
        usuarios_data.append({
            'id': usuario.id,
            'nombre_usuario': usuario.nombre_usuario,
            'nombre_completo': usuario.get_nombre_completo(),
            'email': usuario.persona.correo,
            'cedula': usuario.persona.cedula_identidad,
            'celular': usuario.persona.numero_celular,
            'roles': roles_info,
            'is_active': usuario.is_active,
            'fecha_creacion': usuario.fecha_creacion,
            'ultimo_login': usuario.ultimo_login,
        })

    return Response({
        'success': True,
        'count': len(usuarios_data),
        'usuarios': usuarios_data
    })

@api_view(['GET'])
def obtener_usuario(request, usuario_id):
    """API para obtener usuario - SIN AUTENTICACIÓN"""
    try:
        usuario = Usuario.objects.select_related('persona').get(id=usuario_id)
        
        roles = usuario.usuario_roles.filter(estado='ACTIVO')
        roles_info = [
            {
                'id': ur.rol.id,
                'nombre': ur.rol.nombre_rol,
                'sucursal': ur.get_sucursal_asignada()
            }
            for ur in roles
        ]
        
        data = {
            'id': usuario.id,
            'nombre_usuario': usuario.nombre_usuario,
            'nombre': usuario.persona.nombre,
            'apellido_paterno': usuario.persona.apellido_paterno,
            'apellido_materno': usuario.persona.apellido_materno,
            'cedula_identidad': usuario.persona.cedula_identidad,
            'numero_celular': usuario.persona.numero_celular,
            'correo': usuario.persona.correo,
            'roles': roles_info,
            'is_active': usuario.is_active,
        }
        
        return Response({
            'success': True,
            'usuario': data
        })
        
    except Usuario.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def crear_usuario(request):
    """API para crear un nuevo usuario"""
    try:
        data = request.data

        # Validar campos requeridos
        campos_requeridos = ['nombre', 'apellido_paterno', 'cedula_identidad', 
                            'correo', 'nombre_usuario', 'password', 'rol']
        for campo in campos_requeridos:
            if not data.get(campo):
                return Response({
                    'success': False,
                    'error': f'El campo {campo} es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si el usuario ya existe
        if Usuario.objects.filter(nombre_usuario=data['nombre_usuario']).exists():
            return Response({
                'success': False,
                'error': 'El nombre de usuario ya existe'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si la cédula ya existe
        if Persona.objects.filter(cedula_identidad=data['cedula_identidad']).exists():
            return Response({
                'success': False,
                'error': 'La cédula de identidad ya está registrada'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si el correo ya existe
        if Persona.objects.filter(correo=data['correo']).exists():
            return Response({
                'success': False,
                'error': 'El correo electrónico ya está registrado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar el rol
        try:
            rol = Rol.objects.get(nombre_rol=data['rol'])
        except Rol.DoesNotExist:
            return Response({
                'success': False,
                'error': f'El rol {data["rol"]} no existe'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear la persona
        persona = Persona.objects.create(
            nombre=data['nombre'],
            apellido_paterno=data['apellido_paterno'],
            apellido_materno=data.get('apellido_materno', ''),
            cedula_identidad=data['cedula_identidad'],
            numero_celular=data.get('numero_celular', ''),
            correo=data['correo']
        )
        
        # Crear el usuario
        usuario = Usuario.objects.create(
            nombre_usuario=data['nombre_usuario'],
            persona=persona,
            is_active=True
        )
        usuario.set_password(data['password'])
        usuario.save()
        
        # Asignar el rol
        UsuarioRol.objects.create(
            usuario=usuario,
            rol=rol,
            estado='ACTIVO'
        )
        
        return Response({
            'success': True,
            'message': 'Usuario creado exitosamente',
            'usuario': {
                'id': usuario.id,
                'nombre_usuario': usuario.nombre_usuario,
                'nombre_completo': usuario.get_nombre_completo()
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error al crear usuario: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PUT'])
def actualizar_usuario(request, usuario_id):
    """API para actualizar un usuario"""
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        persona = usuario.persona
        data = request.data
        
        # Actualizar datos de persona
        if 'nombre' in data:
            persona.nombre = data['nombre']
        if 'apellido_paterno' in data:
            persona.apellido_paterno = data['apellido_paterno']
        if 'apellido_materno' in data:
            persona.apellido_materno = data['apellido_materno']
        if 'numero_celular' in data:
            persona.numero_celular = data['numero_celular']
        if 'correo' in data:
            # Verificar que el correo no esté en uso por otra persona
            if Persona.objects.filter(correo=data['correo']).exclude(id=persona.id).exists():
                return Response({
                    'success': False,
                    'error': 'El correo ya está en uso por otro usuario'
                }, status=status.HTTP_400_BAD_REQUEST)
            persona.correo = data['correo']
        
        persona.save()
        
        # Actualizar contraseña si se proporciona
        if 'password' in data and data['password']:
            usuario.set_password(data['password'])
            usuario.save()
        
        # Actualizar rol si se proporciona
        if 'rol' in data:
            try:
                rol = Rol.objects.get(nombre_rol=data['rol'])
                # Desactivar roles anteriores
                UsuarioRol.objects.filter(usuario=usuario).update(estado='INACTIVO')
                # Crear o actualizar el nuevo rol
                UsuarioRol.objects.update_or_create(
                    usuario=usuario,
                    rol=rol,
                    defaults={'estado': 'ACTIVO'}
                )
            except Rol.DoesNotExist:
                pass
         
        return Response({
            'success': True,
            'message': 'Usuario actualizado exitosamente'
        })
        
    except Usuario.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
def eliminar_usuario(request, usuario_id):
    """API para eliminar usuario - SIN AUTENTICACIÓN"""
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        usuario.is_active = False
        usuario.save()
        
        UsuarioRol.objects.filter(usuario=usuario).update(estado='INACTIVO')
        
        return Response({
            'success': True,
            'message': 'Usuario desactivado exitosamente'
        })
        
    except Usuario.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def activar_usuario(request, usuario_id):
    """API para activar usuario - SIN AUTENTICACIÓN"""
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        usuario.is_active = True
        usuario.save()
        
        return Response({
            'success': True,
            'message': 'Usuario activado exitosamente'
        })
        
    except Usuario.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def estadisticas_usuarios(request):
    """API para estadísticas - SIN AUTENTICACIÓN"""
    stats = {
        'total': Usuario.objects.count(),
        'activos': Usuario.objects.filter(is_active=True).count(),
        'inactivos': Usuario.objects.filter(is_active=False).count(),
        'administradores': UsuarioRol.objects.filter(
            rol__nombre_rol='ADMINISTRADOR',
            estado='ACTIVO'
        ).count(),
        'vendedores': UsuarioRol.objects.filter(
            rol__nombre_rol__in=['VENDEDOR_ROYDENT', 'VENDEDOR_MUNDO_MEDICO'],
            estado='ACTIVO'
        ).count(),
    }
    
    return Response({
        'success': True,
        'estadisticas': stats
    })

# ============ API DE PERMISOS ============

from .models import Permiso, RolPermiso

@api_view(['GET'])
def listar_permisos(request):
    """Listar todos los permisos del sistema"""
    try:
        permisos = Permiso.objects.all().order_by('modulo', 'tipo_permiso')
        
        permisos_data = [
            {
                'id': p.id,
                'nombre_permiso': p.nombre_permiso,
                'codigo_permiso': p.codigo_permiso,
                'modulo': p.modulo,
                'tipo_permiso': p.tipo_permiso,
                'descripcion': p.descripcion
            }
            for p in permisos
        ]
        
        return Response({
            'success': True,
            'count': len(permisos_data),
            'permisos': permisos_data
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def obtener_permisos_usuario(request, usuario_id):
    """Obtener permisos de un usuario específico"""
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        
        # Obtener roles del usuario
        roles_usuario = usuario.usuario_roles.filter(estado='ACTIVO')
        
        # Obtener todos los permisos de esos roles
        permisos_ids = set()
        for ur in roles_usuario:
            rol_permisos = RolPermiso.objects.filter(rol=ur.rol).values_list('permiso_id', flat=True)
            permisos_ids.update(rol_permisos)
        
        permisos = Permiso.objects.filter(id__in=permisos_ids)
        
        permisos_data = [
            {
                'id': p.id,
                'nombre_permiso': p.nombre_permiso,
                'codigo_permiso': p.codigo_permiso,
                'modulo': p.modulo,
                'tipo_permiso': p.tipo_permiso
            }
            for p in permisos
        ]
        
        return Response({
            'success': True,
            'permisos': permisos_data
        })
    except Usuario.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def actualizar_permisos_usuario(request, usuario_id):
    """Actualizar permisos de un usuario"""
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        permisos_ids = request.data.get('permisos', [])
        
        # Obtener el rol principal del usuario
        rol_usuario = usuario.usuario_roles.filter(estado='ACTIVO').first()
        
        if not rol_usuario:
            return Response({
                'success': False,
                'error': 'Usuario sin rol asignado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Eliminar permisos actuales del rol
        RolPermiso.objects.filter(rol=rol_usuario.rol).delete()
        
        # Agregar nuevos permisos
        contador = 0
        for permiso_id in permisos_ids:
            try:
                permiso = Permiso.objects.get(id=permiso_id)
                RolPermiso.objects.create(
                    rol=rol_usuario.rol,
                    permiso=permiso,
                    asignado_por=request.user if request.user.is_authenticated else None
                )
                contador += 1
            except Permiso.DoesNotExist:
                continue
        
        return Response({
            'success': True,
            'message': f'Permisos actualizados: {contador} permisos asignados'
        })
        
    except Usuario.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def matriz_permisos_roles(request):
    """Obtener matriz de permisos por rol"""
    try:
        roles = Rol.objects.all()
        roles_permisos = {}
        
        for rol in roles:
            permisos_ids = RolPermiso.objects.filter(rol=rol).values_list('permiso_id', flat=True)
            roles_permisos[rol.nombre_rol] = list(permisos_ids)
        
        return Response({
            'success': True,
            'roles_permisos': roles_permisos
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# autenticacion/views.py - AGREGAR AL FINAL DEL ARCHIVO EXISTENTE

"""
Views para Clientes y Proveedores
"""
from autenticacion.models import Cliente, Proveedor, TipoCliente
from autenticacion.serializers import (
    ClienteSerializer,
    ClienteCreateSerializer,
    ProveedorSerializer,
    TipoClienteSerializer
)

# ============ TIPOS DE CLIENTE ============

@api_view(['GET'])
def listar_tipos_cliente(request):
    """API para listar tipos de cliente"""
    tipos = TipoCliente.objects.all().order_by('nombre_tipo')
    serializer = TipoClienteSerializer(tipos, many=True)
    
    return Response({
        'success': True,
        'count': len(serializer.data),
        'tipos': serializer.data
    })


# ============ CLIENTES - CRUD ============

@api_view(['GET'])
def listar_clientes(request):
    """API para listar clientes con filtros"""
    tipo_cliente = request.GET.get('tipo_cliente', '').strip()
    estado = request.GET.get('estado', '').strip()
    ciudad = request.GET.get('ciudad', '').strip()
    es_vip = request.GET.get('es_vip', '').strip()
    busqueda = request.GET.get('busqueda', '').strip()
    
    # Base query
    clientes = Cliente.objects.select_related(
        'usuario__persona',
        'tipo_cliente'
    ).all()
    
    # Aplicar filtros
    if tipo_cliente and tipo_cliente != 'todos':
        clientes = clientes.filter(tipo_cliente__codigo=tipo_cliente)
    
    if estado and estado != 'todos':
        clientes = clientes.filter(estado=estado.upper())
    
    if ciudad and ciudad != 'todas':
        clientes = clientes.filter(ciudad__icontains=ciudad)
    
    if es_vip == 'true':
        clientes = clientes.filter(es_vip=True)
    
    # Búsqueda por texto
    if busqueda:
        clientes = clientes.filter(
            Q(usuario__persona__nombre__icontains=busqueda) |
            Q(usuario__persona__apellido_paterno__icontains=busqueda) |
            Q(usuario__persona__apellido_materno__icontains=busqueda) |
            Q(usuario__persona__cedula_identidad__icontains=busqueda) |
            Q(usuario__persona__correo__icontains=busqueda) |
            Q(razon_social__icontains=busqueda) |
            Q(nit__icontains=busqueda)
        )
    
    # Ordenar por fecha de registro descendente
    clientes = clientes.order_by('-fecha_registro')
    
    serializer = ClienteSerializer(clientes, many=True)
    
    return Response({
        'success': True,
        'count': len(serializer.data),
        'clientes': serializer.data
    })


@api_view(['GET'])
def obtener_cliente(request, cliente_id):
    """API para obtener un cliente específico"""
    try:
        cliente = Cliente.objects.select_related(
            'usuario__persona',
            'tipo_cliente'
        ).get(id=cliente_id)
        
        serializer = ClienteSerializer(cliente)
        
        return Response({
            'success': True,
            'cliente': serializer.data
        })
        
    except Cliente.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cliente no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def crear_cliente(request):
    """API para crear un nuevo cliente (con usuario y persona)"""
    serializer = ClienteCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            cliente = serializer.save()
            
            # Serializar el cliente creado
            cliente_serializer = ClienteSerializer(cliente)
            
            return Response({
                'success': True,
                'message': 'Cliente creado exitosamente',
                'cliente': cliente_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al crear cliente: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'error': 'Datos inválidos',
        'detalles': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def actualizar_cliente(request, cliente_id):
    """API para actualizar un cliente existente"""
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        
        # Actualizar solo campos de Cliente
        campos_permitidos = [
            'razon_social', 'nit', 'ciudad', 'direccion',
            'especialidad', 'estado', 'es_vip',
            'limite_credito', 'descuento_especial', 'observaciones'
        ]
        
        for campo in campos_permitidos:
            if campo in request.data:
                setattr(cliente, campo, request.data[campo])
        
        # Actualizar tipo_cliente si se proporciona
        if 'tipo_cliente_id' in request.data:
            try:
                tipo_cliente = TipoCliente.objects.get(id=request.data['tipo_cliente_id'])
                cliente.tipo_cliente = tipo_cliente
            except TipoCliente.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Tipo de cliente no válido'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        cliente.save()
        
        serializer = ClienteSerializer(cliente)
        
        return Response({
            'success': True,
            'message': 'Cliente actualizado exitosamente',
            'cliente': serializer.data
        })
        
    except Cliente.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cliente no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def eliminar_cliente(request, cliente_id):
    """API para desactivar un cliente"""
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        
        # Desactivar cliente y usuario asociado
        cliente.estado = 'INACTIVO'
        cliente.save()
        
        cliente.usuario.is_active = False
        cliente.usuario.save()
        
        return Response({
            'success': True,
            'message': 'Cliente desactivado exitosamente'
        })
        
    except Cliente.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cliente no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def activar_cliente(request, cliente_id):
    """API para activar un cliente"""
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        
        # Activar cliente y usuario asociado
        cliente.estado = 'ACTIVO'
        cliente.save()
        
        cliente.usuario.is_active = True
        cliente.usuario.save()
        
        return Response({
            'success': True,
            'message': 'Cliente activado exitosamente'
        })
        
    except Cliente.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Cliente no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def estadisticas_clientes(request):
    """API para estadísticas de clientes"""
    stats = {
        'total': Cliente.objects.count(),
        'activos': Cliente.objects.filter(estado='ACTIVO').count(),
        'inactivos': Cliente.objects.filter(estado='INACTIVO').count(),
        'vip': Cliente.objects.filter(es_vip=True).count(),
        'por_tipo': {}
    }
    
    # Estadísticas por tipo de cliente
    for tipo in TipoCliente.objects.all():
        count = Cliente.objects.filter(tipo_cliente=tipo).count()
        stats['por_tipo'][tipo.nombre_tipo] = count
    
    return Response({
        'success': True,
        'estadisticas': stats
    })


# ============ PROVEEDORES - CRUD ============

@api_view(['GET'])
def listar_proveedores(request):
    """API para listar proveedores con filtros"""
    tipo_proveedor = request.GET.get('tipo', '').strip()
    estado = request.GET.get('estado', '').strip()
    pais = request.GET.get('pais', '').strip()
    es_premium = request.GET.get('es_premium', '').strip()
    busqueda = request.GET.get('busqueda', '').strip()
    
    # Base query
    proveedores = Proveedor.objects.all()
    
    # Aplicar filtros
    if tipo_proveedor and tipo_proveedor != 'todos':
        proveedores = proveedores.filter(tipo_proveedor=tipo_proveedor.upper())
    
    if estado and estado != 'todos':
        proveedores = proveedores.filter(estado=estado.upper())
    
    if pais and pais != 'todos':
        proveedores = proveedores.filter(pais__icontains=pais)
    
    if es_premium == 'true':
        proveedores = proveedores.filter(es_premium=True)
    
    # Búsqueda por texto
    if busqueda:
        proveedores = proveedores.filter(
            Q(nombre__icontains=busqueda) |
            Q(nit__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(telefono__icontains=busqueda) |
            Q(persona_contacto__icontains=busqueda)
        )
    
    # Ordenar por nombre
    proveedores = proveedores.order_by('nombre')
    
    serializer = ProveedorSerializer(proveedores, many=True)
    
    return Response({
        'success': True,
        'count': len(serializer.data),
        'proveedores': serializer.data
    })


@api_view(['GET'])
def obtener_proveedor(request, proveedor_id):
    """API para obtener un proveedor específico"""
    try:
        proveedor = Proveedor.objects.get(id=proveedor_id)
        serializer = ProveedorSerializer(proveedor)
        
        return Response({
            'success': True,
            'proveedor': serializer.data
        })
        
    except Proveedor.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Proveedor no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def crear_proveedor(request):
    """API para crear un nuevo proveedor"""
    serializer = ProveedorSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            proveedor = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Proveedor creado exitosamente',
                'proveedor': ProveedorSerializer(proveedor).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al crear proveedor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'error': 'Datos inválidos',
        'detalles': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def actualizar_proveedor(request, proveedor_id):
    """API para actualizar un proveedor"""
    try:
        proveedor = Proveedor.objects.get(id=proveedor_id)
        serializer = ProveedorSerializer(proveedor, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'success': True,
                'message': 'Proveedor actualizado exitosamente',
                'proveedor': serializer.data
            })
        
        return Response({
            'success': False,
            'error': 'Datos inválidos',
            'detalles': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Proveedor.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Proveedor no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def eliminar_proveedor(request, proveedor_id):
    """API para desactivar un proveedor"""
    try:
        proveedor = Proveedor.objects.get(id=proveedor_id)
        proveedor.estado = 'INACTIVO'
        proveedor.save()
        
        return Response({
            'success': True,
            'message': 'Proveedor desactivado exitosamente'
        })
        
    except Proveedor.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Proveedor no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def activar_proveedor(request, proveedor_id):
    """API para activar un proveedor"""
    try:
        proveedor = Proveedor.objects.get(id=proveedor_id)
        proveedor.estado = 'ACTIVO'
        proveedor.save()
        
        return Response({
            'success': True,
            'message': 'Proveedor activado exitosamente'
        })
        
    except Proveedor.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Proveedor no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def estadisticas_proveedores(request):
    """API para estadísticas de proveedores"""
    stats = {
        'total': Proveedor.objects.count(),
        'activos': Proveedor.objects.filter(estado='ACTIVO').count(),
        'inactivos': Proveedor.objects.filter(estado='INACTIVO').count(),
        'premium': Proveedor.objects.filter(es_premium=True).count(),
        'por_tipo': {},
        'por_pais': {}
    }
    
    # Estadísticas por tipo
    for tipo_code, tipo_name in Proveedor.TIPO_PROVEEDOR:
        count = Proveedor.objects.filter(tipo_proveedor=tipo_code).count()
        stats['por_tipo'][tipo_name] = count
    
    # Estadísticas por país (top 5)
    paises = Proveedor.objects.values('pais').annotate(
        count=models.Count('id')
    ).order_by('-count')[:5]
    
    for pais in paises:
        stats['por_pais'][pais['pais']] = pais['count']
    
    return Response({
        'success': True,
        'estadisticas': stats
    })