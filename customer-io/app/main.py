from customerio import CustomerIO, Regions
import requests
import time
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURACIÓN ---

# 1. Site ID y API Key para Tracking API (crear/actualizar/eliminar personas)
SITE_ID = os.getenv("CUSTOMERIO_SITE_ID")
TRACKING_API_KEY = os.getenv("CUSTOMERIO_TRACKING_API_KEY")

# 2. App API Key para consultar datos (GET)
APP_API_KEY = os.getenv("CUSTOMERIO_APP_API_KEY")

# 3. Región - ⚠️ IMPORTANTE: Verifica tu región en Settings > Privacy
# Ve a: https://fly.customer.io/settings/privacy
REGION = Regions.US  # Cambia a Regions.EU si tu cuenta está en Europa

# Base URL para App API según región (se configura automáticamente)
if REGION == Regions.EU:
    API_BASE_URL = "https://api-eu.customer.io/v1"
    TRACKING_URL = "https://track-eu.customer.io"
else:
    API_BASE_URL = "https://api.customer.io/v1"
    TRACKING_URL = "https://track.customer.io"

# Inicializar cliente de Tracking con la región correcta
tracking_client = CustomerIO(SITE_ID, TRACKING_API_KEY, region=REGION)

logger.info(f"✅ Configuración completada")
logger.info(f"   - Región: {REGION}")
logger.info(f"   - API Base URL: {API_BASE_URL}")
logger.info(f"   - Tracking URL: {TRACKING_URL}")


# --- FUNCIONES DE TRACKING (CustomerIO SDK) ---

def create_or_update_customer(user_id, email, first_name, plan):
    """
    CREAR / ACTUALIZAR cliente usando Tracking API.
    Si el ID no existe, lo crea. Si ya existe, actualiza sus atributos.

    Docs: https://customer.io/docs/api/track/#operation/identify
    """
    try:
        logger.info(f"Enviando datos para usuario: {user_id}...")

        tracking_client.identify(
            id=user_id,
            email=email,
            first_name=first_name,
            plan=plan,
            subscription_status="active",
            created_at=int(time.time()),
        )

        logger.success("✅ Cliente creado/actualizado correctamente")
        return True

    except Exception as e:
        logger.error(f"❌ Error al crear/actualizar cliente: {e}")
        return False


def delete_customer(user_id):
    """
    ELIMINAR un cliente.

    Docs: https://customer.io/docs/api/track/#operation/delete
    """
    try:
        logger.info(f"Eliminando usuario: {user_id}...")
        tracking_client.delete(user_id)
        logger.success("✅ Cliente eliminado correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error al eliminar cliente: {e}")
        return False


def track_event(user_id, event_name, event_data=None):
    """
    Rastrear un evento para un cliente.

    Docs: https://customer.io/docs/api/track/#operation/track
    """
    try:
        logger.info(f"Registrando evento '{event_name}' para usuario: {user_id}...")

        if event_data is None:
            event_data = {}

        tracking_client.track(customer_id=user_id, name=event_name, **event_data)

        logger.success(f"✅ Evento '{event_name}' registrado correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error al registrar evento: {e}")
        return False


# --- FUNCIONES DE CONSULTA (App API con requests) ---

