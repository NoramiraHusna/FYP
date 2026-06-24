import sys
import asyncio

# --- ULTIMATE MAGIC PATCH FOR PYTHON 3.10+ ---
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
    
    # NEW: Patching the wait_for command that crashed the disconnect!
    _orig_wait_for = asyncio.wait_for
    def patched_wait_for(*args, **kwargs):
        kwargs.pop('loop', None)
        return _orig_wait_for(*args, **kwargs)
    asyncio.wait_for = patched_wait_for
# ---------------------------------------------

import logging
import mini.mini_sdk as MiniSdk
from mini.dns.dns_browser import WiFiDevice
from mini.apis.api_setup import StartRunProgram
from mini.apis.api_sound import StartPlayTTS

async def test_robot():
    MiniSdk.set_log_level(logging.INFO)
    MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)

    print("🚀 Bypassing the buggy scanner...")
    print("🔌 Connecting directly to IP: 172.20.10.3...")

    device = WiFiDevice.__new__(WiFiDevice)
    device.name = "Edu_EAA005UBT00000107"
    device.address = "172.20.10.3" 
    device.ip = "172.20.10.3"
    device.port = 50634

    try:
        await MiniSdk.connect(device)
        print("✅ Successfully Connected to Alpha Mini!")
        
        print("⚙️ Entering programming mode...")
        await StartRunProgram().execute()
        await asyncio.sleep(2)
        
        print("🗣️ Sending speech command...")
        await StartPlayTTS(text="Hello! The direct IP connection is a complete success!").execute()
        
        # Give the robot 6 seconds to actually finish speaking before we hang up!
        print("⏳ Waiting for Alpha Mini to finish speaking...")
        await asyncio.sleep(6) 
        
        print("👋 Disconnecting...")
        await MiniSdk.release()
        print("🎉 Test Complete!")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_robot())