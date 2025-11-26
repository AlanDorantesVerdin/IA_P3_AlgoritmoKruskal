import matplotlib.pyplot as plt
import networkx as nx

class KruskalVisual:
    """Clase para ejecutar y visualizar paso a paso el algoritmo de Kruskal."""
    
    def __init__(self, graph, minimize=True):
        self.graph = graph
        # Bandera para decidir si buscamos costo mínimo (True) o máximo (False)
        self.minimize = minimize
        
        # Lista para almacenar los estados (snapshots) del algoritmo
        self.steps = []
        self.current_step = 0
        
    # === Implementación del algoritmo de Kruskal con captura de pasos ===
    def kruskal_with_steps(self):
        """
        Ejecuta la lógica de Kruskal utilizando Union-Find para detección de ciclos.
        Guarda los pasos intermedios para su visualización.
        """
        
        # ------------------ PASO 1: Inicialización de Union-Find ------------------
        # Kruskal necesita gestionar conjuntos disjuntos para detectar ciclos.
        # Al inicio, cada nodo es su propio "padre" (cada nodo es un conjunto independiente).
        parent = {node: node for node in self.graph.nodes()}
        
        # 'rank' se usa para optimizar la unión de árboles (Union by Rank)
        rank = {node: 0 for node in self.graph.nodes()}
        
        # Función auxiliar: Encuentra el representante (raíz) del conjunto
        def find(node):
            if parent[node] != node:
                # Compresión de camino: apunta directamente al abuelo/raíz para aplanar el árbol
                parent[node] = find(parent[node])
            return parent[node]
        
        # Función auxiliar: Une dos conjuntos
        def union(node1, node2):
            root1 = find(node1)
            root2 = find(node2)
            
            # Si las raíces son diferentes, unimos los conjuntos
            if root1 != root2:
                # Union by Rank: el árbol más bajo se une al más alto para mantener balance
                if rank[root1] < rank[root2]:
                    parent[root1] = root2
                elif rank[root1] > rank[root2]:
                    parent[root2] = root1
                else:
                    parent[root2] = root1
                    rank[root1] += 1
                return True # Unión exitosa
            return False # Ya estaban en el mismo conjunto (formaría ciclo)
        
        # ------------------ PASO 2: Ordenamiento de Aristas ------------------
        # Extraemos todas las aristas con sus pesos
        edges = []
        for u, v, data in self.graph.edges(data=True):
            weight = data['weight']
            edges.append((weight, u, v))
        
        # Kruskal es un algoritmo 'greedy' (voraz): procesa aristas por orden de peso.
        # Ascendente para MST mínimo, Descendente para máximo.
        edges.sort(reverse=not self.minimize)
        
        # Lista final de aristas del MST y peso total
        mst_edges = []
        total_weight = 0
        
        # Guardar snapshot inicial
        mode_text = "Mínimo" if self.minimize else "Máximo"
        self.steps.append({
            'sorted_edges': edges.copy(),
            'current_edge': None,
            'mst_edges': [],
            'total_weight': 0,
            'parent': parent.copy(),
            'message': f'Inicio: Aristas ordenadas para buscar costo {mode_text}'
        })
        
        # ------------------ PASO 3: Iteración y Selección ------------------
        # Recorremos todas las aristas ordenadas
        for i, (weight, u, v) in enumerate(edges):
            
            # Guardar snapshot de evaluación (resalta la arista que se está analizando)
            self.steps.append({
                'sorted_edges': edges.copy(),
                'current_edge': (u, v, weight),
                'current_edge_index': i,
                'mst_edges': mst_edges.copy(),
                'total_weight': total_weight,
                'parent': parent.copy(),
                'message': f'Evaluando arista ({u}, {v}) con peso {weight}'
            })
            
            # Buscamos los conjuntos a los que pertenecen los nodos u y v
            root_u = find(u)
            root_v = find(v)
            
            # ------------------ PASO 4: Validación de Ciclos ------------------
            # Si las raíces son diferentes, no forman ciclo -> ACEPTAR ARISTA
            if root_u != root_v:
                # Unir los conjuntos lógicamente
                union(u, v)
                
                # Agregar arista al MST
                mst_edges.append((u, v, weight))
                total_weight += weight
                
                # Guardar snapshot de aceptación
                self.steps.append({
                    'sorted_edges': edges.copy(),
                    'current_edge': (u, v, weight),
                    'current_edge_index': i,
                    'mst_edges': mst_edges.copy(),
                    'total_weight': total_weight,
                    'parent': parent.copy(),
                    'accepted': True,
                    'message': f'✓ Arista ({u}, {v}) ACEPTADA - Conecta componentes distintos'
                })
                
                # Optimización: Si ya tenemos (V - 1) aristas, el árbol está completo
                if len(mst_edges) == len(self.graph.nodes()) - 1:
                    break
            else:
                # ------------------ PASO 5: Rechazo (Ciclo) ------------------
                # Si las raíces son iguales, los nodos ya están conectados -> RECHAZAR
                self.steps.append({
                    'sorted_edges': edges.copy(),
                    'current_edge': (u, v, weight),
                    'current_edge_index': i,
                    'mst_edges': mst_edges.copy(),
                    'total_weight': total_weight,
                    'parent': parent.copy(),
                    'rejected': True,
                    'message': f'✗ Arista ({u}, {v}) RECHAZADA - Formaría un ciclo'
                })
        
        # Guardar snapshot final con el resultado
        self.steps.append({
            'sorted_edges': edges.copy(),
            'current_edge': None,
            'mst_edges': mst_edges.copy(),
            'total_weight': total_weight,
            'parent': parent.copy(),
            'final_mst': True,
            'message': f'Proceso finalizado. Peso total del MST: {total_weight}'
        })
        
        return mst_edges, total_weight
    
    def visualize(self):
        """Prepara la visualización y muestra la interfaz interactiva."""
        
        # Ejecutar algoritmo y capturar pasos
        self.kruskal_with_steps()
        
        # Crear figura con tema oscuro
        self.fig, self.ax = plt.subplots(figsize=(14, 10), facecolor='#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        
        # Registrar eventos de teclado
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        
        # Calcular layout fijo para los nodos
        self.pos = nx.spring_layout(self.graph, seed=42, k=2)
        
        # Dibujar primer paso
        self.draw_step()
        plt.tight_layout()
        plt.show()
    
    def draw_step(self):
        """Dibuja el paso actual tomando la información desde `self.steps`."""
        
        self.ax.clear()
        
        # Asegurar índice válido
        if self.current_step >= len(self.steps):
            self.current_step = len(self.steps) - 1
        
        step = self.steps[self.current_step]
        
        # Configuración de títulos y textos
        mode_text = "Mínimo" if self.minimize else "Máximo"
        self.ax.set_title(f"\n\n\nAlgoritmo de Kruskal - Árbol de Expansión de {mode_text} Coste\n\n",
                          fontsize=16, fontweight='bold', color="#837B7B")

        self.ax.text(0.5, 0.95, f"\n\n\nPaso {self.current_step + 1}/{len(self.steps)}\n{step['message']}\n\n",
                     transform=self.ax.transAxes, ha='center', fontsize=12, color="#837B7B", fontweight='bold')

        self.ax.text(0.1, 0.05, "[Presiona → para avanzar, 'q' para salir]", 
                     transform=self.ax.transAxes, ha='center', fontsize=10, color="#837B7B")
        
        # Lógica de colores para los nodos
        node_colors = []
        nodes_in_mst = set()
        
        # Recopilar nodos que ya están conectados en el MST
        for edge in step['mst_edges']:
            nodes_in_mst.add(edge[0])
            nodes_in_mst.add(edge[1])
        
        for node in self.graph.nodes():
            # Si el nodo es parte de la arista que se evalúa actualmente
            if step['current_edge'] and node in [step['current_edge'][0], step['current_edge'][1]]:
                node_colors.append('#FF8C00')  # naranja
            # Si el nodo ya forma parte de alguna arista del MST
            elif node in nodes_in_mst:
                node_colors.append('#4169E1')  # azul
            else:
                node_colors.append('#696969')  # gris
        
        # Lógica de colores para las aristas
        edges = self.graph.edges()
        edge_colors = []
        edge_widths = []
        
        for edge in edges:
            # Verificar si la arista ya está en el MST
            in_mst = False
            for mst_edge in step['mst_edges']:
                if (edge == (mst_edge[0], mst_edge[1]) or edge == (mst_edge[1], mst_edge[0])):
                    in_mst = True
                    break
            
            if in_mst:
                edge_colors.append('#00FF7F')    # verde brillante (MST confirmado)
                edge_widths.append(4)
            # Verificar si es la arista actual bajo evaluación
            elif step['current_edge'] and (edge == (step['current_edge'][0], step['current_edge'][1]) or 
                                           edge == (step['current_edge'][1], step['current_edge'][0])):
                if 'accepted' in step:
                    edge_colors.append('#FFD700')  # dorado (aceptada)
                    edge_widths.append(5)
                elif 'rejected' in step:
                    edge_colors.append('#FF0000')  # rojo (rechazada)
                    edge_widths.append(3)
                else:
                    edge_colors.append('#FF4500')  # naranja (evaluando)
                    edge_widths.append(3)
            else:
                edge_colors.append('#555555')    # gris (inactiva)
                edge_widths.append(1)
        
        # Dibujar aristas
        nx.draw_networkx_edges(self.graph, self.pos, ax=self.ax, 
                               edge_color=edge_colors, width=edge_widths, alpha=0.6)
        
        # Dibujar nodos
        nx.draw_networkx_nodes(self.graph, self.pos, ax=self.ax,
                               node_color=node_colors, node_size=800,
                               edgecolors='white', linewidths=2)
        
        # Etiquetas
        nx.draw_networkx_labels(self.graph, self.pos, ax=self.ax,
                                font_size=12, font_weight='bold', font_color='white')
        
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, self.pos, edge_labels, ax=self.ax,
                                     font_size=10, font_color='white',
                                     bbox=dict(boxstyle='round,pad=0.3', facecolor='#2b2b2b', 
                                     edgecolor='none', alpha=0.8))
        
        # Caja de texto con el peso acumulado
        if 'final_mst' in step:
            weight_text = f"Peso total del MST: {step['total_weight']}"
        else:
            weight_text = f"Peso acumulado del MST: {step['total_weight']}"
        
        self.ax.text(0.02, 0.98, weight_text, transform=self.ax.transAxes,
                     fontsize=10, verticalalignment='center', color="#BEB1B1", fontweight='bold',
                     bbox=dict(boxstyle='round', facecolor='#404040', alpha=0.9, edgecolor="#8B8686"))
        
        # Mostrar lista de aristas pendientes (solo al principio para no saturar)
        if self.current_step <= 1 and 'sorted_edges' in step:
            edges_text = "Aristas ordenadas:\n"
            for i, (w, u, v) in enumerate(step['sorted_edges'][:8]):
                edges_text += f"({u},{v}):{w}  "
                if (i + 1) % 4 == 0:
                    edges_text += "\n"
            if len(step['sorted_edges']) > 8:
                edges_text += "..."
            
            self.ax.text(.17, .19, edges_text, transform=self.ax.transAxes,
                         fontsize=8, verticalalignment='top', horizontalalignment='right',
                         color="#BEB1B1", fontweight='bold',
                         bbox=dict(boxstyle='round', facecolor='#404040', alpha=0.9, edgecolor="#8B8686"))
        
        self.ax.axis('off')
        self.fig.canvas.draw()
    
    def on_key(self, event):
        """Manejador de eventos de teclado."""
        if event.key == 'right':
            if self.current_step < len(self.steps) - 1:
                self.current_step += 1
                self.draw_step()
        elif event.key == 'q':
            plt.close()


# ------------------ Ejemplo de uso ------------------

if __name__ == "__main__":
    # Crear grafo de ejemplo
    G = nx.Graph()
    
    edges = [
        ('A', 'B', 4), ('A', 'C', 2),
        ('B', 'C', 1), ('B', 'D', 5),
        ('C', 'D', 8), ('C', 'E', 10),
        ('D', 'E', 2), ('D', 'F', 6),
        ('E', 'F', 3)
    ]
    
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    
    # Mensajes por consola
    print("Iniciando visualización del algoritmo de Kruskal...")
    print("\nOpciones:")
    print("1. Árbol de Expansión Mínima (minimize=True)")
    print("2. Árbol de Expansión Máxima (minimize=False)")
    print("\nControles:")
    print("  → (flecha derecha): Avanzar al siguiente paso")
    print("  q: Cerrar visualización")
    
    # Ejecutar para MST Mínimo o Maximo
    kruskal_viz = KruskalVisual(G, minimize=True)
    kruskal_viz.visualize()