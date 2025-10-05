#!/usr/bin/env python
"""
Script de prueba para el juego Nave Varada
Ejecuta el juego en modo de desarrollo
"""

import sys
import os

# Asegurar que el directorio del proyecto esté en el path
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Importar y ejecutar el juego
from main import main

if __name__ == "__main__":
    print("=" * 50)
    print("NAVE VARADA - Juego Educativo")
    print("=" * 50)
    print("\nControles:")
    print("  [M] - Minar materiales (costo: 2 oxígeno)")
    print("  [R] - Reparar nave (costo: 3 oxígeno + 5-10 materiales)")
    print("  [I] - Ver inventario")
    print("  [D] - Ver deudas")
    print("  [P] - Ver progreso de reparación")
    print("  [ESPACIO] - Avanzar diálogos")
    print("  [ESC] - Cerrar paneles / Saltar diálogos")
    print("\nObjetivo: Reparar tu nave al 100% antes de quedarte sin oxígeno")
    print("\nConcepto educativo:")
    print("  - Oxígeno = Dinero (moneda del juego)")
    print("  - Materiales = Trabajo (lo que produces)")
    print("  - Préstamos se piden en oxígeno, se pagan en materiales")
    print("\n" + "=" * 50)
    print("\nIniciando juego...\n")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nJuego interrumpido por el usuario")
    except Exception as e:
        print(f"\n\nError al ejecutar el juego: {e}")
        import traceback
        traceback.print_exc()
