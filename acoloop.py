import random
import networkx as nx
import matplotlib.pyplot as plt

# --- 1. DEFINISI GRAF SESUAI GAMBAR ---
graph_data = {
    'A': {'#': 3, 'C': 6}, 
    'B': {'C': 9, 'D': 8},
    'C': {'A': 6, '#': 2, 'F': 4, 'B': 9},
    'D': {'H': 9, 'E': 7, 'B': 8},
    'E': {'D': 7, 'F': 2, 'G': 1, 'H': 1},
    'F': {'C': 4, 'E': 2},
    'G': {'#': 5, 'E': 1, 'H': 3},
    'H': {'D': 9, 'E': 1, 'G': 3},
    '#': {'A': 3, 'G': 5, 'C': 2}
}

# --- 2. FUNGSI VISUALISASI ---
def draw_graph(graph, best_path=None, show_result=False, title="Traveling Salesman Problem Graph"):
    """
    Menggambar graf
    - show_result=False: graf awal (tanpa panah)
    - show_result=True: hasil optimal (hanya path merah yang ada panah)
    """
    G = nx.Graph()  # Selalu gunakan Graph untuk edge hitam (tanpa panah)
    
    # Tambahkan edge dengan bobot
    for node, neighbors in graph.items():
        for neighbor, weight in neighbors.items():
            G.add_edge(node, neighbor, weight=weight)
    
    # Setup posisi node
    pos = {
        'A': (0, 2),      # Kiri atas
        'B': (0.5, 0),    # Kiri bawah
        'C': (1.5, 1.5),  # Tengah kiri
        'D': (2.5, 0.5),  # Tengah bawah
        'E': (4, 1.5),    # Tengah kanan
        'F': (3.5, 2.5),  # Kanan atas
        'G': (5, 3),      # Kanan atas ekstrem
        'H': (5, 0),      # Kanan bawah
        '#': (2, 3)       # Puncak tengah
    }
    
    plt.figure(figsize=(14, 10))
    
    # Gambar semua node
    nx.draw_networkx_nodes(G, pos, node_size=800, node_color='lightblue', edgecolors='black')
    
    # Highlight node khusus
    nx.draw_networkx_nodes(G, pos, nodelist=['H'], node_color='green', node_size=800, edgecolors='black', label='Start (H)')
    nx.draw_networkx_nodes(G, pos, nodelist=['D'], node_color='red', node_size=800, edgecolors='black', label='End (D)')
    nx.draw_networkx_nodes(G, pos, nodelist=['#'], node_color='orange', node_size=800, edgecolors='black', label='Must Pass (#)')
    
    # Gambar edge hitam (selalu tanpa arah panah)
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.6)
    
    # Label node
    nx.draw_networkx_labels(G, pos, font_size=14, font_weight='bold')
    
    # Tampilkan bobot edge
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=11, font_color='blue')
    
    # Jika ada best path dan show_result=True, highlight path dengan warna merah dan arah panah
    if best_path and show_result:
        # Buat graf berarah khusus untuk path merah
        path_edges = [(best_path[i], best_path[i+1]) for i in range(len(best_path)-1)]
        
        # Gambar path merah dengan arah panah (menggunakan DiGraph)
        G_path = nx.DiGraph()
        G_path.add_edges_from(path_edges)
        nx.draw_networkx_edges(G_path, pos, edgelist=path_edges, width=4, edge_color='red', 
                               arrows=True, arrowsize=35, arrowstyle='->', label='Optimal Path')
    
    plt.title(title, fontsize=16, fontweight='bold')
    plt.axis('off')
    plt.legend(loc='upper left', fontsize=12)
    plt.tight_layout()
    plt.show()

# --- 3. PARAMETER ACO ---
num_ants = 20
num_iterations = 40
alpha = 1.0
beta = 2.0
evaporation = 0.5
Q = 100

# Inisialisasi Feromon
pheromone = {i: {j: 1.0 for j in graph_data[i]} for i in graph_data}

# --- 4. FUNGSI BANTU ---
def get_distance(u, v):
    return graph_data[u].get(v, float('inf'))

