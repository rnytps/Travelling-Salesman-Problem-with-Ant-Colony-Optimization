import random
import matplotlib.pyplot as plt
import networkx as nx

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

# --- 2. PARAMETER ACO ---
num_ants = 20        # Jumlah semut
num_iterations = 40  # Jumlah iterasi
alpha = 1.0          # Bobot feromon
beta = 2.0           # Bobot jarak
evaporation = 0.5    # Tingkat penguapan
Q = 100              # Konstanta deposit feromon

# Inisialisasi feromon (menggunakan matriks)
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

# --- 3. FUNGSI BANTU ---
def get_distance(city1, city2):
    """Mengembalikan jarak antara dua kota menggunakan matriks"""
    idx1 = node_to_idx[city1]
    idx2 = node_to_idx[city2]
    dist = dist_matrix[idx1][idx2]
    return float('inf') if dist == INF else dist

def get_pheromone(city1, city2):
    """Mengembalikan nilai feromon antara dua kota"""
    idx1 = node_to_idx[city1]
    idx2 = node_to_idx[city2]
    return pheromone[idx1][idx2]

def set_pheromone(city1, city2, value):
    """Mengatur nilai feromon antara dua kota"""
    idx1 = node_to_idx[city1]
    idx2 = node_to_idx[city2]
    pheromone[idx1][idx2] = value

def update_pheromone(city1, city2, delta):
    """Menambahkan delta ke feromon antara dua kota"""
    idx1 = node_to_idx[city1]
    idx2 = node_to_idx[city2]
    pheromone[idx1][idx2] += delta
    # Update juga reverse untuk graf tidak berarah
    pheromone[idx2][idx1] += delta

def calculate_tour_length(tour):
    """Menghitung total jarak tour"""
    total = 0
    for i in range(len(tour) - 1):
        dist = get_distance(tour[i], tour[i+1])
        if dist == float('inf'):
            return float('inf')
        total += dist
    return total

def get_neighbors(city):
    """Mendapatkan tetangga yang terhubung dari suatu kota"""
    idx = node_to_idx[city]
    neighbors = []
    for j in range(num_cities):
        if dist_matrix[idx][j] != INF and dist_matrix[idx][j] != 0:
            neighbors.append(idx_to_node[j])
    return neighbors

# --- 4. FUNGSI VISUALISASI ---
def draw_graph_with_path(path=None, title="Graf TSP"):
    """Menggambar graf dengan path optimal (jika ada)"""
    G = nx.Graph()
    
    # Tambahkan edge dengan bobot dari matriks
    for i in range(num_cities):
        for j in range(i+1, num_cities):  # Hanya setengah matriks karena simetris
            if dist_matrix[i][j] != INF and dist_matrix[i][j] != 0:
                city1, city2 = idx_to_node[i], idx_to_node[j]
                G.add_edge(city1, city2, weight=dist_matrix[i][j])
    
    plt.figure(figsize=(12, 8))
    
    # Gambar node
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue', edgecolors='black')
    nx.draw_networkx_nodes(G, pos, nodelist=['H'], node_color='green', node_size=700, label='Start (H)')
    nx.draw_networkx_nodes(G, pos, nodelist=['D'], node_color='red', node_size=700, label='End (D)')
    nx.draw_networkx_nodes(G, pos, nodelist=['#'], node_color='orange', node_size=700, label='Must Pass (#)')
    
    # Gambar edge dengan bobot
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
    
    # Tampilkan bobot
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    
    # Jika ada path, highlight dengan warna merah dan arah panah
    if path:
        path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
        # Buat DiGraph khusus untuk arah panah
        G_path = nx.DiGraph()
        G_path.add_edges_from(path_edges)
        nx.draw_networkx_edges(G_path, pos, edgelist=path_edges, width=3, edge_color='red', 
                               arrows=True, arrowsize=25, arrowstyle='->', label='Optimal Path')
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.legend(loc='upper left')
    plt.tight_layout()
    plt.show()

# --- 5. CETAK MATRIKS ---
print("="*60)
print("MATRIKS KETETANGGAAN")
print("="*60)
print("   A  B  C  #  D  E  F  G  H")
for i, row in enumerate(dist_matrix):
    node = idx_to_node[i]
    print(f"{node}: ", end="")
    for val in row:
        if val == INF:
            print(" - ", end="")
        else:
            print(f"{val:2} ", end="")
    print()

# --- 6. ALGORITMA ACO ---
print("\n" + "="*60)
print("ANT COLONY OPTIMIZATION - TSP (Matrix Version)")
print("="*60)
print(f"Start: H (index {node_to_idx['H']}) | Must-Pass: # (index {node_to_idx['#']}) | End: D (index {node_to_idx['D']})")
print("="*60)

# Gambar graf awal
print("\n✅ Menampilkan graf awal...")
draw_graph_with_path(title="Graf Awal TSP (Matrix Version)")

