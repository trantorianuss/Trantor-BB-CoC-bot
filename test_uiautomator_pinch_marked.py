import cv2
import uiautomator2 as u2

DEVICE = "emulator-5554"

P1 = (1140, 340)  # dedo 1 inicial
P2 = ( 140, 340)  # dedo 2 inicial
P3 = ( 940, 340)  # dedo 1 final
P4 = ( 340, 340)  # dedo 2 final


def mark_point(image, point, label):
    x, y = point
    cv2.circle(image, point, 12, (0, 0, 255), -1)
    cv2.putText(image, label, (x + 15, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)


def main():
    d = u2.connect(DEVICE)
    print("Conectado a LDPlayer")

    stage = d(resourceId="com.supercell.clashofclans:id/stage")
    print("Stage encontrado:")
    print(stage.info)

    print("Haciendo screenshot y marcando puntos...")
    image = d.screenshot(format="opencv")

    mark_point(image, P1, "P1 750,457")
    mark_point(image, P2, "P2 509,698")
    mark_point(image, P3, "P3 650,520")
    mark_point(image, P4, "P4 600,620")

    cv2.line(image, P1, P3, (0, 255, 0), 3)
    cv2.line(image, P2, P4, (255, 0, 0), 3)

    filename = "zoom_points.png"
    cv2.imwrite(filename, image)
    print(f"Imagen guardada: {filename}")
    print("Ahora puedes comprobar dónde caen los 4 puntos.")

    input("Pulsa ENTER para ejecutar el pinch...")

    print("Ejecutando pinch...")
    stage.gesture(P1, P2, P3, P4, steps=20)
    print("Pinch terminado")


if __name__ == "__main__":
    main()