def tour_length(tour):
    total = 0
    for i in range(len(tour)-1):
        dist = get_distance(tour[i], tour[i+1])
        if dist == float('inf'):
            return float('inf')
        total += dist
    return total

# --- 5. ALGORITMA ACO ---
best_tour = None
best_len = float('inf')

print("="*60)
print("  ANT COLONY OPTIMIZATION - TSP")
print("="*60)
print(f"  Start: H | Must-Pass: # | End: D")
print("="*60)

# Gambar graf awal (TANPA arah panah)
print("\n✅ Menampilkan visualisasi graf awal (tanpa arah panah)...")
draw_graph(graph_data, show_result=False, title="Graf Awal TSP (Tanpa Arah Panah)")

for iteration in range(num_iterations):
    iteration_tours = []
    
    for ant in range(num_ants):
        # Mulai dari H
        current = 'H'
        visited = ['H']
        
        # Loop sampai mencapai D
        while current != 'D':
            # Dapatkan tetangga
            neighbors = list(graph_data[current].keys())
            
            # FILTER 1: Jangan balik ke kota yang sudah dikunjungi
            possible = [n for n in neighbors if n not in visited]
            
            # FILTER 2: LOGIKA "WAJIB #"
            # Jika # BELUM dikunjungi, jangan pilih D sebagai tujuan sekarang
            if '#' not in visited:
                possible = [n for n in possible if n != 'D']
            
            # Fallback: Jika tidak ada pilihan, ambil tetangga yang ada
            if not possible:
                possible = neighbors
            
            # Hitung Probabilitas
            probs = []
            for next_city in possible:
                tau = pheromone[current][next_city]
                eta = 1.0 / graph_data[current][next_city]
                p = (tau ** alpha) * (eta ** beta)
                probs.append(p)
            
            # Pilih berdasarkan probabilitas (Roulette Wheel)
            total = sum(probs)
            if total == 0:
                next_city = random.choice(possible)
            else:
                r = random.uniform(0, total)
                cum = 0
                for i, p in enumerate(probs):
                    cum += p
                    if r <= cum:
                        next_city = possible[i]
                        break
            
            current = next_city
            visited.append(current)
            
            # Cek kondisi berhenti
            if current == 'D' and '#' in visited:
                break
        
        # Validasi Tour
        if visited[0] == 'H' and visited[-1] == 'D' and '#' in visited:
            length = tour_length(visited)
            if length != float('inf'):
                iteration_tours.append((visited, length))
                
                if length < best_len:
                    best_len = length
                    best_tour = visited

    # Update Feromon
    # Evaporasi
    for i in graph_data:
        for j in graph_data[i]:
            pheromone[i][j] *= (1 - evaporation)
    
    # Deposit
    for tour, length in iteration_tours:
        deposit = Q / length
        for i in range(len(tour)-1):
            u, v = tour[i], tour[i+1]
            pheromone[u][v] += deposit
            # Update juga reverse untuk graf tidak berarah
            if v in pheromone and u in pheromone[v]:
                pheromone[v][u] += deposit
    
    # Progress report setiap 10 iterasi
    if (iteration + 1) % 10 == 0:
        print(f"  Iterasi {iteration+1}/{num_iterations}: Best length = {best_len}")

# --- 6. HASIL AKHIR ---
print("\n" + "="*60)
print("  🏆 HASIL OPTIMAL")
print("="*60)
if best_tour:
    print(f"  Rute Terbaik: {' -> '.join(best_tour)}")
    print(f"  Total Jarak: {best_len}")
    print(f"  Jumlah kota dikunjungi: {len(best_tour)}")
    
    # Gambar graf dengan rute terbaik (HANYA garis merah yang ada arah panah)
    print("\n✅ Menampilkan visualisasi rute optimal (hanya garis merah dengan arah panah)...")
    draw_graph(graph_data, best_tour, show_result=True, title="Rute Optimal TSP (Hanya Garis Merah dengan Arah Panah)")
else:
    print("  ❌ Tidak ditemukan rute valid. Coba jalankan ulang program.")