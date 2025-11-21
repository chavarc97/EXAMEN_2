from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
import json


# ============================================================================
# INTERFACES (Principio DIP - Dependency Inversion Principle)
# ============================================================================

class INotificationStrategy(ABC):
    """
    Interface para estrategias de notificación (Pattern: Strategy)
    Permite agregar nuevos canales sin modificar código existente (OCP)
    """
    
    @abstractmethod
    def send(self, notification: 'Notification') -> bool:
        """Envía una notificación por el canal específico"""
        pass
    
    
# ============================================================================
# CLASES PARA OBJETOS DE DOMINIO
# ============================================================================
class Customer:
    """Value Object que representa un cliente"""
    
    def __init__(self, name: str, email: str, phone: str, 
                 device_id: str, preferences: Optional[List[str]] = None):
        self.name = name
        self.email = email
        self.phone = phone
        self.device_id = device_id
        self.notification_preferences = preferences or ['email']
    
    def get_contact_info(self, channel: str) -> Optional[str]:
        """Obtiene la información de contacto según el canal"""
        contact_map = {
            'email': self.email,
            'sms': self.phone,
            'push': self.device_id
        }
        return contact_map.get(channel)
    
    def prefers_channel(self, channel: str) -> bool:
        """Verifica si el cliente prefiere este canal"""
        return channel in self.notification_preferences


class Order:
    """Value Object que representa un pedido"""
    
    def __init__(self, order_id: str, customer: Customer, 
                 total: float, items: Optional[List[Dict[str, Any]]] = None):
        self.order_id = order_id
        self.customer = customer
        self.total = total
        self.items = items or []
        self.timestamp = datetime.now()
    
    def get_order_id(self) -> str:
        return self.order_id
    
    def get_total(self) -> float:
        return self.total
    
    def get_customer(self) -> Customer:
        return self.customer


