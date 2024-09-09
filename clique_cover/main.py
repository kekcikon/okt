#!/usr/bin/env python3
import networkx as nx
import neal
import dimod

def create_qubo_clique_cover(G, k):
    """Создание QUBO для покрытия кликами """
    Q = {}

    # # Коэффициенты штрафов
    A = 2 
    B = A*8/min(2*max(G.degree, key=lambda x:x[1])[1], G.number_of_nodes())  
    for v in G.nodes():
        for c in range(k):
            Q[(('x', v, c), ('x', v, c))] = -A
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                Q[(('x', v, c1), ('x', v, c2))] = 2*A

    for c in range(k):
        for u in G.nodes():
            for v in G.nodes():
                if u < v and not G.has_edge(u, v):
                    Q[(('x', u, c), ('x', v, c))] = B


    return Q

def solve_clique_cover(G, max_k=3):
    """Решаем задачу покрытия кликами """
    sampler = neal.SimulatedAnnealingSampler()

    for k in range(1, max_k + 1):
        print(f"Пробуем решение с {k} кликами...")
        Q = create_qubo_clique_cover(G, k)

        bqm = dimod.BinaryQuadraticModel.from_qubo(Q)
        response = sampler.sample(bqm, num_reads=100)

        for sample in response:
            solution = sample
            if is_valid_clique_cover(G, solution, k):
                # print(f"Найдено валидное решение с {k} кликами!")
                return k, solution

    return None, None

def is_valid_clique_cover(G, solution, k):
    """Проверка, является ли решение валидным покрытием кликами"""
    covered_vertices = set()
    for c in range(k):
        clique = [v for v in G.nodes() if solution.get(('x', v, c), 0) == 1]
        if clique:
            # Проверяем, что все пары вершин внутри клики связаны
            for i in range(len(clique)):
                for j in range(i + 1, len(clique)):
                    if not G.has_edge(clique[i], clique[j]):
                        return False
            covered_vertices.update(clique)
    # Проверяем, что все вершины покрыты
    if covered_vertices != set(G.nodes()):
        return False
    return True

