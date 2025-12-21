import random
import hashlib
import json
from typing import Dict, List, Tuple, Set, Optional
from dataclasses import dataclass
from enum import Enum

class Color(Enum):
    RED = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    PURPLE = 5
    ORANGE = 6

@dataclass
class Edge:
    u: int
    v: int
    
    def __hash__(self):
        return hash((min(self.u, self.v), max(self.u, self.v)))
    
    def __eq__(self, other):
        if not isinstance(other, Edge):
            return False
        return {self.u, self.v} == {other.u, other.v}

class Graph:
    def __init__(self, num_vertices: int = 0):
        self.num_vertices = num_vertices
        self.edges: Set[Edge] = set()
        self.adjacency_list: Dict[int, Set[int]] = {i: set() for i in range(num_vertices)}
    
    def add_edge(self, u: int, v: int):
        if u == v:
            return
        edge = Edge(u, v)
        self.edges.add(edge)
        self.adjacency_list[u].add(v)
        self.adjacency_list[v].add(u)
    
    def get_neighbors(self, vertex: int) -> Set[int]:
        return self.adjacency_list.get(vertex, set())
    
    def is_valid_coloring(self, coloring: Dict[int, Color]) -> bool:
        if len(coloring) != self.num_vertices:
            return False
        for edge in self.edges:
            if coloring[edge.u] == coloring[edge.v]:
                return False
        return True
    
    def get_chromatic_number_upper_bound(self) -> int:
        if not self.adjacency_list:
            return 1
        return max(len(neighbors) for neighbors in self.adjacency_list.values()) + 1
    
    @classmethod
    def from_file(cls, filename: str) -> Tuple['Graph', Optional[Dict[int, Color]]]:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        n, m = map(int, lines[0].split())
        graph = cls(n)
        
        for i in range(1, m + 1):
            u, v = map(int, lines[i].split())
            graph.add_edge(u - 1, v - 1)
        
        coloring = None
        if len(lines) > m + 1:
            color_values = list(map(int, lines[m + 1].split()))
            color_map = {1: Color.RED, 2: Color.BLUE, 3: Color.GREEN, 
                        4: Color.YELLOW, 5: Color.PURPLE, 6: Color.ORANGE}
            
            coloring = {vertex: color_map[color_num] 
                       for vertex, color_num in enumerate(color_values)}
            
            if not graph.is_valid_coloring(coloring):
                raise ValueError("Некорректная раскраска в файле")
        
        return graph, coloring

class GraphColoringSolver:
    def __init__(self, graph: Graph):
        self.graph = graph
    
    def generate_valid_coloring(self, max_colors: int = 6) -> Optional[Dict[int, Color]]:
        colors = list(Color)[:max_colors]
        coloring = {}
        
        vertices = sorted(range(self.graph.num_vertices), 
                         key=lambda v: len(self.graph.get_neighbors(v)), 
                         reverse=True)
        
        for vertex in vertices:
            used_colors = {coloring[neighbor] for neighbor in self.graph.get_neighbors(vertex) 
                          if neighbor in coloring}
            available_colors = [c for c in colors if c not in used_colors]
            
            if not available_colors:
                return None
            coloring[vertex] = available_colors[0]
        
        return coloring
    
    def find_minimal_coloring(self) -> Optional[Dict[int, Color]]:
        upper_bound = min(self.graph.get_chromatic_number_upper_bound(), 6)
        for num_colors in range(1, upper_bound + 1):
            coloring = self.generate_valid_coloring(num_colors)
            if coloring:
                return coloring
        return None

class ZKPCommitment:
    @staticmethod
    def commit(value: str, nonce: str) -> str:
        combined = f"{value}:{nonce}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    @staticmethod
    def verify_commitment(commitment: str, value: str, nonce: str) -> bool:
        return commitment == ZKPCommitment.commit(value, nonce)

class GraphColoringZKProver:
    def __init__(self, graph: Graph, coloring: Dict[int, Color]):
        self.graph = graph
        self.original_coloring = coloring
        self.current_round_data = None
        if not graph.is_valid_coloring(coloring):
            raise ValueError("Некорректная раскраска")
    
    def start_round(self) -> Dict[int, str]:
        colors_used = list(set(self.original_coloring.values()))
        permuted_colors = colors_used.copy()
        random.shuffle(permuted_colors)
        
        color_permutation = dict(zip(colors_used, permuted_colors))
        permuted_coloring = {vertex: color_permutation[color] 
                           for vertex, color in self.original_coloring.items()}
        
        nonces = {vertex: str(random.randint(10**10, 10**15)) 
                 for vertex in range(self.graph.num_vertices)}
        
        commitments = {}
        for vertex in range(self.graph.num_vertices):
            color_value = str(permuted_coloring[vertex].value)
            commitments[vertex] = ZKPCommitment.commit(color_value, nonces[vertex])
        
        self.current_round_data = {
            'permuted_coloring': permuted_coloring,
            'nonces': nonces
        }
        return commitments
    
    def respond_to_challenge(self, challenged_edge: Edge) -> Tuple[Color, Color, str, str]:
        u, v = challenged_edge.u, challenged_edge.v
        permuted_coloring = self.current_round_data['permuted_coloring']
        nonces = self.current_round_data['nonces']
        
        return (permuted_coloring[u], permuted_coloring[v], nonces[u], nonces[v])

