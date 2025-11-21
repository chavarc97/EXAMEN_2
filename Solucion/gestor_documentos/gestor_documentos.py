from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

"""
Principios SOLID:

    * SRP (Single Responsibility Principle) - Separar responsabilidades
    * OCP (Open/Closed Principle) - Extensible sin modificación
    * DIP (Dependency Inversion Principle) - Depender de abstracciones
    
Patrones de Diseño:
    * Strategy Pattern - Para formatos y métodos de entrega
    * Factory Pattern - Para crear reportes
    * Builder Pattern - Para construir reportes complejos
"""     
# ========================================================================================================
# MODELO DE DATOS
# ========================================================================================================
class Report:
    """Modelo de datos para un reporte"""
    
    def __init__(self, content: str, report_type: str, 
                 format_type: str, metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.type = report_type
        self.format = format_type
        self.timestamp = datetime.now()
        self.metadata = metadata or {}
    
    def get_content(self) -> str:
        return self.content
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'format': self.format,
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            **self.metadata
        }
        
# ========================================================================================================
# Patron Factory: Generador de Reportes
# Justificación: Centraliza la creación de reportes, facilitando la extensión y mantenimiento.
# OCP: Se pueden agregar nuevos tipos de reportes sin modificar el código existente.

# INTERFACES (Principio DIP - Dependency Inversion Principle)
# ============================================================================
class IFormatStrategy(ABC):
    """Interface para estrategias de formateo (Pattern: Strategy)"""
    
    @abstractmethod
    def format(self, content: str) -> str:
        """Formatea el contenido del reporte"""
        pass


class IDeliveryStrategy(ABC):
    """Interface para estrategias de entrega (Pattern: Strategy)"""
    
    @abstractmethod
    def deliver(self, report: str, metadata: Dict[str, Any]) -> bool:
        """Entrega el reporte según el método especificado"""
        pass
class IReportGenerator(ABC):
    @abstractmethod
    def generate_report(self,data: Dict[str, Any],) -> Report:
        pass
 
# ========================================================================================================
# GENERADORES DE REPORTES (Principio SRP - Single Responsibility Principle)
# Cada clase tiene UNA sola responsabilidad: generar un tipo específico de reporte
# =========================================================================================================
class SalesReportGenerator(IReportGenerator):
    """Generador de reportes de ventas"""
    
    def generate_report(self, data: Dict[str, Any]) -> Report:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = "=" * 60 + "\n"
        content += "           REPORTE DE VENTAS\n"
        content += "=" * 60 + "\n"
        content += f"Fecha de generación: {timestamp}\n\n"
        
        total_sales = self._calculate_totals(data['sales'])
        content += f"Total de ventas: ${total_sales:.2f}\n"
        content += f"Número de transacciones: {len(data['sales'])}\n"
        content += f"Periodo: {data['period']}\n\n"
        
        content += self._format_sales_detail(data['sales'])
        
        return Report(content, 'sales', 'raw', {'period': data['period']})
    
    def _calculate_totals(self, sales: List[Dict]) -> float:
        return sum(item['amount'] for item in sales)
    
    def _format_sales_detail(self, sales: List[Dict]) -> str:
        detail = "Detalle de ventas:\n"
        detail += "-" * 60 + "\n"
        for sale in sales:
            detail += f"  • Producto: {sale['product']} - ${sale['amount']:.2f}\n"
        return detail
    
    
