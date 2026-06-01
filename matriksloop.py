import random
import networkx as nx
import matplotlib.pyplot as plt

# --- 1. DEFINISI GRAF DENGAN MATRIKS KETETANGGAAN ---
INF = 999
dist_matrix = [
    # A  B  C  #  D  E  F  G  H
    [0, INF, 6, 3, INF, INF, INF, INF, INF], # A (index 0)
    [INF, 0, 9, INF, 8, INF, INF, INF, INF], # B (index 1)
    [6, 9, 0, 2, INF, INF, 4, INF, INF],     # C (index 2)
    [3, INF, 2, 0, INF, INF, INF, 5, INF],   # # (index 3)
    [INF, 8, INF, INF, 0, 7, INF, INF, 9],   # D (index 4)
    [INF, INF, INF, INF, 7, 0, 2, 1, 1],     # E (index 5)
    [INF, INF, 4, INF, INF, 2, 0, INF, INF], # F (index 6)
    [INF, INF, INF, 5, INF, 1, INF, 0, 3],   # G (index 7)
    [INF, INF, INF, INF, 9, 1, INF, 3, 0]    # H (index 8)
]

# Mapping node ke index untuk kemudahan akses
node_to_idx = {
    'A': 0, 'B': 1, 'C': 2, '#': 3,
    'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8
}

idx_to_node = {v: k for k, v in node_to_idx.items()}

# Koordinat posisi untuk visualisasi
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

# Daftar semua kota
cities = list(node_to_idx.keys())
num_cities = len(cities)

# --- 2. FUNGSI VISUALISASI ---
def draw_graph(graph, best_path=None, show_result=False, title="Traveling Salesman Problem Graph"):
    """
    Menggambar graf
    - show_result=False: graf awal (tanpa panah)
    - show_result=True: hasil optimal (hanya path merah yang ada panah)
    """
    G = nx.Graph()  # Selalu gunakan Graph untuk edge hitam (tanpa panah)
    
    # Tambahkan edge dengan bobot dari matriks
    for i in range(num_cities):
        for j in range(i+1, num_cities):  # Hanya setengah matriks karena simetris
            if dist_matrix[i][j] != INF and dist_matrix[i][j] != 0:
                city1, city2 = idx_to_node[i], idx_to_node[j]
                G.add_edge(city1, city2, weight=dist_matrix[i][j])
    
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

# Inisialisasi Feromon (menggunakan matriks)
pheromone = []
for i in range(num_cities):
    row = []
    for j in range(num_cities):
        # Inisialisasi feromon hanya jika ada jalur (bukan INF dan bukan diagonal)
        if dist_matrix[i][j] != INF and dist_matrix[i][j] != 0:
            row.append(1.0)
        else:
            row.append(0.0)
    pheromone.append(row)

# --- 4. FUNGSI BANTU ---
def get_distance(u, v):
    """Mengembalikan jarak antara dua kota menggunakan matriks"""
    idx_u = node_to_idx[u]
    idx_v = node_to_idx[v]
    dist = dist_matrix[idx_u][idx_v]
    return float('inf') if dist == INF else dist

def tour_length(tour):
    """Menghitung total jarak tour"""
    total = 0
    for i in range(len(tour)-1):
        dist = get_distance(tour[i], tour[i+1])
        if dist == float('inf'):
            return float('inf')
        total += dist
    return total

def get_pheromone(u, v):
    """Mengembalikan nilai feromon antara dua kota"""
    idx_u = node_to_idx[u]
    idx_v = node_to_idx[v]
    return pheromone[idx_u][idx_v]

def update_pheromone(u, v, delta):
    """Menambahkan delta ke feromon antara dua kota (dua arah)"""
    idx_u = node_to_idx[u]
    idx_v = node_to_idx[v]
    pheromone[idx_u][idx_v] += delta
    # Update juga reverse untuk graf tidak berarah
    pheromone[idx_v][idx_u] += delta

# --- 5. CETAK MATRIKS ---
print("="*70)
print("MATRIKS KETETANGGAAN")
print("="*70)
print("     A    B    C    #    D    E    F    G    H")
for i, row in enumerate(dist_matrix):
    node = idx_to_node[i]
    print(f"{node}: ", end="")
    for val in row:
        if val == INF:
            print("  - ", end=" ")
        else:
            print(f"{val:3} ", end=" ")
    print()

