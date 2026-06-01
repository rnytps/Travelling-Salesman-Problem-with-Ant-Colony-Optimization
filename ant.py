import random
import math
import matplotlib.pyplot as plt
import networkx as nx

# --- 1. DEFINISI GRAF SESUAI GAMBAR 1 ---
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

# Jarak antar node (bobot edge)
distances = {
    ('A', '#'): 3, ('A', 'C'): 6,
    ('B', 'C'): 9, ('B', 'D'): 8,
    ('C', 'A'): 6, ('C', '#'): 2, ('C', 'F'): 4, ('C', 'B'): 9,
    ('D', 'H'): 9, ('D', 'E'): 7, ('D', 'B'): 8,
    ('E', 'D'): 7, ('E', 'F'): 2, ('E', 'G'): 1, ('E', 'H'): 1,
    ('F', 'C'): 4, ('F', 'E'): 2,
    ('G', '#'): 5, ('G', 'E'): 1, ('G', 'H'): 3,
    ('H', 'D'): 9, ('H', 'E'): 1, ('H', 'G'): 3,
    ('#', 'A'): 3, ('#', 'G'): 5, ('#', 'C'): 2
}

# Daftar semua kota
cities = list(pos.keys())
num_cities = len(cities)

# --- 2. PARAMETER ACO ---
num_ants = 20        # Jumlah semut
num_iterations = 40  # Jumlah iterasi
alpha = 1.0          # Bobot feromon
beta = 2.0           # Bobot jarak
evaporation = 0.5    # Tingkat penguapan
Q = 100              # Konstanta deposit feromon

# Inisialisasi feromon
pheromone = {}
for i in cities:
    for j in cities:
        if (i, j) in distances or (j, i) in distances:
            pheromone[(i, j)] = 1.0

# --- 3. FUNGSI BANTU ---
def get_distance(city1, city2):
    """Mengembalikan jarak antara dua kota"""
    if (city1, city2) in distances:
        return distances[(city1, city2)]
    elif (city2, city1) in distances:
        return distances[(city2, city1)]
    return float('inf')

def calculate_tour_length(tour):
    """Menghitung total jarak tour"""
    total = 0
    for i in range(len(tour) - 1):
        dist = get_distance(tour[i], tour[i+1])
        if dist == float('inf'):
            return float('inf')
        total += dist
    return total

# --- 4. FUNGSI VISUALISASI ---
def draw_graph_with_path(path=None, title="Graf TSP"):
    """Menggambar graf dengan path optimal (jika ada)"""
    G = nx.Graph()
    
    # Tambahkan edge dengan bobot
    for (u, v), weight in distances.items():
        G.add_edge(u, v, weight=weight)
    
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

# --- 5. ALGORITMA ACO (Mirip Video) ---
print("="*60)
print("ANT COLONY OPTIMIZATION - TSP")
print("="*60)
print(f"Start: H | Must-Pass: # | End: D")
print("="*60)

# Gambar graf awal
print("\n✅ Menampilkan graf awal...")
draw_graph_with_path(title="Graf Awal TSP")

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
            
            # Jika tidak ada pilihan, pilih dari semua tetangga
            if not neighbors:
                all_neighbors = [city for city in unvisited if get_distance(current_city, city) != float('inf')]
                if all_neighbors:
                    neighbors = all_neighbors
                else:
                    # Jika benar-benar tidak ada, pilih random dari unvisited
                    neighbors = unvisited
            
            # Hitung probabilitas (seperti video)
            probabilities = []
            total_prob = 0
            
            for next_city in neighbors:
                # Feromon
                tau = pheromone.get((current_city, next_city), 1.0)
                # Jarak
                dist = get_distance(current_city, next_city)
                eta = 1.0 / dist if dist != float('inf') else 0
                
                prob = (tau ** alpha) * (eta ** beta)
                probabilities.append(prob)
                total_prob += prob
            
            # Pilih kota berikutnya (Roulette Wheel)
            if total_prob == 0:
                next_city = random.choice(neighbors)
            else:
                r = random.uniform(0, total_prob)
                cumsum = 0
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
    
    # Update feromon (evaporasi + deposit)
    for key in pheromone:
        pheromone[key] *= (1 - evaporation)
    
    for tour, length in zip(all_tours, all_lengths):
        deposit = Q / length
        for i in range(len(tour) - 1):
            u, v = tour[i], tour[i+1]
            pheromone[(u, v)] += deposit
            # Untuk graf tidak berarah, update juga reverse
            if (v, u) in pheromone:
                pheromone[(v, u)] += deposit
    
    # Progress report
    if (iteration + 1) % 10 == 0:
        print(f"Iterasi {iteration+1}/{num_iterations}: Best length = {best_length}")

# --- 6. HASIL AKHIR ---
print("\n" + "="*60)
print("🏆 HASIL OPTIMAL")
print("="*60)
if best_tour:
    print(f"Rute Terbaik: {' -> '.join(best_tour)}")
    print(f"Total Jarak: {best_length}")
    print(f"Jumlah kota dikunjungi: {len(best_tour)}")
    
    # Gambar graf dengan rute optimal
    print("\n✅ Menampilkan rute optimal dengan arah panah...")
    draw_graph_with_path(best_tour, title="Rute Optimal TSP (Dengan Arah Panah)")
else:
    print("❌ Tidak ditemukan rute valid. Coba jalankan ulang program.")