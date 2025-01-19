import time
import pymem
import ctypes
from ctypes import wintypes

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ('BaseAddress', ctypes.c_void_p),
        ('AllocationBase', ctypes.c_void_p),
        ('AllocationProtect', wintypes.DWORD),
        ('RegionSize', ctypes.c_size_t),
        ('State', wintypes.DWORD),
        ('Protect', wintypes.DWORD),
        ('Type', wintypes.DWORD),
    ]

MEM_COMMIT = 0x1000
MEM_PRIVATE = 0x20000
PAGE_READWRITE = 0x04

def get_memory_regions(handle):
    mbi = MEMORY_BASIC_INFORMATION()
    address, regions = 0, []
    while ctypes.windll.kernel32.VirtualQueryEx(handle, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)):
        if mbi.State == MEM_COMMIT and mbi.Type == MEM_PRIVATE:
            regions.append({'BaseAddress': mbi.BaseAddress, 'RegionSize': mbi.RegionSize, 'Protect': mbi.Protect})
        address += mbi.RegionSize
    return regions

def main():
    time.sleep(10) # for bloxstrap auto start thingy
    process = None
    while process is None:
        try: process = pymem.Pymem('RobloxPlayerBeta.exe')
        except: time.sleep(0.1)
    watched_memory_pool = None
    while watched_memory_pool is None:
        for mem_region in get_memory_regions(process.process_handle):
            if mem_region['Protect'] == PAGE_READWRITE and mem_region['RegionSize'] == 0x200000:
                watched_memory_pool = mem_region['BaseAddress']
                print(f"[info] Found watched memory pool at 0x{watched_memory_pool:x}, {mem_region['RegionSize']} bytes")
                break
        if not watched_memory_pool: time.sleep(0.1)
    process.write_int(watched_memory_pool + 0x208, 0x20)
    print(f"[info] modified memory at 0x{watched_memory_pool + 0x208:x}")
    input("press enter to exit")

if __name__ == "__main__": main()
