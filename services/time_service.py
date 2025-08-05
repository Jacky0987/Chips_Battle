import threading
import time
from core.event_bus import EventBus

class TimeService:
    def __init__(self, event_bus: EventBus, tick_interval: int = 60):
        self.event_bus = event_bus
        self.tick_interval = tick_interval
        self.is_running = False
        self.thread = None

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._tick_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.is_running = False

    def _tick_loop(self):
        while self.is_running:
            self.event_bus.publish("TimeTickEvent", {"timestamp": time.time()})
            time.sleep(self.tick_interval) 