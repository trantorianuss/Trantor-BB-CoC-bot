# Estado compartido de runtime para el bot

bh_pos = None
bh_size = None
bh_scale = None
bh_zoom = None

def set_calibration(pos, size, scale, zoom):
    """Actualizar el estado de calibración del BH."""
    global bh_pos, bh_size, bh_scale, bh_zoom
    bh_pos = pos
    bh_size = size
    bh_scale = scale
    bh_zoom = zoom