class InventoryReportGenerator(IReportGenerator):
    """Generador de reportes de inventario"""
    
    def generate_report(self, data: Dict[str, Any]) -> Report:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = "=" * 60 + "\n"
        content += "           REPORTE DE INVENTARIO\n"
        content += "=" * 60 + "\n"
        content += f"Fecha de generación: {timestamp}\n\n"
        
        total_items = self._calculate_totals(data['items'])
        categories = self._group_by_category(data['items'])
        
        content += f"Total de productos: {total_items}\n"
        content += f"Categorías: {len(categories)}\n\n"
        
        content += "Inventario actual:\n"
        content += "-" * 60 + "\n"
        for item in data['items']:
            content += f"  • {item['name']} ({item['category']}): {item['quantity']} unidades\n"
        
        return Report(content, 'inventory', 'raw', {'total_items': total_items})
    
    def _calculate_totals(self, items: List[Dict]) -> int:
        return sum(item['quantity'] for item in items)
    
    def _group_by_category(self, items: List[Dict]) -> Dict:
        categories = {}
        for item in items:
            cat = item['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        return categories
    

class FinancialReportGenerator(IReportGenerator):
    """Generador de reportes financieros"""
    
    def generate_report(self, data: Dict[str, Any]) -> Report:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = "=" * 60 + "\n"
        content += "           REPORTE FINANCIERO\n"
        content += "=" * 60 + "\n"
        content += f"Fecha de generación: {timestamp}\n\n"
        
        balance = self._calculate_balance(data['income'], data['expenses'])
        
        content += f"Ingresos: ${data['income']:.2f}\n"
        content += f"Gastos: ${data['expenses']:.2f}\n"
        content += f"Balance: ${balance:.2f}\n"
        
        return Report(content, 'financial', 'raw', {'balance': balance})
    
    def _calculate_balance(self, income: float, expenses: float) -> float:
        return income - expenses
    
    


# ====================================================================================================================
# ESTRATEGIAS DE FORMATO (Patrón Strategy + Principio OCP)
# Open/Closed Principle: abierto para extensión, cerrado para modificación
# Podemos agregar nuevos formatos sin modificar código existente
# ==========================================================
class PDFFormatter(IFormatStrategy):
    """Estrategia de formateo a PDF"""
    
    def format(self, content: str) -> str:
        print("📄 Generando reporte en formato PDF...")
        return f"[PDF FORMAT]\n{content}\n[END PDF]"


class ExcelFormatter(IFormatStrategy):
    """Estrategia de formateo a Excel"""
    
    def format(self, content: str) -> str:
        print("📊 Generando reporte en formato Excel...")
        return f"[EXCEL FORMAT]\n{content}\n[END EXCEL]"


class HTMLFormatter(IFormatStrategy):
    """Estrategia de formateo a HTML"""
    
    def format(self, content: str) -> str:
        print("🌐 Generando reporte en formato HTML...")
        return f"<html><body><pre>{content}</pre></body></html>"
    

# ====================================================================================================================
# ESTRATEGIAS DE ENTREGA (Patrón Strategy + Principio OCP)
# ====================================================================================================================
class EmailDelivery(IDeliveryStrategy):
    """Estrategia de entrega por email"""
    
    def __init__(self, smtp_config: Optional[Dict[str, Any]] = None):
        self.smtp_config = smtp_config or {'recipient': 'admin@company.com'}
    
    def deliver(self, report: str, metadata: Dict[str, Any]) -> bool:
        print(f"📧 Enviando reporte por email...")
        print(f"   Destinatario: {self.smtp_config['recipient']}")
        return True


class DownloadDelivery(IDeliveryStrategy):
    """Estrategia de entrega por descarga"""
    
    def __init__(self, download_path: str = "./reports"):
        self.download_path = download_path
    
    def deliver(self, report: str, metadata: Dict[str, Any]) -> bool:
        filename = f"report_{metadata['type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{metadata['format']}"
        print(f"💾 Reporte disponible para descarga: {filename}")
        print(f"   Ubicación: {self.download_path}/{filename}")
        return True


class CloudDelivery(IDeliveryStrategy):
    """Estrategia de entrega a la nube"""
    
    def __init__(self, cloud_config: Optional[Dict[str, Any]] = None):
        self.cloud_config = cloud_config or {'base_url': 'https://cloud.company.com'}
    
    def deliver(self, report: str, metadata: Dict[str, Any]) -> bool:
        print(f"☁️  Subiendo reporte a la nube...")
        print(f"   URL: {self.cloud_config['base_url']}/reports/{metadata['type']}")
        return True



# ====================================================================================================================
# PATRÓN FACTORY
# ====================================================================================================================

class ReportFactory:
    """Factory para crear generadores de reportes"""
    
    def __init__(self):
        self._generators = {
            'sales': SalesReportGenerator(),
            'inventory': InventoryReportGenerator(),
            'financial': FinancialReportGenerator()
        }
    
    def create_generator(self, report_type: str) -> IReportGenerator:
        """Crea un generador según el tipo de reporte"""
        generator = self._generators.get(report_type)
        if not generator:
            raise ValueError(f"Tipo de reporte no soportado: {report_type}")
        return generator
    
    def register_generator(self, report_type: str, generator: IReportGenerator):
        """Permite registrar nuevos tipos de generadores (Principio OCP)"""
        self._generators[report_type] = generator
        

# ====================================================================================================================
# PATRÓN BUILDER
# ====================================================================================================================
class ReportBuilder:
    """Builder para construir reportes complejos paso a paso"""
    
    def __init__(self):
        self._generator = None
        self._formatter = None
        self._delivery = None
        self._data = None
    
    def set_generator(self, generator: IReportGenerator) -> 'ReportBuilder':
        self._generator = generator
        return self
    
    def set_formatter(self, formatter: IFormatStrategy) -> 'ReportBuilder':
        self._formatter = formatter
        return self
    
    def set_delivery(self, delivery: IDeliveryStrategy) -> 'ReportBuilder':
        self._delivery = delivery
        return self
    
    def set_data(self, data: Dict[str, Any]) -> 'ReportBuilder':
        self._data = data
        return self
    
    def build(self) -> Report:
        """Construye y entrega el reporte completo"""
        if not all([self._generator, self._formatter, self._delivery, self._data]):
            raise ValueError("Faltan componentes para construir el reporte")
        
        # Generar contenido
        assert self._generator is not None
        assert self._formatter is not None
        assert self._delivery is not None
        assert self._data is not None
        
        report = self._generator.generate_report(self._data)
        
        # Formatear
        formatted_content = self._formatter.format(report.get_content())
        
        # Entregar
        self._delivery.deliver(formatted_content, report.get_metadata())
        
        # Actualizar reporte con contenido formateado
        report.content = formatted_content
        
        print(f"\n✅ Reporte generado exitosamente\n")
        print(formatted_content)
        print("\n" + "=" * 60 + "\n")
        
        return report
    
    
# ===================================================================================================================
# SISTEMA PRINCIPAL
# ===================================================================================================================

class ReportSystem:
    """Sistema principal de generación de reportes"""
    
    def __init__(self):
        self.factory = ReportFactory()
        self.builder = ReportBuilder()
        self.report_history = []
        
        # Mapeos de estrategias
        self._format_strategies = {
            'pdf': PDFFormatter(),
            'excel': ExcelFormatter(),
            'html': HTMLFormatter()
        }
        
        self._delivery_strategies = {
            'email': EmailDelivery(),
            'download': DownloadDelivery(),
            'cloud': CloudDelivery()
        }
    
    def generate_report(self, report_type: str, data: Dict[str, Any],
                       output_format: str, delivery_method: str) -> Report:
        """Genera un reporte completo usando el builder pattern"""
        
        # Obtener componentes
        generator = self.factory.create_generator(report_type)
        formatter = self._format_strategies.get(output_format)
        delivery = self._delivery_strategies.get(delivery_method)
        
        if not formatter:
            raise ValueError(f"Formato no soportado: {output_format}")
        if not delivery:
            raise ValueError(f"Método de entrega no soportado: {delivery_method}")
        
        # Construir reporte
        report = (self.builder
                 .set_generator(generator)
                 .set_formatter(formatter)
                 .set_delivery(delivery)
                 .set_data(data)
                 .build())
        
        # Registrar en historial
        self._log_report(report)
        
        return report
    
    def _log_report(self, report: Report):
        """Registra el reporte en el historial"""
        self.report_history.append({
            'type': report.type,
            'format': report.format,
            'timestamp': report.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'metadata': report.metadata
        })
    
    def get_report_history(self) -> List[Dict[str, Any]]:
        """Obtiene el historial de reportes generados"""
        return self.report_history
    
    
    
# ============================================================================
# CÓDIGO DE PRUEBA
# ============================================================================

if __name__ == "__main__":
    system = ReportSystem()
    
    # Reporte de ventas
    sales_data = {
        'period': 'Enero 2024',
        'sales': [
            {'product': 'Laptop HP', 'amount': 899.99},
            {'product': 'Mouse Logitech', 'amount': 25.50},
            {'product': 'Teclado Mecánico', 'amount': 120.00},
            {'product': 'Monitor LG 24"', 'amount': 199.99}
        ]
    }
    
    system.generate_report('sales', sales_data, 'pdf', 'email')
    
    # Reporte de inventario
    inventory_data = {
        'items': [
            {'name': 'Laptop HP', 'category': 'Computadoras', 'quantity': 15},
            {'name': 'Mouse Logitech', 'category': 'Accesorios', 'quantity': 50},
            {'name': 'Teclado Mecánico', 'category': 'Accesorios', 'quantity': 30},
            {'name': 'Monitor LG', 'category': 'Pantallas', 'quantity': 20}
        ]
    }
    
    system.generate_report('inventory', inventory_data, 'excel', 'download')
    
    # Reporte financiero
    financial_data = {
        'income': 50000.00,
        'expenses': 32000.00
    }
    
    system.generate_report('financial', financial_data, 'html', 'cloud')
    
    # Mostrar historial
    print("\nHISTORIAL DE REPORTES GENERADOS:")
    print(json.dumps(system.get_report_history(), indent=2))