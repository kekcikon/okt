#!/usr/bin/env python3
import pytest
import numpy as np
import networkx as nx
from clique_cover.main import solve_clique_cover

@pytest.mark.parametrize("verticies, clique",[
                                        (5, 1),
                                        (15, 1),
                                        (100, 1)])
def test_complete(verticies, clique, max_c=100):
        G = nx.complete_graph(verticies)
        min_k, solution = solve_clique_cover(G, max_c)            
        assert min_k== clique

@pytest.mark.parametrize("verticies, clique",[
                                        (5, 5),
                                        (15, 15),
                                        (1, 1)])
def test_empty(verticies, clique, max_c=100):
        G = nx.empty_graph(verticies)
        min_k, solution = solve_clique_cover(G, max_c)            
        assert min_k== clique

@pytest.mark.parametrize("verticies",[
                                        (5),
                                        (15),
                                        (10)])
def test_cycle(verticies, max_c=100):
        clique = np.ceil(verticies/2)
        G = nx.cycle_graph(verticies)
        min_k, solution = solve_clique_cover(G, max_c)            
        assert min_k== clique

@pytest.mark.parametrize("verticies, clique",[
                                        ((10,2), 3),
                                        ((15,2), 3),
                                        ((10,3), 4)])
def test_empty(verticies, clique, max_c=100):
        G = nx.barbell_graph(*verticies)
        min_k, solution = solve_clique_cover(G, max_c)            
        assert min_k== clique