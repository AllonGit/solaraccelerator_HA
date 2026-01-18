"""Constants for the Solar Accelerator integration."""

DOMAIN = "solaraccelerator"

# Config flow
CONF_API_KEY = "api_key"
CONF_SERVER_URL = "server_url"
CONF_SEND_INTERVAL = "send_interval"
CONF_ENTITY_MAPPING = "entity_mapping"

# Default values
DEFAULT_SERVER_URL = "https://solaraccelerator.cloud"
DEFAULT_SEND_INTERVAL = 60  # 1 minute in seconds

# Sensor attributes
ATTR_LAST_SENT = "last_sent"
ATTR_LAST_RECEIVED = "last_received"
ATTR_CONNECTION_STATUS = "connection_status"
ATTR_ENTITIES_COUNT = "entities_count"

# API endpoint
API_PUSH_ENDPOINT = "/api/push/homeassistant"

# All 36 required entities for SolarAccelerator API
# Format: (key, description, unit, category)
REQUIRED_ENTITIES = [
    # PV (Panele fotowoltaiczne)
    ("day_pv_energy", "Dzienna produkcja PV", "kWh", "pv"),
    ("pv1_power", "Moc PV string 1", "W", "pv"),
    ("pv2_power", "Moc PV string 2", "W", "pv"),
    ("pv1_voltage", "Napięcie PV string 1", "V", "pv"),
    ("pv2_voltage", "Napięcie PV string 2", "V", "pv"),
    ("pv1_current", "Prąd PV string 1", "A", "pv"),
    ("pv2_current", "Prąd PV string 2", "A", "pv"),
    ("total_pv_generation", "Całkowita generacja PV", "kWh", "pv"),

    # Bateria
    ("day_battery_discharge", "Dzienne rozładowanie baterii", "kWh", "battery"),
    ("day_battery_charge", "Dzienne ładowanie baterii", "kWh", "battery"),
    ("battery_power", "Moc baterii (+ ładowanie, - rozładowanie)", "W", "battery"),
    ("battery_current", "Prąd baterii", "A", "battery"),
    ("battery_temp", "Temperatura baterii", "°C", "battery"),
    ("battery_voltage", "Napięcie baterii", "V", "battery"),
    ("battery_soc", "Stan naładowania baterii", "%", "battery"),
    ("battery_soh", "Stan zdrowia baterii", "%", "battery"),

    # Inwerter
    ("inverter_status", "Status inwertera", "-", "inverter"),
    ("inverter_voltage_l1", "Napięcie L1", "V", "inverter"),
    ("inverter_voltage_l2", "Napięcie L2", "V", "inverter"),
    ("inverter_voltage_l3", "Napięcie L3", "V", "inverter"),
    ("inverter_current_l1", "Prąd L1", "A", "inverter"),
    ("inverter_current_l2", "Prąd L2", "A", "inverter"),
    ("inverter_current_l3", "Prąd L3", "A", "inverter"),
    ("inverter_power", "Moc inwertera", "W", "inverter"),

    # Sieć
    ("grid_power", "Moc sieci (+ pobór, - oddawanie)", "W", "grid"),
    ("grid_ct_power_l1", "Moc CT L1", "W", "grid"),
    ("grid_ct_power_l2", "Moc CT L2", "W", "grid"),
    ("grid_ct_power_l3", "Moc CT L3", "W", "grid"),
    ("day_grid_import", "Dzienny pobór z sieci", "kWh", "grid"),
    ("day_grid_export", "Dzienne oddanie do sieci", "kWh", "grid"),
    ("grid_connected_status", "Status połączenia z siecią", "bool", "grid"),

    # Obciążenie
    ("day_load_energy", "Dzienne zużycie", "kWh", "load"),
    ("load_power_l1", "Moc obciążenia L1", "W", "load"),
    ("load_power_l2", "Moc obciążenia L2", "W", "load"),
    ("load_power_l3", "Moc obciążenia L3", "W", "load"),
    ("load_frequency", "Częstotliwość sieci", "Hz", "load"),

    # Temperatury
    ("radiator_temp", "Temperatura radiatora", "°C", "temp"),
    ("dc_transformer_temp", "Temperatura transformatora DC", "°C", "temp"),
]

# Entity keys for easy access
ENTITY_KEYS = [entity[0] for entity in REQUIRED_ENTITIES]

# Grouped entities by category
ENTITY_CATEGORIES = {
    "pv": "Panele fotowoltaiczne (PV)",
    "battery": "Bateria",
    "inverter": "Inwerter",
    "grid": "Sieć",
    "load": "Obciążenie",
    "temp": "Temperatury",
}