class Notification:
    """Entity que representa una notificación"""
    
    def __init__(self, notification_type: str, recipient: str, 
                 message: str, order_id: str):
        self.notification_id = f"NOTIF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.type = notification_type
        self.recipient = recipient
        self.message = message
        self.order_id = order_id
        self.timestamp = datetime.now()
        self.status = 'pending'
    
    def mark_as_sent(self):
        """Marca la notificación como enviada"""
        self.status = 'sent'
    
    def mark_as_failed(self, error: str):
        """Marca la notificación como fallida"""
        self.status = 'failed'
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la notificación a diccionario"""
        return {
            'notification_id': self.notification_id,
            'type': self.type,
            'recipient': self.recipient,
            'message': self.message,
            'order_id': self.order_id,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status
        }
        

# ============================================================================
# ESTRATEGIAS DE NOTIFICACIÓN (Strategy Pattern + SRP)
# Cada clase tiene UNA responsabilidad: enviar notificaciones por UN canal
# ============================================================================
class EmailNotifier(INotificationStrategy):
    """Estrategia para envío de emails (Principio SRP)"""
    
    def __init__(self, smtp_config: Optional[Dict[str, Any]] = None):
        self.smtp_config = smtp_config or {
            'host': 'smtp.company.com',
            'port': 587
        }
    
    def send(self, notification: Notification) -> bool:
        """Envía notificación por email"""
        try:
            # Simulación de envío de email
            html_email = self._format_html_email(notification.message)
            
            print(f"📧 EMAIL enviado a {notification.recipient}")
            print(f"   Asunto: Confirmación de Pedido #{notification.order_id}")
            print(f"   Mensaje: {notification.message}\n")
            
            notification.mark_as_sent()
            return True
        except Exception as e:
            notification.mark_as_failed(str(e))
            return False
    
    def _format_html_email(self, message: str) -> str:
        """Formatea el mensaje como HTML"""
        return f"<html><body><p>{message}</p></body></html>"


class SMSNotifier(INotificationStrategy):
    """Estrategia para envío de SMS (Principio SRP)"""
    
    def __init__(self, gateway_config: Optional[Dict[str, Any]] = None):
        self.gateway_config = gateway_config or {
            'provider': 'Twilio',
            'api_key': 'fake-api-key'
        }
    
    def send(self, notification: Notification) -> bool:
        """Envía notificación por SMS"""
        try:
            if not self._validate_phone(notification.recipient):
                raise ValueError("Número de teléfono inválido")
            
            formatted_sms = self._format_sms(notification.message)
            
            print(f"📱 SMS enviado a {notification.recipient}")
            print(f"   Mensaje: {formatted_sms}\n")
            
            notification.mark_as_sent()
            return True
        except Exception as e:
            notification.mark_as_failed(str(e))
            return False
    
    def _validate_phone(self, phone: str) -> bool:
        """Valida formato de teléfono"""
        return bool(phone and len(phone) > 10)
    
    def _format_sms(self, message: str) -> str:
        """Formatea mensaje para SMS (máximo 160 caracteres)"""
        return message[:160]


class PushNotifier(INotificationStrategy):
    """Estrategia para envío de notificaciones push (Principio SRP)"""
    
    def __init__(self, push_service: str = 'Firebase'):
        self.push_service = push_service
        self.credentials = {
            'api_key': 'fake-firebase-key',
            'project_id': 'my-project'
        }
    
    def send(self, notification: Notification) -> bool:
        """Envía notificación push"""
        try:
            if not self._validate_device(notification.recipient):
                raise ValueError("Device ID inválido")
            
            push_payload = self._format_push(notification.message)
            
            print(f"🔔 PUSH enviada al dispositivo {notification.recipient}")
            print(f"   Mensaje: {notification.message}\n")
            
            notification.mark_as_sent()
            return True
        except Exception as e:
            notification.mark_as_failed(str(e))
            return False
    
    def _validate_device(self, device_id: str) -> bool:
        """Valida el device ID"""
        return bool(device_id and device_id.startswith('DEVICE-'))
    
    def _format_push(self, message: str) -> Dict[str, Any]:
        """Formatea el mensaje como payload push"""
        return {
            'notification': {
                'title': 'Pedido Confirmado',
                'body': message,
                'sound': 'default'
            }
        }


# ============================================================================
# PATRÓN FACTORY
# ============================================================================

class NotificationFactory:
    """
    Factory para crear estrategias de notificación
    Permite agregar nuevos canales dinámicamente (Principio OCP)
    """
    
    def __init__(self):
        self._notifiers: Dict[str, INotificationStrategy] = {
            'email': EmailNotifier(),
            'sms': SMSNotifier(),
            'push': PushNotifier()
        }
    
    def create_notifier(self, notification_type: str) -> INotificationStrategy:
        """Crea una estrategia de notificación según el tipo"""
        notifier = self._notifiers.get(notification_type)
        if not notifier:
            raise ValueError(f"Tipo de notificación no soportado: {notification_type}")
        return notifier
    
    def register_notifier(self, notification_type: str, 
                         notifier: INotificationStrategy):
        """
        Permite registrar nuevos tipos de notificadores (Principio OCP)
        Ej: factory.register_notifier('whatsapp', WhatsAppNotifier())
        """
        self._notifiers[notification_type] = notifier
    
    def get_available_channels(self) -> List[str]:
        """Retorna los canales disponibles"""
        return list(self._notifiers.keys())
    
    
# ============================================================================
# PATRÓN BUILDER
# ============================================================================

class MessageBuilder:
    """
    Builder para construir mensajes personalizados
    Separa la construcción del mensaje de su representación
    """
    
    def __init__(self):
        self._order: Optional[Order] = None
        self._customer: Optional[Customer] = None
        self._channel: Optional[str] = None
    
    def set_order(self, order: Order) -> 'MessageBuilder':
        self._order = order
        return self
    
    def set_customer(self, customer: Customer) -> 'MessageBuilder':
        self._customer = customer
        return self
    
    def set_channel(self, channel: str) -> 'MessageBuilder':
        self._channel = channel
        return self
    
    def build(self) -> str:
        """Construye el mensaje personalizado"""
        if not all([self._order, self._customer, self._channel]):
            raise ValueError("Faltan datos para construir el mensaje")
        
        # Aplicar plantilla según el canal
        message = self._apply_template()
        
        # Personalizar
        message = self._personalize(message)
        
        return message
    
    def _apply_template(self) -> str:
        """Aplica la plantilla según el canal"""
        # Assert non-None to satisfy type checker
        assert self._customer is not None
        assert self._order is not None
        assert self._channel is not None
        
        templates = {
            'email': (f"Estimado {self._customer.name}, su pedido "
                     f"#{self._order.order_id} por ${self._order.total:.2f} "
                     f"ha sido confirmado. Gracias por su compra."),
            
            'sms': (f"Pedido #{self._order.order_id} confirmado. "
                   f"Total: ${self._order.total:.2f}. Gracias!"),
            
            'push': (f"¡Pedido confirmado! #{self._order.order_id} - "
                    f"${self._order.total:.2f}")
        }
        
        return templates.get(self._channel, "Pedido confirmado")
    
    def _personalize(self, message: str) -> str:
        """Personaliza el mensaje con datos adicionales"""
        # Aquí se pueden agregar personalizaciones adicionales
        # como emojis, links de tracking, etc.
        return message


# ============================================================================
# REPOSITORY (SRP)
# ============================================================================

class NotificationRepository:
    """
    Repository para gestionar el almacenamiento de notificaciones
    Responsabilidad única: persistencia de datos
    """
    
    def __init__(self):
        self._storage: List[Notification] = []
    
    def save(self, notification: Notification):
        """Guarda una notificación"""
        self._storage.append(notification)
    
    def find_by_order(self, order_id: str) -> List[Notification]:
        """Encuentra notificaciones por ID de pedido"""
        return [n for n in self._storage if n.order_id == order_id]
    
    def find_by_customer(self, customer_email: str) -> List[Notification]:
        """Encuentra notificaciones por email de cliente"""
        return [n for n in self._storage if customer_email in n.recipient]
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todas las notificaciones como diccionarios"""
        return [n.to_dict() for n in self._storage]
    