def get_customer(cio_id):
    """
    GET: Obtener datos de un cliente usando App API directamente.

    Docs: https://customer.io/docs/api/app/#tag/customers
    """
    try:
        logger.info(f"Buscando datos del usuario: {cio_id}...")

        url = f"{API_BASE_URL}/customers/{cio_id}"
        headers = {
            "Authorization": f"Bearer {APP_API_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers, timeout=10)
        logger.info(f"Response Status Code: {response.content}")
        if response.status_code == 200:
            customer_data = response.json()
            customer = customer_data.get("customer", {})

            logger.success("✅ Usuario encontrado:")
            logger.info(f"   - ID: {customer.get('id')}")
            logger.info(f"   - Email: {customer.get('email')}")
            logger.info(f"   - CIO ID: {customer.get('cio_id')}")
            logger.info(f"   - Atributos: {customer.get('attributes', {})}")

            return customer
        elif response.status_code == 404:
            logger.warning("⚠️ Usuario no encontrado")
            logger.info("💡 El usuario puede estar en proceso de creación. Espera unos segundos.")
            return None
        elif response.status_code == 401:
            logger.error("❌ Error 401 - Unauthorized")
            logger.info("💡 Posibles causas:")
            logger.info("   1. App API Key incorrecta")
            logger.info("   2. App API Key sin permiso 'Customers: Read'")
            logger.info("   3. Región incorrecta (verifica US vs EU)")
            return None
        else:
            logger.error(
                f"❌ Error al obtener usuario: {response.status_code} - {response.text}"
            )
            return None

    except Exception as e:
        logger.error(f"❌ Error al obtener usuario: {e}")
        return None


def find_customer_by_email(email):
    """
    Buscar cliente por email usando App API.

    Docs: https://customer.io/docs/api/app/#operation/listCustomers
    """
    try:
        logger.info(f"🔎 Buscando usuario por email: {email}...")

        url = f"{API_BASE_URL}/customers"
        headers = {
            "Authorization": f"Bearer {APP_API_KEY}",
            "Content-Type": "application/json",
        }
        params = {"email": email}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                user = data["results"][0]
                logger.success("✅ ¡Usuario encontrado!")
                logger.info(f"   - ID: {user.get('id')}")
                logger.info(f"   - Email: {user.get('email')}")
                logger.info(f"   - CIO ID: {user.get('cio_id')}")
                return user
            else:
                logger.warning("⚠️ No se encontró ningún usuario con ese email")
                return None
        elif response.status_code == 401:
            logger.error("❌ Error 401 - Unauthorized")
            logger.info("💡 Verifica:")
            logger.info("   1. Tu App API Key en el .env")
            logger.info("   2. Que tenga permiso 'Customers: Read'")
            logger.info("   3. Que la región sea correcta (US o EU)")
            return None
        else:
            logger.error(
                f"❌ Error al buscar por email: {response.status_code} - {response.text}"
            )
            return None

    except Exception as e:
        logger.error(f"❌ Error al buscar por email: {e}")
        return None


def search_customers(filter_query: dict, limit: int = 10):
    """
    Search customers using Customer.io App API.
    Requires App API key with Customers: Read permission.
    """

    if not filter_query:
        raise ValueError("filter_query is required")

    url = f"{API_BASE_URL}/customers/search"
    headers = {
        "Authorization": f"Bearer {APP_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "filter": filter_query,
        "limit": limit,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    if response.status_code == 200:
        results = response.json().get("results", [])
        logger.success(f"Found {len(results)} customers")
        return results

    if response.status_code == 401:
        logger.error("Unauthorized: check App API Key permissions")
        return []

    logger.error(f"Search failed: {response.status_code} {response.content}")
    return []



def get_customer_attributes(user_id):
    """
    Obtener solo los atributos de un cliente.
    """
    try:
        logger.info(f"Obteniendo atributos del usuario: {user_id}...")

        url = f"{API_BASE_URL}/customers/{user_id}/attributes"
        headers = {
            "Authorization": f"Bearer {APP_API_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            attributes = response.json()
            logger.success("✅ Atributos obtenidos:")
            logger.info(f"   {attributes}")
            return attributes
        elif response.status_code == 404:
            logger.warning("⚠️ Usuario no encontrado")
            return None
        elif response.status_code == 401:
            logger.error("❌ Error 401 - Unauthorized")
            logger.info("💡 Verifica tu App API Key y región")
            return None
        else:
            logger.error(f"❌ Error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logger.error(f"❌ Error al obtener atributos: {e}")
        return None


def verify_configuration():
    """
    Verificar que la configuración es correcta antes de ejecutar.
    """
    logger.info("=== VERIFICANDO CONFIGURACIÓN ===\n")
    
    issues = []
    
    # Verificar variables de entorno
    if not SITE_ID:
        issues.append("❌ CUSTOMERIO_SITE_ID no está configurado")
    else:
        logger.success(f"✅ Site ID: {SITE_ID[:8]}...")
    
    if not TRACKING_API_KEY:
        issues.append("❌ CUSTOMERIO_TRACKING_API_KEY no está configurado")
    else:
        logger.success(f"✅ Tracking API Key: {TRACKING_API_KEY[:8]}...")
    
    if not APP_API_KEY:
        issues.append("❌ CUSTOMERIO_APP_API_KEY no está configurado")
    else:
        logger.success(f"✅ App API Key: {APP_API_KEY[:8]}...")
    
    if issues:
        logger.error("\n⚠️ PROBLEMAS DE CONFIGURACIÓN:")
        for issue in issues:
            logger.error(f"   {issue}")
        logger.info("\nAgrega estas variables a tu archivo .env")
        return False
    
    logger.success("\n✅ Todas las credenciales están configuradas")
    
    # Verificar región
    logger.info(f"\n📍 Región configurada: {REGION}")
    logger.info(f"   API URL: {API_BASE_URL}")
    logger.info("\n💡 Para verificar tu región:")
    logger.info("   Ve a: https://fly.customer.io/settings/privacy")
    logger.info("   Si dice 'European Union', cambia a: REGION = Regions.EU")
    
    return True


# --- EJEMPLO DE USO ---

if __name__ == "__main__":
    # Verificar configuración primero
    if not verify_configuration():
        exit(1)
    
    USER_ID = "123456"
    USER_EMAIL = "juan.perez@ejemplo.com"

    logger.info("\n=== INICIANDO PRUEBAS ===\n")

    # PASO 1: Crear un nuevo cliente
    logger.info("--- PASO 1: Crear Cliente ---")
    #create_or_update_customer(
    #    user_id=USER_ID, email=USER_EMAIL, first_name="Juan", plan="free"
    #)

    # Esperar procesamiento (aumentado a 5 segundos)
    logger.info("\n⏳ Esperando 5 segundos para procesamiento...")
    
    #time.sleep(5)

    # PASO 2: Buscar por email (más confiable que buscar por ID)
    logger.info("\n--- PASO 2: Buscar por Email ---")
    find_customer_by_email(USER_EMAIL)

    # PASO 3: Obtener datos del cliente por ID
    logger.info("\n--- PASO 3: Obtener Cliente por ID ---")
    #get_customer(USER_ID)

    # PASO 4: Actualizar el cliente
    logger.info("\n--- PASO 4: Actualizar Cliente ---")
    #create_or_update_customer(
    #    user_id=USER_ID, email=USER_EMAIL, first_name="Juan Actualizado", plan="premium"
    #)

    time.sleep(3)

    # PASO 5: Verificar actualización
    logger.info("\n--- PASO 5: Verificar Actualización ---")
    get_customer("95b60c00090a")

    # PASO 6: Obtener solo atributos
    logger.info("\n--- PASO 6: Obtener Atributos ---")
    get_customer_attributes(USER_ID)

    # PASO 7: Registrar un evento
    logger.info("\n--- PASO 7: Registrar Evento ---")
    track_event(
        user_id=USER_ID,
        event_name="completed_purchase",
        event_data={"amount": 99.99, "product": "Premium Plan", "currency": "USD"},
    )

    # PASO 8: Buscar clientes (OPCIONAL - puede dar error 400)
    # Este endpoint requiere permisos especiales y filtros válidos
    # Solo descomenta si necesitas búsquedas avanzadas
    # logger.info("\n--- PASO 8: Buscar Clientes (opcional) ---")
    paid_users = search_customers(
    filter_query={
        "type": "and",
        "filters": [
            {
                "type": "attribute",
                "field": "plan",
                "operator": "eq",
                "value": "premium",
            },
            {
                "type": "attribute",
                "field": "subscription_status",
                "operator": "eq",
                "value": "active",
            },
        ],
    },
    limit=50,
)

    # OPCIONAL: Eliminar cliente (descomenta para probar)
    # logger.info("\n--- PASO 9: Eliminar Cliente ---")
    # delete_customer(USER_ID)

    logger.info("\n=== PRUEBAS COMPLETADAS ===")