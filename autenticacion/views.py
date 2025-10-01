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
from .models import Usuario, Persona, Rol, UsuarioRol
from .serializers import (
    LoginSerializer, RegistroSerializer, UsuarioSerializer,
    CambiarPasswordSerializer
)
import re
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

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
                usuario = serializer.save()
                
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
                    'message': 'Usuario registrado exitosamente',
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
    """API para listar usuarios - SIN AUTENTICACIÓN"""
    busqueda = request.GET.get('busqueda', '')
    rol = request.GET.get('rol', '')
    estado = request.GET.get('estado', '')
    
    usuarios = Usuario.objects.select_related('persona').prefetch_related('usuario_roles__rol')
    
    if busqueda:
        usuarios = usuarios.filter(
            Q(nombre_usuario__icontains=busqueda) |
            Q(persona__nombre__icontains=busqueda) |
            Q(persona__apellido_paterno__icontains=busqueda) |
            Q(persona__correo__icontains=busqueda)
        )
    
    if estado == 'activo':
        usuarios = usuarios.filter(is_active=True)
    elif estado == 'inactivo':
        usuarios = usuarios.filter(is_active=False)
    
    if rol and rol != 'todos':
        usuarios = usuarios.filter(usuario_roles__rol__nombre_rol=rol.upper(), usuario_roles__estado='ACTIVO')
    
    usuarios = usuarios.order_by('-fecha_creacion')
    
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
    """API para crear usuario - SIN AUTENTICACIÓN"""
    serializer = RegistroSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            usuario = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Usuario creado exitosamente',
                'usuario': {
                    'id': usuario.id,
                    'nombre_usuario': usuario.nombre_usuario,
                    'nombre_completo': usuario.get_nombre_completo(),
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Error al crear usuario: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'error': 'Datos inválidos',
        'detalles': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def actualizar_usuario(request, usuario_id):
    """API para actualizar usuario - SIN AUTENTICACIÓN"""
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        persona = usuario.persona
        
        if 'nombre' in request.data:
            persona.nombre = request.data['nombre']
        if 'apellido_paterno' in request.data:
            persona.apellido_paterno = request.data['apellido_paterno']
        if 'apellido_materno' in request.data:
            persona.apellido_materno = request.data['apellido_materno']
        if 'numero_celular' in request.data:
            persona.numero_celular = request.data['numero_celular']
        if 'correo' in request.data:
            persona.correo = request.data['correo']
        
        persona.save()
        
        if 'is_active' in request.data:
            usuario.is_active = request.data['is_active']
        
        if 'password' in request.data and request.data['password']:
            usuario.set_password(request.data['password'])
        
        if 'rol' in request.data:
            rol_nombre = request.data['rol']
            try:
                rol = Rol.objects.get(nombre_rol=rol_nombre)
                UsuarioRol.objects.filter(usuario=usuario).update(estado='INACTIVO')
                UsuarioRol.objects.update_or_create(
                    usuario=usuario,
                    rol=rol,
                    defaults={'estado': 'ACTIVO'}
                )
            except Rol.DoesNotExist:
                pass
        
        usuario.save()
        
        return Response({
            'success': True,
            'message': 'Usuario actualizado exitosamente'
        })
        
    except Usuario.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)

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