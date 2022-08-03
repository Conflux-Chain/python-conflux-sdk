
from curses import meta
from typing import Any


def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

class Hash32StrMeta(type):
    def __instancecheck__(self, __instance: Any) -> bool:
        return isinstance(__instance, str) and \
            is_hex(__instance) and \
                len(__instance) == 66 # with prefix 0x

class Hash32Str(str, metaclass=Hash32StrMeta):
    pass
                
if __name__ == "__main__":
    print(isinstance('0x0514fc4dfde898ca5eeef304e25c0f322b19d3da83113c5c12835de65fe525ac', Hash32Str))