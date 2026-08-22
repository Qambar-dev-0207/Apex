import psutil
from src.core.models import SystemVitals

class HardwareMonitor:
    """
    Monitors local system resources.
    """
    def __init__(self, temp_threshold: float = 85.0):
        self.temp_threshold = temp_threshold

    def get_vitals(self) -> SystemVitals:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        
        # Temperature (Best effort)
        temp = None
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Take the first available core temp
                    core_temps = list(temps.values())[0]
                    if core_temps:
                        temp = core_temps[0].current
        except:
            pass

        # GPU (Stub for pynvml integration)
        gpu = None
        
        status = "nominal"
        if cpu > 90 or (temp and temp > self.temp_threshold):
            status = "critical"
        elif cpu > 70 or ram > 85:
            status = "warning"
            
        return SystemVitals(
            cpu_percent=cpu,
            gpu_percent=gpu,
            ram_percent=ram,
            temperature=temp,
            status=status
        )

    def is_throttling_required(self) -> bool:
        vitals = self.get_vitals()
        return vitals.status == "critical"
