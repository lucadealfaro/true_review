# This file defines a key-value table for storing large blobs of text and similar.

# key-value table for defining large blobs.
gdb.define_table('keyval',
                 Field('cont', 'blob'))

# Functions for storing text
def text_store_read(k):
    """Reads a keystore value for key k."""
    return gdb.keyval(k).cont

def text_store_write(v, key=None):
    """Writes a text store value of v, with key k if specified.  Returns the key."""
    if key is None:
        return gdb.keyval.insert(cont=v)
    else:
        kk = int(key)
        gdb.keyval.update_or_insert((gdb.keyval.id == kk), id=kk, cont=v)
        return kk

def represent_text_field(v, r):
    return text_store_read(int(v))