class GraphColoringZKVerifier:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.current_commitments = None
    
    def receive_commitments(self, commitments: Dict[int, str]):
        self.current_commitments = commitments
    
    def generate_challenge(self) -> Edge:
        return random.choice(list(self.graph.edges))
    
    def verify_response(self, challenge_edge: Edge, 
                       color_u: Color, color_v: Color, 
                       nonce_u: str, nonce_v: str) -> bool:
        u, v = challenge_edge.u, challenge_edge.v
        
        if color_u == color_v:
            return False
        
        commitment_u = self.current_commitments[u]
        commitment_v = self.current_commitments[v]
        
        valid_u = ZKPCommitment.verify_commitment(commitment_u, str(color_u.value), nonce_u)
        valid_v = ZKPCommitment.verify_commitment(commitment_v, str(color_v.value), nonce_v)
        
        return valid_u and valid_v

class GraphColoringZKProtocol:
    def __init__(self, graph: Graph, coloring: Dict[int, Color]):
        self.graph = graph
        self.prover = GraphColoringZKProver(graph, coloring)
        self.verifier = GraphColoringZKVerifier(graph)
        self.protocol_log = []
    
    def run_single_round(self, round_num: int) -> bool:
        print(f"\n--- РАУНД {round_num} ---")
        
        commitments = self.prover.start_round()
        self.verifier.receive_commitments(commitments)
        
        challenge_edge = self.verifier.generate_challenge()
        print(f"Выбрано ребро: ({challenge_edge.u + 1}, {challenge_edge.v + 1})")
        
        color_u, color_v, nonce_u, nonce_v = self.prover.respond_to_challenge(challenge_edge)
        print(f"Цвета: {color_u.name}, {color_v.name}")
        
        is_valid = self.verifier.verify_response(challenge_edge, color_u, color_v, nonce_u, nonce_v)
        
        self.protocol_log.append({
            'round': round_num,
            'challenged_edge': (challenge_edge.u + 1, challenge_edge.v + 1),
            'valid': is_valid
        })
        
        print("Успех" if is_valid else "Провал")
        return is_valid
    
    def run_protocol(self, num_rounds: int = 10) -> bool:
        print(f"ПРОТОКОЛ ZK ДЛЯ РАСКРАСКИ ГРАФА")
        print(f"Граф: {self.graph.num_vertices} вершин, {len(self.graph.edges)} рёбер")
        print(f"Раундов: {num_rounds}")
        
        for round_num in range(1, num_rounds + 1):
            if not self.run_single_round(round_num):
                print(f"\nПРОТОКОЛ ПРОВАЛЕН НА РАУНДЕ {round_num}")
                return False
        
        print(f"\nПРОТОКОЛ УСПЕШНО ЗАВЕРШЕН!")
        return True
    
    def get_protocol_statistics(self) -> Dict:
        total_rounds = len(self.protocol_log)
        successful_rounds = sum(1 for r in self.protocol_log if r['valid'])
        
        return {
            'total_rounds': total_rounds,
            'successful_rounds': successful_rounds,
            'success_rate': successful_rounds / total_rounds if total_rounds > 0 else 0,
            'security_level': 1 / (2 ** successful_rounds) if successful_rounds > 0 else 1
        }

def main():
    
    filename = input("Введите имя файла с графом: ").strip()
    if not filename:
        return
    
    try:
        graph, file_coloring = Graph.from_file(filename)
        print(f"Граф загружен: {graph.num_vertices} вершин, {len(graph.edges)} рёбер")
        
        if file_coloring:
            coloring = file_coloring
            print("Раскраска загружена из файла")
        else:
            solver = GraphColoringSolver(graph)
            coloring = solver.find_minimal_coloring()
            if not coloring:
                print("Не удалось найти раскраску")
                return
        
        colors_used = set(coloring.values())
        print(f"Раскраска использует {len(colors_used)} цветов:")
        for vertex, color in sorted(coloring.items()):
            print(f"  Вершина {vertex + 1}: {color.name}")
        
        try:
            num_rounds = int(input("Количество раундов (по умолчанию 10): ") or "10")
        except ValueError:
            num_rounds = 10
        
        protocol = GraphColoringZKProtocol(graph, coloring)
        success = protocol.run_protocol(num_rounds)
        
        stats = protocol.get_protocol_statistics()
        print(f"\nСТАТИСТИКА:")
        print(f"  Раундов: {stats['total_rounds']}")
        print(f"  Успешных: {stats['successful_rounds']}")
        print(f"  Уровень безопасности: {stats['security_level']:.2e}")
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()