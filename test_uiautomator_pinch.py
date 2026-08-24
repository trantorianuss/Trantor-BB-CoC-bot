import uiautomator2 as u2

DEVICE = "emulator-5554"

d = u2.connect(DEVICE)

print("Conectado a LDPlayer")

stage = d(resourceId="com.supercell.clashofclans:id/stage")

print("Stage encontrado:")
print(stage.info)

print("Ejecutando pinch...")

stage.gesture(
    (750, 457),   # dedo 1 inicial
    (509, 698),   # dedo 2 inicial
    (650, 520),   # dedo 1 final
    (600, 620),   # dedo 2 final
    steps=20
)

print("Pinch terminado")