# --- 6. ALGORITMA ACO ---
best_tour = None
best_len = float('inf')

print("\n" + "="*70)
print("  ANT COLONY OPTIMIZATION - TSP (Matrix Version - Loop Style)")
print("="*70)
print(f"  Start: H (index {node_to_idx['H']}) | Must-Pass: # (index {node_to_idx['#']}) | End: D (index {node_to_idx['D']})")
print("="*70)

# Gambar graf awal (TANPA arah panah)
print("\n✅ Menampilkan visualisasi graf awal (tanpa arah panah)...")
draw_graph(dist_matrix, show_result=False, title="Graf Awal TSP - Matrix Version (Tanpa Arah Panah)")

for iteration in range(num_iterations):
    iteration_tours = []
    
    for ant in range(num_ants):
        # Mulai dari H
        current = 'H'
        visited = ['H']
        
        # Loop sampai mencapai D (seperti Program 1)
        while current != 'D':
            # Dapatkan tetangga dari matriks
            neighbors = []
            for j in range(num_cities):
                if dist_matrix[node_to_idx[current]][j] != INF and dist_matrix[node_to_idx[current]][j] != 0:
                    neighbors.append(idx_to_node[j])
            
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
                tau = get_pheromone(current, next_city)
                eta = 1.0 / get_distance(current, next_city)
                p = (tau ** alpha) * (eta ** beta)
                probs.append(p)
            
            # Pilih berdasarkan probabilitas (Roulette Wheel)
            total = sum(probs)
            if total == 0:
                next_city = random.choice(possible)
            else:
                r = random.uniform(0, total)
                cum = 0
                next_city = possible[0]  # Default
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
                    print(f"  ✅ Ditemukan rute lebih baik: {' -> '.join(visited)} (Jarak: {length})")

    # Update Feromon
    # Evaporasi
    for i in range(num_cities):
        for j in range(num_cities):
            if dist_matrix[i][j] != INF and dist_matrix[i][j] != 0:
                pheromone[i][j] *= (1 - evaporation)
    
    # Deposit
    for tour, length in iteration_tours:
        deposit = Q / length
        for i in range(len(tour)-1):
            u, v = tour[i], tour[i+1]
            update_pheromone(u, v, deposit)
    
    # Progress report setiap 10 iterasi
    if (iteration + 1) % 10 == 0:
        print(f"  📊 Iterasi {iteration+1}/{num_iterations}: Best length = {best_len}")

# --- 7. HASIL AKHIR ---
print("\n" + "="*70)
print("  🏆 HASIL OPTIMAL")
print("="*70)
if best_tour:
    print(f"  Rute Terbaik: {' -> '.join(best_tour)}")
    print(f"  Total Jarak: {best_len}")
    print(f"  Jumlah kota dikunjungi: {len(best_tour)}")
    
    # Verifikasi rute menggunakan matriks
    print("\n  📋 Verifikasi Rute (menggunakan matriks):")
    total_check = 0
    for i in range(len(best_tour)-1):
        dist = get_distance(best_tour[i], best_tour[i+1])
        print(f"    {best_tour[i]} ({node_to_idx[best_tour[i]]}) -> {best_tour[i+1]} ({node_to_idx[best_tour[i+1]]}): {dist}")
        total_check += dist
    print(f"    Total terverifikasi: {total_check}")
    
    # Gambar graf dengan rute terbaik (HANYA garis merah yang ada arah panah)
    print("\n✅ Menampilkan visualisasi rute optimal (hanya garis merah dengan arah panah)...")
    draw_graph(dist_matrix, best_tour, show_result=True, title="Rute Optimal TSP - Matrix Version (Hanya Garis Merah dengan Arah Panah)")
else:
    print("  ❌ Tidak ditemukan rute valid. Coba jalankan ulang program.")

# --- 8. TAMPILKAN MATRIKS FEROMON AKHIR ---
print("\n" + "="*70)
print("MATRIKS FEROMON AKHIR")
print("="*70)
print("        A         B         C         #         D         E         F         G         H")
for i, row in enumerate(pheromone):
    node = idx_to_node[i]
    print(f"{node}: ", end="")
    for val in row:
        print(f"{val:8.4f} ", end="")
    print()