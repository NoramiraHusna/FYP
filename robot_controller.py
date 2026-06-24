import os
# PROTOBUF COLLISION FIX
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import sys
import asyncio
import threading
import logging
import mini.mini_sdk as MiniSdk
from mini.dns.dns_browser import WiFiDevice
from mini.apis.api_setup import StartRunProgram
from mini.apis.api_sound import StartPlayTTS

# ULTIMATE MAGIC PATCH FOR PYTHON 3.10+
if sys.version_info >= (3, 10):
    for name in ('Lock', 'Event', 'Condition', 'Semaphore', 'BoundedSemaphore', 'Queue'):
        original = getattr(asyncio, name, None)
        if original:
            def create_patched(orig):
                def patched(*args, **kwargs):
                    kwargs.pop('loop', None)
                    return orig(*args, **kwargs)
                return patched
            setattr(asyncio, name, create_patched(original))
    
    _orig_sleep = asyncio.sleep
    def patched_sleep(*args, **kwargs):
        kwargs.pop('loop', None)
        return _orig_sleep(*args, **kwargs)
    asyncio.sleep = patched_sleep

    _orig_wait = asyncio.wait
    def patched_wait(*args, **kwargs):
        kwargs.pop('loop', None)
        return _orig_wait(*args, **kwargs)
    asyncio.wait = patched_wait
    
    _orig_wait_for = asyncio.wait_for
    def patched_wait_for(*args, **kwargs):
        kwargs.pop('loop', None)
        return _orig_wait_for(*args, **kwargs)
    asyncio.wait_for = patched_wait_for

class RobotController:
    def __init__(self):
        self.is_connected = False
        self.is_speaking = False 
        
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.thread.start()
        
        MiniSdk.set_log_level(logging.INFO) 
        MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.speech_queue = asyncio.Queue() 
        self.loop.create_task(self._speech_worker()) 
        self.loop.run_forever()

    def connect(self):
        asyncio.run_coroutine_threadsafe(self._async_connect(), self.loop)

    async def _async_connect(self):
        print("🔌 Connecting to Alpha Mini for the game...")
        device = WiFiDevice.__new__(WiFiDevice)
        device.name = "Edu_EAA005UBT00000107"
        device.address = "172.20.10.3" 
        device.ip = "172.20.10.3"
        device.port = 50634

        try:
            await MiniSdk.connect(device)
            await StartRunProgram().execute()
            await asyncio.sleep(2)
            self.is_connected = True
            print("✅ Alpha Mini is locked in and ready for the simulation!")
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            self.is_connected = False

    def speak(self, tone, line_1, line_2=None):
        full_text = line_1
        if line_2:
            full_text += " " + line_2
            
        print(f"\n[{tone.upper()} ROBOT]: {full_text}\n")
        
        if self.is_connected:
            self.loop.call_soon_threadsafe(self.speech_queue.put_nowait, full_text)

    async def _speech_worker(self):
        while True:
            text = await self.speech_queue.get() 
            self.is_speaking = True 
            try:
                print("🗣️ Executing speech command...")
                await StartPlayTTS(text=text).execute()
                
                # ⚡ MAXIMUM SPEED UPGRADE: Wait for exact completion + 0.5s pause
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Speech error: {e}")
            finally:
                self.is_speaking = False 
                self.speech_queue.task_done()