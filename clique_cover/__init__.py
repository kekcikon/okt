import networkx as nx
import neal
import dimod

def create_qubo_clique_cover(G, k):
    """Создание QUBO для покрытия кликами с использованием формулировки из пункта 6.2"""
    Q = {}

    # # Коэффициенты штрафов
    A = 2  # За нарушение ограничения на принадлежность вершины клике
    B = A*8/min(2*max(G.degree, key=lambda x:x[1])[1], G.number_of_nodes())  # За нарушение кликового ограничения
    print(B)
    # 1. Каждая вершина должна принадлежать хотя бы одной клике
    for v in G.nodes():
        # Линейные члены для переменных x_{v,c}
        for c in range(k):
            Q[(('x', v, c), ('x', v, c))] = -A
        # Квадратичные члены для обеспечения, что вершина принадлежит только одной клике
        for c1 in range(k):
            for c2 in range(c1 + 1, k):
                Q[(('x', v, c1), ('x', v, c2))] = 2*A

    # 2. Внутри каждой клики все вершины должны быть связаны рёбрами
    for c in range(k):
        for u in G.nodes():
            for v in G.nodes():
                if u < v:
                    if not G.has_edge(u, v):
                        Q[(('x', u, c), ('x', v, c))] = B


    return Q

def solve_clique_cover_with_neal(G, max_k=3):
    """Решаем задачу покрытия кликами с использованием dwave-neal"""
    sampler = neal.SimulatedAnnealingSampler()

    # Перебираем количество клик от 1 до max_k
    for k in range(1, max_k + 1):
        print(f"Пробуем решение с {k} кликами...")
        Q = create_qubo_clique_cover(G, k)

        # Преобразуем QUBO в BQM и решаем с помощью симулированного отжига
        bqm = dimod.BinaryQuadraticModel.from_qubo(Q)
        response = sampler.sample(bqm, num_reads=100)

        # Проверяем, есть ли валидное решение
        for sample in response:
            solution = sample
            if is_valid_clique_cover(G, solution, k):
                print(f"Найдено валидное решение с {k} кликами!")
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

# Пример использования
if __name__ == "__main__":
    # Создаем пример графа
    # G = nx.barbell_graph(5,2)
    # G = nx.complete_graph(350)
    # G = nx.empty_graph(105)
    G = nx.cycle_graph(20)
    max_k = 25  # Максимальное количество клик для поиска

    # Поиск минимального покрытия кликами
    min_k, solution = solve_clique_cover_with_neal(G, max_k)

    if solution:
        print(f"Минимальное количество клик: {min_k}")
        for c in range(min_k):
            clique = [v for v in G.nodes() if solution.get(('x', v, c), 0) == 1]
            if clique:
                print(f"Clique {c+1}: {clique}")
    else:
        print("Не удалось найти покрытие кликами.")