# ============================================================================
# NOTIFICATION MANAGER
# ============================================================================

class NotificationManager:
    """
    Manager que coordina el envío de notificaciones
    Usa Factory, Builder y Repository (orquestación)
    """
    
    def __init__(self):
        self.factory = NotificationFactory()
        self.message_builder = MessageBuilder()
        self.repository = NotificationRepository()
    
    def send_notifications(self, order: Order, channels: List[str]):
        """Envía notificaciones por los canales especificados"""
        print(f"\n{'='*50}")
        print(f"Procesando pedido #{order.order_id}")
        print(f"Cliente: {order.customer.name}")
        print(f"Total: ${order.total:.2f}")
        print(f"{'='*50}\n")
        
        for channel in channels:
            try:
                # Crear notificación
                notification = self._create_notification(order, channel)
                
                # Obtener estrategia de envío
                notifier = self.factory.create_notifier(channel)
                
                # Enviar
                success = notifier.send(notification)
                
                # Guardar en repositorio
                self.repository.save(notification)
                
                if not success:
                    print(f"⚠️  Falló el envío por {channel}")
                    
            except Exception as e:
                print(f"❌ Error al enviar por {channel}: {str(e)}\n")
    
    def _create_notification(self, order: Order, channel: str) -> Notification:
        """Crea una notificación usando el builder"""
        # Construir mensaje
        message = (self.message_builder
                  .set_order(order)
                  .set_customer(order.customer)
                  .set_channel(channel)
                  .build())
        
        # Obtener destinatario
        recipient = order.customer.get_contact_info(channel)
        
        # Validar que el destinatario existe
        if recipient is None:
            raise ValueError(f"No se encontró información de contacto para el canal {channel}")
        
        # Crear notificación
        return Notification(
            notification_type=channel,
            recipient=recipient,
            message=message,
            order_id=order.order_id
        )


# ============================================================================
# ORDER PROCESSOR
# ============================================================================

class OrderProcessor:
    """
    Procesador de pedidos que coordina la validación y notificación
    """
    
    def __init__(self, notification_manager: NotificationManager):
        self.notification_manager = notification_manager
    
    def process_order(self, order_data: Dict[str, Any], 
                     notification_types: List[str]):
        """Procesa un pedido y envía notificaciones"""
        # Validar datos del pedido
        if not self._validate_order(order_data):
            raise ValueError("Datos de pedido inválidos")
        
        # Crear objetos de dominio
        customer = Customer(
            name=order_data['customer']['name'],
            email=order_data['customer']['email'],
            phone=order_data['customer']['phone'],
            device_id=order_data['customer']['device_id'],
            preferences=notification_types
        )
        
        order = Order(
            order_id=order_data['order_id'],
            customer=customer,
            total=order_data['total'],
            items=order_data.get('items', [])
        )
        
        # Enviar notificaciones
        self.notification_manager.send_notifications(order, notification_types)
    
    def _validate_order(self, order_data: Dict[str, Any]) -> bool:
        """Valida los datos del pedido"""
        required_fields = ['order_id', 'customer', 'total']
        return all(field in order_data for field in required_fields)


# ============================================================================
# SISTEMA PRINCIPAL
# ============================================================================

class OrderNotificationSystem:
    """Sistema principal de notificaciones de pedidos"""
    
    def __init__(self):
        self.notification_manager = NotificationManager()
        self.order_processor = OrderProcessor(self.notification_manager)
    
    def process_order(self, order_data: Dict[str, Any], 
                     notification_types: List[str]):
        """Procesa un pedido (punto de entrada principal)"""
        self.order_processor.process_order(order_data, notification_types)
    
    def get_notification_history(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de notificaciones"""
        return self.notification_manager.repository.get_all()


# ============================================================================
# CÓDIGO DE PRUEBA
# ============================================================================

if __name__ == "__main__":
    system = OrderNotificationSystem()
    
    # Pedido 1: Cliente premium (todos los canales)
    order1 = {
        'order_id': 'ORD-001',
        'customer': {
            'name': 'Ana García',
            'email': 'ana.garcia@email.com',
            'phone': '+34-600-123-456',
            'device_id': 'DEVICE-ABC-123'
        },
        'total': 150.50
    }
    
    system.process_order(order1, ['email', 'sms', 'push'])
    
    # Pedido 2: Cliente estándar (solo email)
    order2 = {
        'order_id': 'ORD-002',
        'customer': {
            'name': 'Carlos Ruiz',
            'email': 'carlos.ruiz@email.com',
            'phone': '+34-600-789-012',
            'device_id': 'DEVICE-XYZ-789'
        },
        'total': 75.00
    }
    
    system.process_order(order2, ['email'])
    
    # Mostrar historial
    print("\n" + "="*50)
    print("HISTORIAL DE NOTIFICACIONES")
    print("="*50)
    history = system.get_notification_history()
    print(json.dumps(history, indent=2, ensure_ascii=False))