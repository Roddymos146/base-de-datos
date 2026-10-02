La base de datos es ficticia y se encuentra en vuelos.txt.
Cada línea tiene el formato: origen;destino;precio_usd
"""

from heapq import heappop, heappush
from pathlib import Path
from time import perf_counter_ns


class GrafoVuelos:
    """Grafo dirigido y ponderado: los vértices son aeropuertos
    y las aristas son vuelos con el precio como peso.
    """

    def _init_(self):
        self.adyacencia = {}

    def agregar_aeropuerto(self, aeropuerto):
        self.adyacencia.setdefault(aeropuerto, [])

    def agregar_vuelo(self, origen, destino, precio):
        self.agregar_aeropuerto(origen)
        self.agregar_aeropuerto(destino)
        self.adyacencia[origen].append((destino, precio))

    @classmethod
    def cargar_desde_archivo(cls, nombre_archivo):
        grafo = cls()
        with open(nombre_archivo, "r", encoding="utf-8") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                partes = [p.strip() for p in linea.split(";")]
                if len(partes) != 3:
                    raise ValueError(
                        f"Línea {numero_linea}: se esperaban 3 campos."
                    )
                origen, destino, precio = partes
                try:
                    precio = float(precio)
                except ValueError as exc:
                    raise ValueError(
                        f"Línea {numero_linea}: precio no válido."
                    ) from exc
                if precio <= 0:
                    raise ValueError(
                        f"Línea {numero_linea}: el precio debe ser positivo."
                    )
                grafo.agregar_vuelo(origen.upper(), destino.upper(), precio)
        return grafo

    def listar_vuelos(self):
        vuelos = []
        for origen in sorted(self.adyacencia):
            for destino, precio in sorted(self.adyacencia[origen]):
                vuelos.append((origen, destino, precio))
        return vuelos

    def consultar_aeropuerto(self, aeropuerto):
        aeropuerto = aeropuerto.upper()
        return sorted(self.adyacencia.get(aeropuerto, []))

    def dijkstra(self, origen, destino):
        """Encuentra la ruta de menor costo acumulado.
        Requiere pesos no negativos; los precios cumplen esa condición.
        """
        origen, destino = origen.upper(), destino.upper()
        if origen not in self.adyacencia or destino not in self.adyacencia:
            return None, float("inf")

        distancias = {nodo: float("inf") for nodo in self.adyacencia}
        anteriores = {nodo: None for nodo in self.adyacencia}
        distancias[origen] = 0.0

        cola = [(0.0, origen)]

        while cola:
            distancia_actual, actual = heappop(cola)

            if distancia_actual > distancias[actual]:
                continue

            if actual == destino:
                break

            for vecino, precio in self.adyacencia[actual]:
                nueva_distancia = distancia_actual + precio
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    anteriores[vecino] = actual
                    heappush(cola, (nueva_distancia, vecino))

        if distancias[destino] == float("inf"):
            return None, float("inf")

        ruta = []
        actual = destino
        while actual is not None:
            ruta.append(actual)
            actual = anteriores[actual]
        ruta.reverse()

        return ruta, distancias[destino]

    def reporte(self):
        vuelos = self.listar_vuelos()
        print("\n========== REPORTERÍA DEL GRAFO ==========")
        print(f"Aeropuertos (vértices): {len(self.adyacencia)}")
        print(f"Vuelos (aristas):       {len(vuelos)}")
        print("\nListado de vuelos:")
        for origen, destino, precio in vuelos:
            print(f"  {origen} -> {destino} : ${precio:.2f}")

    def reporte_aeropuerto(self, aeropuerto):
        aeropuerto = aeropuerto.upper()
        vuelos = self.consultar_aeropuerto(aeropuerto)
        print(f"\nVuelos desde {aeropuerto}:")
        if not vuelos:
            print("  No existen vuelos registrados.")
            return
        for destino, precio in vuelos:
            print(f"  {aeropuerto} -> {destino} : ${precio:.2f}")


def buscar_vuelo_barato(grafo, origen, destino):
    inicio = perf_counter_ns()
    ruta, costo = grafo.dijkstra(origen, destino)
    fin = perf_counter_ns()
    tiempo_ns = fin - inicio

    print("\n========== CONSULTA DE VUELO BARATO ==========")
    if ruta is None:
        print(f"No existe una ruta disponible entre {origen.upper()} y {destino.upper()}.")
    else:
        print("Ruta encontrada:", " -> ".join(ruta))
        print(f"Costo total: ${costo:.2f}")
        print(f"Cantidad de tramos: {len(ruta) - 1}")
    print(f"Tiempo de Dijkstra: {tiempo_ns} ns ({tiempo_ns / 1_000_000:.6f} ms)")
    return ruta, costo, tiempo_ns


def menu(grafo):
    while True:
        print("\n" + "=" * 48)
        print("      SISTEMA DE VUELOS BARATOS - GRAFO")
        print("=" * 48)
        print("1. Mostrar reportería completa")
        print("2. Consultar vuelos desde un aeropuerto")
        print("3. Buscar ruta más económica")
        print("4. Salir")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            grafo.reporte()

        elif opcion == "2":
            aeropuerto = input("Ingrese código del aeropuerto (ej. UIO): ").strip()
            grafo.reporte_aeropuerto(aeropuerto)

        elif opcion == "3":
            origen = input("Aeropuerto de origen: ").strip()
            destino = input("Aeropuerto de destino: ").strip()
            buscar_vuelo_barato(grafo, origen, destino)

        elif opcion == "4":
            print("Programa finalizado.")
            break

        else:
            print("Opción no válida. Intente nuevamente.")


def main():
    archivo = Path(_file_).with_name("vuelos.txt")
    if not archivo.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {archivo}")

    inicio_carga = perf_counter_ns()
    grafo = GrafoVuelos.cargar_desde_archivo(archivo)
    fin_carga = perf_counter_ns()

    print("Base de datos cargada correctamente.")
    print(f"Tiempo de carga: {(fin_carga - inicio_carga) / 1_000_000:.6f} ms")

    # Demostración automática para facilitar la evidencia del funcionamiento.
    grafo.reporte()
    buscar_vuelo_barato(grafo, "UIO", "MAD")

    # Para usar el sistema de manera interactiva, descomentar:
    # menu(grafo)


if _name_ == "_main_":
    main()