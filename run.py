#!/usr/bin/env python
"""
Script de inicio rápido para AstroDebt
Verifica dependencias y ejecuta el juego
"""

import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 13:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ⚠️  Python {version.major}.{version.minor}.{version.micro} detectado")
        print(f"   Se recomienda Python 3.13.7")
        return True  # No bloqueamos, solo advertimos


def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print("\n📦 Verificando dependencias...")
    
    try:
        import pygame
        print(f"   ✅ Pygame {pygame.version.ver} instalado")
    except ImportError:
        print("   ❌ Pygame no encontrado")
        print("\n   Para instalar: pip install -r requirements.txt")
        return False
    
    return True


def check_data_files():
    """Verifica que los archivos de datos existan"""
    print("\n📁 Verificando archivos de datos...")
    
    required_files = [
        "data/config.json",
        "data/localization.json",
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} no encontrado")
            all_exist = False
    
    return all_exist


def check_modules():
    """Verifica que los módulos principales existan"""
    print("\n🔧 Verificando módulos del juego...")
    
    required_modules = [
        "engine",
        "finance",
        "gameplay",
        "ui",
    ]
    
    all_exist = True
    for module in required_modules:
        if Path(module).is_dir() and Path(module, "__init__.py").exists():
            print(f"   ✅ {module}/")
        else:
            print(f"   ❌ {module}/ no encontrado o incompleto")
            all_exist = False
    
    return all_exist


def show_info():
    """Muestra información del juego"""
    print("\n" + "="*60)
    print("🚀 AstroDebt - Nave Varada")
    print("="*60)
    print("Juego educativo sobre finanzas personales")
    print("Versión: 0.1.0 (Esqueleto)")
    print("="*60 + "\n")


def run_tests():
    """Ejecuta las pruebas unitarias"""
    print("\n🧪 Ejecutando pruebas...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                          capture_output=False)
    return result.returncode == 0


def run_game():
    """Ejecuta el juego"""
    print("\n🎮 Iniciando AstroDebt...\n")
    print("="*60 + "\n")
    
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Juego interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al ejecutar el juego: {e}")
        return False
    
    return True


def main():
    """Función principal"""
    show_info()
    
    # Cambiar al directorio del script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Verificaciones
    checks = [
        check_python_version(),
        check_dependencies(),
        check_data_files(),
        check_modules(),
    ]
    
    if not all(checks):
        print("\n❌ Algunas verificaciones fallaron.")
        print("   Por favor, revisa los errores arriba.\n")
        sys.exit(1)
    
    print("\n✅ Todas las verificaciones pasaron!")
    
    # Preguntar si desea ejecutar tests
    print("\n¿Deseas ejecutar las pruebas primero? (s/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            if not run_tests():
                print("\n⚠️  Algunas pruebas fallaron. ¿Continuar de todas formas? (s/n): ", end="")
                response = input().lower().strip()
                if response not in ['s', 'si', 'sí', 'y', 'yes']:
                    print("\n👋 Ejecución cancelada")
                    sys.exit(0)
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Ejecución cancelada")
        sys.exit(0)
    
    # Ejecutar juego
    run_game()
    
    print("\n" + "="*60)
    print("👋 Gracias por jugar AstroDebt!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