best_tour = None
best_length = float('inf')

for iteration in range(num_iterations):
    all_tours = []
    all_lengths = []
    
    for ant in range(num_ants):
        # Mulai dari H (sesuai tugas)
        current_city = 'H'
        visited = ['H']
        unvisited = [c for c in cities if c != 'H']
        
        # Bangun tour
        while len(visited) < len(cities):
            # Dapatkan tetangga yang belum dikunjungi
            neighbors = []
            for city in unvisited:
                if get_distance(current_city, city) != float('inf'):
                    neighbors.append(city)
            
            # Filter: Jika # belum dikunjungi, jangan pilih D
            if '#' not in visited:
                neighbors = [n for n in neighbors if n != 'D']
            
            # Jika tidak ada pilihan, pilih dari semua tetangga yang terhubung
            if not neighbors:
                all_possible_neighbors = get_neighbors(current_city)
                neighbors = [n for n in all_possible_neighbors if n not in visited]
                if not neighbors:
                    # Jika benar-benar buntu, pilih random dari unvisited yang terhubung
                    neighbors = [n for n in unvisited if get_distance(current_city, n) != float('inf')]
            
            # Hitung probabilitas
            probabilities = []
            total_prob = 0
            
            for next_city in neighbors:
                # Feromon
                tau = get_pheromone(current_city, next_city)
                # Jarak
                dist = get_distance(current_city, next_city)
                eta = 1.0 / dist if dist != float('inf') else 0
                
                prob = (tau ** alpha) * (eta ** beta)
                probabilities.append(prob)
                total_prob += prob
            
            # Pilih kota berikutnya (Roulette Wheel)
            if total_prob == 0:
                next_city = random.choice(neighbors) if neighbors else random.choice([c for c in cities if c not in visited])
            else:
                r = random.uniform(0, total_prob)
                cumsum = 0
                next_city = neighbors[0]  # Default
                for i, prob in enumerate(probabilities):
                    cumsum += prob
                    if r <= cumsum:
                        next_city = neighbors[i]
                        break
            
            # Pindah ke kota berikutnya
            current_city = next_city
            visited.append(next_city)
            unvisited.remove(next_city)
            
            # Cek kondisi: Jika sudah di D dan # sudah dikunjungi, selesai
            if current_city == 'D' and '#' in visited:
                break
        
        # Validasi tour
        if visited[0] == 'H' and visited[-1] == 'D' and '#' in visited:
            length = calculate_tour_length(visited)
            if length != float('inf'):
                all_tours.append(visited)
                all_lengths.append(length)
                
                if length < best_length:
                    best_length = length
                    best_tour = visited
                    print(f"  ✅ Ditemukan rute lebih baik: {' -> '.join(visited)} (Jarak: {length})")
    
    # Update feromon (evaporasi)
    for i in range(num_cities):
        for j in range(num_cities):
            if dist_matrix[i][j] != INF and dist_matrix[i][j] != 0:
                pheromone[i][j] *= (1 - evaporation)
    
    # Deposit feromon
    for tour, length in zip(all_tours, all_lengths):
        deposit = Q / length
        for i in range(len(tour) - 1):
            update_pheromone(tour[i], tour[i+1], deposit)
    
    # Progress report
    if (iteration + 1) % 10 == 0:
        print(f"📊 Iterasi {iteration+1}/{num_iterations}: Best length = {best_length}")

# --- 7. HASIL AKHIR ---
print("\n" + "="*60)
print("🏆 HASIL OPTIMAL")
print("="*60)
if best_tour:
    print(f"Rute Terbaik: {' -> '.join(best_tour)}")
    print(f"Total Jarak: {best_length}")
    print(f"Jumlah kota dikunjungi: {len(best_tour)}")
    
    # Verifikasi rute menggunakan matriks
    print("\n📋 Verifikasi Rute (menggunakan matriks):")
    total_check = 0
    for i in range(len(best_tour)-1):
        dist = get_distance(best_tour[i], best_tour[i+1])
        print(f"  {best_tour[i]} -> {best_tour[i+1]}: {dist}")
        total_check += dist
    print(f"  Total terverifikasi: {total_check}")
    
    # Gambar graf dengan rute optimal
    print("\n✅ Menampilkan rute optimal dengan arah panah...")
    draw_graph_with_path(best_tour, title="Rute Optimal TSP (Matrix Version - Dengan Arah Panah)")
else:
    print("❌ Tidak ditemukan rute valid. Coba jalankan ulang program.")
    
# --- 8. TAMPILKAN MATRIKS FEROMON AKHIR ---
print("\n" + "="*60)
print("MATRIKS FEROMON AKHIR")
print("="*60)
print("        A       B       C       #       D       E       F       G       H")
for i, row in enumerate(pheromone):
    node = idx_to_node[i]
    print(f"{node}: ", end="")
    for val in row:
        print(f"{val:7.4f} ", end="")
    print()