"""
Generators for some classic graphs.

The typical graph generator is called as follows:

>>> G=nx.complete_graph(100)

returning the complete graph on n nodes labeled 0, .., 99
as a simple graph. Except for empty_graph, all the generators
in this module return a Graph class (i.e. a simple, undirected graph).

"""
# Authors: Aric Hagberg (hagberg@lanl.gov) and Pieter Swart (swart@lanl.gov)

#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from __future__ import division

import itertools

import networkx as nx
from networkx.algorithms.bipartite.generators import complete_bipartite_graph
from networkx.utils import accumulate
from networkx.utils import flatten
from networkx.utils import nodes_or_number
from networkx.utils import pairwise

__all__ = ['balanced_tree',
           'barbell_graph',
           'complete_graph',
           'complete_multipartite_graph',
           'circular_ladder_graph',
           'circulant_graph',
           'cycle_graph',
           'dorogovtsev_goltsev_mendes_graph',
           'empty_graph',
           'full_rary_tree',
           'grid_graph',
           'grid_2d_graph',
           'hypercube_graph',
           'ladder_graph',
           'lollipop_graph',
           'null_graph',
           'path_graph',
           'star_graph',
           'trivial_graph',
           'turan_graph',
           'wheel_graph']


#-------------------------------------------------------------------
#   Some Classic Graphs
#-------------------------------------------------------------------

def _tree_edges(n, r):
    # helper function for trees
    # yields edges in rooted tree at 0 with n nodes and branching ratio r
    nodes = iter(range(n))
    parents = [next(nodes)]  # stack of max length r
    while parents:
        source = parents.pop(0)
        for i in range(r):
            try:
                target = next(nodes)
                parents.append(target)
                yield source, target
            except StopIteration:
                break


def full_rary_tree(r, n, create_using=None):
    """Creates a full r-ary tree of n vertices.

    Sometimes called a k-ary, n-ary, or m-ary tree.
    "... all non-leaf vertices have exactly r children and all levels
    are full except for some rightmost position of the bottom level
    (if a leaf at the bottom level is missing, then so are all of the
    leaves to its right." [1]_

    Parameters
    ----------
    r : int
        branching factor of the tree
    n : int
        Number of nodes in the tree
    create_using : Graph, optional (default None)
        If provided this graph is cleared of nodes and edges and filled
        with the new graph. Usually used to set the type of the graph.

    Returns
    -------
    G : networkx Graph
        An r-ary tree with n nodes

    References
    ----------
    .. [1] An introduction to data structures and algorithms,
           James Andrew Storer,  Birkhauser Boston 2001, (page 225).
    """
    G = nx.empty_graph(n, create_using)
    G.add_edges_from(_tree_edges(n, r))
    return G


def balanced_tree(r, h, create_using=None):
    """Return the perfectly balanced `r`-ary tree of height `h`.

    Parameters
    ----------
    r : int
        Branching factor of the tree; each node will have `r`
        children.

    h : int
        Height of the tree.

    create_using : Graph, optional (default None)
        If provided this graph is cleared of nodes and edges and filled
        with the new graph. Usually used to set the type of the graph.

    Returns
    -------
    G : NetworkX graph
        A balanced `r`-ary tree of height `h`.

    Notes
    -----
    This is the rooted tree where all leaves are at distance `h` from
    the root. The root has degree `r` and all other internal nodes
    have degree `r + 1`.

    Node labels are integers, starting from zero.

    A balanced tree is also known as a *complete r-ary tree*.

    """
    # The number of nodes in the balanced tree is `1 + r + ... + r^h`,
    # which is computed by using the closed-form formula for a geometric
    # sum with ratio `r`. In the special case that `r` is 1, the number
    # of nodes is simply `h + 1` (since the tree is actually a path
    # graph).
    if r == 1:
        n = h + 1
    else:
        # This must be an integer if both `r` and `h` are integers. If
        # they are not, we force integer division anyway.
        n = (1 - r ** (h + 1)) // (1 - r)
    return full_rary_tree(r, n, create_using=create_using)


def barbell_graph(m1, m2, create_using=None):
    """Return the Barbell Graph: two complete graphs connected by a path.

    For `m1 > 1` and `m2 >= 0`.

    Two identical complete graphs `K_{m1}` form the left and right bells,
    and are connected by a path `P_{m2}`.

    The `2*m1+m2`  nodes are numbered
        `0, ..., m1-1` for the left barbell,
        `m1, ..., m1+m2-1` for the path,
        and `m1+m2, ..., 2*m1+m2-1` for the right barbell.

    The 3 subgraphs are joined via the edges `(m1-1, m1)` and 
    `(m1+m2-1, m1+m2)`. If `m2=0`, this is merely two complete 
    graphs joined together.

    This graph is an extremal example in David Aldous
    and Jim Fill's e-text on Random Walks on Graphs.

    """
    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")
    if m1 < 2:
        raise nx.NetworkXError(
            "Invalid graph description, m1 should be >=2")
    if m2 < 0:
        raise nx.NetworkXError(
            "Invalid graph description, m2 should be >=0")

    # left barbell
    G = complete_graph(m1, create_using)
    G.name = "barbell_graph(%d,%d)" % (m1, m2)

    # connecting path
    G.add_nodes_from(range(m1, m1 + m2 - 1))
    if m2 > 1:
        G.add_edges_from(pairwise(range(m1, m1 + m2)))
    # right barbell
    G.add_edges_from((u, v) for u in range(m1 + m2, 2 * m1 + m2)
                     for v in range(u + 1, 2 * m1 + m2))
    # connect it up
    G.add_edge(m1 - 1, m1)
    if m2 > 0:
        G.add_edge(m1 + m2 - 1, m1 + m2)
    return G


@nodes_or_number(0)
def complete_graph(n, create_using=None):
    """ Return the complete graph `K_n` with n nodes.

    Parameters
    ==========
    n : int or iterable container of nodes
        If n is an integer, nodes are from range(n).
        If n is a container of nodes, those nodes appear in the graph.
    create_using : Graph, optional (default None)
        If provided this graph is cleared of nodes and edges and filled
        with the new graph. Usually used to set the type of the graph.

    Examples
    ========
    >>> G = nx.complete_graph(9)
    >>> len(G)
    9
    >>> G.size()
    36
    >>> G = nx.complete_graph(range(11,14))
    >>> list(G.nodes())
    [11, 12, 13]
    >>> G = nx.complete_graph(4, nx.DiGraph())
    >>> G.is_directed()
    True

    """
    n_name, nodes = n
    G = empty_graph(n_name, create_using)
    G.name = "complete_graph(%s)" % (n_name,)
    if len(nodes) > 1:
        if G.is_directed():
            edges = itertools.permutations(nodes, 2)
        else:
            edges = itertools.combinations(nodes, 2)
        G.add_edges_from(edges)
    return G


def circular_ladder_graph(n, create_using=None):
    """Return the circular ladder graph `CL_n` of length n.

    `CL_n` consists of two concentric n-cycles in which
    each of the n pairs of concentric nodes are joined by an edge.

    Node labels are the integers 0 to n-1

    """
    G = ladder_graph(n, create_using)
    G.name = "circular_ladder_graph(%d)" % n
    G.add_edge(0, n - 1)
    G.add_edge(n, 2 * n - 1)
    return G


def circulant_graph(n, offsets, create_using=None):
    """Generates the circulant graph Ci_n(x_1, x_2, ..., x_m) with n vertices.

    Returns
    -------
    The graph Ci_n(x_1, ..., x_m) consisting of n vertices 0, ..., n-1 such
    that the vertex with label i is connected to the vertices labelled (i + x)
    and (i - x), for all x in x_1 up to x_m, with the indices taken modulo n.

    Parameters
    ----------
    n : integer
        The number of vertices the generated graph is to contain.
    offsets : list of integers
        A list of vertex offsets, x_1 up to x_m, as described above.
    create_using : Graph, optional (default None)
        If provided this graph is cleared of nodes and edges and filled
        with the new graph. Usually used to set the type of the graph.

    Examples
    --------
    Many well-known graph families are subfamilies of the circulant graphs; for
    example, to generate the cycle graph on n points, we connect every vertex to
    every other at offset plus or minus one. For n = 10,

    >>> import networkx
    >>> G = networkx.generators.classic.circulant_graph(10, [1])
    >>> edges = [
    ...     (0, 9), (0, 1), (1, 2), (2, 3), (3, 4),
    ...     (4, 5), (5, 6), (6, 7), (7, 8), (8, 9)]
    ...
    >>> sorted(edges) == sorted(G.edges())
    True

    Similarly, we can generate the complete graph on 5 points with the set of
    offsets [1, 2]:

    >>> G = networkx.generators.classic.circulant_graph(5, [1, 2])
    >>> edges = [
    ...     (0, 1), (0, 2), (0, 3), (0, 4), (1, 2),
    ...     (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
    ...
    >>> sorted(edges) == sorted(G.edges())
    True

    """
    G = empty_graph(n, create_using)
    template = 'circulant_graph(%d, [%s])'
    G.name = template % (n, ', '.join(str(j) for j in offsets))
    for i in range(n):
        for j in offsets:
            G.add_edge(i, (i - j) % n)
            G.add_edge(i, (i + j) % n)
    return G


@nodes_or_number(0)
def cycle_graph(n, create_using=None):
    """Return the cycle graph `C_n` of cyclicly connected nodes.

    `C_n` is a path with its two end-nodes connected.

    Parameters
    ==========
    n : int or iterable container of nodes
        If n is an integer, nodes are from `range(n)`.
        If n is a container of nodes, those nodes appear in the graph.
    create_using : Graph, optional (default Graph())
        If provided this graph is cleared of nodes and edges and filled
        with the new graph. Usually used to set the type of the graph.

    Notes
    =====
    If create_using is directed, the direction is in increasing order.

    """
    n_orig, nodes = n
    G = empty_graph(nodes, create_using)
    G.name = "cycle_graph(%s)" % (n_orig,)
    G.add_edges_from(nx.utils.pairwise(nodes))
    G.add_edge(nodes[-1], nodes[0])
    return G


def dorogovtsev_goltsev_mendes_graph(n, create_using=None):
    """Return the hierarchically constructed Dorogovtsev-Goltsev-Mendes graph.

    n is the generation.
    See: arXiv:/cond-mat/0112143 by Dorogovtsev, Goltsev and Mendes.

    """
    if create_using is not None:
        if create_using.is_directed():
            raise nx.NetworkXError("Directed Graph not supported")
        if create_using.is_multigraph():
            raise nx.NetworkXError("Multigraph not supported")
    G = empty_graph(0, create_using)
    G.name = "Dorogovtsev-Goltsev-Mendes Graph"
    G.add_edge(0, 1)
    if n == 0:
        return G
    new_node = 2         # next node to be added
    for i in range(1, n + 1):  # iterate over number of generations.
        last_generation_edges = list(G.edges())
        number_of_edges_in_last_generation = len(last_generation_edges)
        for j in range(0, number_of_edges_in_last_generation):
            G.add_edge(new_node, last_generation_edges[j][0])
            G.add_edge(new_node, last_generation_edges[j][1])
            new_node += 1
    return G


@nodes_or_number(0)
def empty_graph(n=0, create_using=None):
    """Return the empty graph with n nodes and zero edges.

    Parameters
    ==========
    n : int or iterable container of nodes (default = 0)
        If n is an integer, nodes are from `range(n)`.
        If n is a container of nodes, those nodes appear in the graph.
    create_using : Graph, optional (default Graph())
        If provided this graph is cleared of nodes and edges and filled
        with the new graph. Usually used to set the type of the graph.

    For example:
    >>> G=nx.empty_graph(10)
    >>> G.number_of_nodes()
    10
    >>> G.number_of_edges()
    0
    >>> G=nx.empty_graph("ABC")
    >>> G.number_of_nodes()
    3
    >>> sorted(G)
    ['A', 'B', 'C']

    Notes
    =====
    The variable create_using should point to a "graph"-like object that
    will be cleared (nodes and edges will be removed) and refitted as
    an empty "graph" with nodes specified in n. This capability
    is useful for specifying the class-nature of the resulting empty
    "graph" (i.e. Graph, DiGraph, MyWeirdGraphClass, etc.).

    The variable create_using has two main uses:
    Firstly, the variable create_using can be used to create an
    empty digraph, multigraph, etc.  For example,

    >>> n=10
    >>> G=nx.empty_graph(n, create_using=nx.DiGraph())

    will create an empty digraph on n nodes.

    Secondly, one can pass an existing graph (digraph, multigraph,
    etc.) via create_using. For example, if G is an existing graph
    (resp. digraph, multigraph, etc.), then empty_graph(n, create_using=G)
    will empty G (i.e. delete all nodes and edges using G.clear())
    and then add n nodes and zero edges, and return the modified graph.

    See also create_empty_copy(G).

    """
    if create_using is None:
        # default empty graph is a simple graph
        G = nx.Graph()
    else:
        G = create_using
        G.clear()

    n_name, nodes = n
    G.name = "empty_graph(%s)" % (n_name,)
    G.add_nodes_from(nodes)
    return G


@nodes_or_number([0, 1])
def grid_2d_graph(m, n, periodic=False, create_using=None):
    """ Return the 2d grid graph of mxn nodes
    
    The grid graph has each node connected to its four nearest neighbors.

    Parameters
    ==========
    m, n : int or iterable container of nodes (default = 0)
        If an integer, nodes are from `range(n)`.
        If a container, those become the coordinate of the node.
    periodic : bool (default = False)
        If True will connect boundary nodes in periodic fashion.
    create_using : Graph, optional (default Graph())
        If provided this graph is cleared of nodes and edges and filled
        with the new graph. Usually used to set the type of the graph.
    """
    G = empty_graph(0, create_using)
    row_name, rows = m
    col_name, columns = n
    G.name = "grid_2d_graph(%s, %s)" % (row_name, col_name)
    G.add_nodes_from((i, j) for i in rows for j in columns)
    G.add_edges_from(((i, j), (pi, j))
                     for pi, i in pairwise(rows) for j in columns)
    G.add_edges_from(((i, j), (i, pj))
                     for i in rows for pj, j in pairwise(columns))
    if G.is_directed():
        G.add_edges_from(((pi, j), (i, j))
                         for pi, i in pairwise(rows) for j in columns)
        G.add_edges_from(((i, pj), (i, j))
                         for i in rows for pj, j in pairwise(columns))
    if periodic:
        if len(columns) > 2:
            f = columns[0]
            l = columns[-1]
            G.add_edges_from(((i, f), (i, l)) for i in rows)
            if G.is_directed():
                G.add_edges_from(((i, l), (i, f)) for i in rows)
        if len(rows) > 2:
            f = rows[0]
            l = rows[-1]
            G.add_edges_from(((f, j), (l, j)) for j in columns)
            if G.is_directed():
                G.add_edges_from(((l, j), (f, j)) for j in columns)
        G.name = "periodic_grid_2d_graph(%s,%s)" % (m, n)
    return G


def grid_graph(dim, periodic=False):
    """ Return the n-dimensional grid graph.

    'dim' is a list with the size in each dimension or an
    iterable of nodes for each dimension. The dimension of
    the grid_graph is the length of the list 'dim'.

    E.g. G=grid_graph(dim=[2, 3]) produces a 2x3 grid graph.

    E.g. G=grid_graph(dim=[range(7, 9), range(3, 6)]) produces a 2x3 grid graph.

    If periodic=True then join grid edges with periodic boundary conditions.

    """
    dlabel = "%s" % dim
    if dim == []:
        G = empty_graph(0)
        G.name = "grid_graph(%s)" % dim
        return G
    if periodic:
        func = cycle_graph
    else:
        func = path_graph

    dim = list(dim)
    current_dim = dim.pop()
    G = func(current_dim)
    while len(dim) > 0:
        current_dim = dim.pop()
        # order matters: copy before it is cleared during the creation of Gnew
        Gold = G.copy()
        Gnew = func(current_dim)
        # explicit: create_using=None
        # This is so that we get a new graph of Gnew's class.
        G = nx.cartesian_product(Gnew, Gold)
    # graph G is done but has labels of the form (1, (2, (3, 1)))
    # so relabel
    H = nx.relabel_nodes(G, flatten)
    H.name = "grid_graph(%s)" % dlabel
    return H


def hypercube_graph(n):
    """Return the n-dimensional hypercube.

    Node labels are the integers 0 to 2**n - 1.

    """
    dim = n * [2]
    G = grid_graph(dim)
    G.name = "hypercube_graph_(%d)" % n
    return G


def ladder_graph(n, create_using=None):
    """Return the Ladder graph of length n.

    This is two rows of n nodes, with
    each pair connected by a single edge.

    Node labels are the integers 0 to 2*n - 1.

    """
    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")
    G = empty_graph(2 * n, create_using)
    G.name = "ladder_graph_(%d)" % n
    G.add_edges_from(pairwise(range(n)))
    G.add_edges_from(pairwise(range(n, 2 * n)))
    G.add_edges_from((v, v + n) for v in range(n))
    return G


@nodes_or_number([0, 1])
def lollipop_graph(m, n, create_using=None):
    """Return the Lollipop Graph; `K_m` connected to `P_n`.

    This is the Barbell Graph without the right barbell.

    Parameters
    ==========
    m, n : int or iterable container of nodes (default = 0)
        If an integer, nodes are from `range(m)` and `range(m,m+n)`.
        If a container, the entries are the coordinate of the node.

        The nodes for m appear in the complete graph `K_m` and the nodes
        for n appear in the path `P_n`
    create_using : Graph, optional (default Graph())
        If provided this graph is cleared of nodes and edges and filled
        with the new graph. Usually used to set the type of the graph.

    Notes
    =====
    The 2 subgraphs are joined via an edge (m-1, m).  
    If n=0, this is merely a complete graph.

    (This graph is an extremal example in David Aldous and Jim
    Fill's etext on Random Walks on Graphs.)

    """
    m, m_nodes = m
    n, n_nodes = n
    M = len(m_nodes)
    N = len(n_nodes)
    if isinstance(m, int):
        n_nodes = [len(m_nodes) + i for i in n_nodes]
    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")
    if M < 2:
        raise nx.NetworkXError(
            "Invalid graph description, m should be >=2")
    if N < 0:
        raise nx.NetworkXError(
            "Invalid graph description, n should be >=0")

    # the ball
    G = complete_graph(m_nodes, create_using)
    # the stick
    G.add_nodes_from(n_nodes)
    if N > 1:
        G.add_edges_from(pairwise(n_nodes))
    # connect ball to stick
    if M > 0 and N > 0:
        G.add_edge(m_nodes[-1], n_nodes[0])
    G.name = "lollipop_graph(%s, %s)" % (m, n)
    return G


def null_graph(create_using=None):
    """Return the Null graph with no nodes or edges.

    See empty_graph for the use of create_using.

    """
    G = empty_graph(0, create_using)
    G.name = "null_graph()"
    return G


@nodes_or_number(0)
def path_graph(n, create_using=None):
    """Return the Path graph `P_n` of linearly connected nodes.

    Parameters
    ==========
    n : int or iterable
        If an integer, node labels are 0 to n with center 0.
        If an iterable of nodes, the center is the first.
    create_using : Graph, optional (default Graph())
        If provided this graph is cleared of nodes and edges and filled
        with the new graph. Usually used to set the type of the graph.

    """
    n_name, nodes = n
    G = empty_graph(nodes, create_using)
    G.name = "path_graph(%s)" % (n_name,)
    G.add_edges_from(nx.utils.pairwise(nodes))
    return G


@nodes_or_number(0)
def star_graph(n, create_using=None):
    """ Return the star graph
    
    The star graph consists of one center node connected to n outer nodes.

    Parameters
    ==========
    n : int or iterable
        If an integer, node labels are 0 to n with center 0.
        If an iterable of nodes, the center is the first.
    create_using : Graph, optional (default Graph())
        If provided this graph is cleared of nodes and edges and filled
        with the new graph. Usually used to set the type of the graph.

    Notes
    =====
    The graph has n+1 nodes for integer n.
    So star_graph(3) is the same as star_graph(range(4)).
    """
    n_name, nodes = n
    if isinstance(n_name, int):
        nodes = nodes + [n_name]  # there should be n+1 nodes
    first = nodes[0]
    G = empty_graph(nodes, create_using)
    if G.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")
    G.add_edges_from((first, v) for v in nodes[1:])
    G.name = "star_graph(%s)" % (n_name,)
    return G


def trivial_graph(create_using=None):
    """ Return the Trivial graph with one node (with label 0) and no edges.

    """
    G = empty_graph(1, create_using)
    G.name = "trivial_graph()"
    return G


def turan_graph(n,r):
    """ Return the Turan Graph
    
    The Turan Graph is a complete multipartite graph on `n` vertices
    with `r` partitions with the property that it has the maximum number
    of edges for any graph with the same number of vertices and partitions.

    Given n and r, we get a complete multipartite graph with `r-(n mod r)`
    partitions of size `n/r`, rounded down, and `n mod r` partitions of size
    `n/r+1`, rounded down.

    Parameters
    ==========
    n : int
        The number of vertices.
    r : int
        The number of partitions.
        Must be less than or equal to n.

    Notes
    =====
    Must satisfy `1 <= r <= n`.
    The graph has `(r-1)(n^2)/(2r)` edges, rounded down.
    """

    if not isinstance(n,int) or not isinstance(r,int):
        raise nx.NetworkXError("n and r must be type int") 

    if not 1 <= r <= n:
        raise nx.NetworkXError("Must satisfy 1 <= r <= n")

    partitions = [n//r]*(r-(n%r))+[n//r+1]*(n%r)
    G = complete_multipartite_graph(*partitions)
    G.name = "turan_graph({},{})".format(n,r)
    return G


@nodes_or_number(0)
def wheel_graph(n, create_using=None):
    """ Return the wheel graph
    
    The wheel graph consists of a hub node connected to a cycle of (n-1) nodes.

    Parameters
    ==========
    n : int or iterable
        If an integer, node labels are 0 to n with center 0.
        If an iterable of nodes, the center is the first.
    create_using : Graph, optional (default Graph())
        If provided this graph is cleared of nodes and edges and filled
        with the new graph. Usually used to set the type of the graph.
    Node labels are the integers 0 to n - 1.

    """
    n_name, nodes = n
    if n_name == 0:
        G = nx.empty_graph(0, create_using=create_using)
        G.name = "wheel_graph(0)"
        return G
    G = star_graph(nodes, create_using)
    G.name = "wheel_graph(%s)" % (n_name,)
    if len(G) > 2:
        G.add_edges_from(pairwise(nodes[1:]))
        G.add_edge(nodes[-1], nodes[1])
    return G


def complete_multipartite_graph(*block_sizes):
    """Returns the complete multipartite graph with the specified block sizes.

    Parameters
    ----------
    block_sizes : tuple of integers or tuple of node iterables
       The arguments can either all be integer number of nodes or they
       can all be iterables of nodes. If integers, they represent the
       number of vertices in each block of the multipartite graph.
       If iterables, each is used to create the nodes for that block.
       The length of block_sizes is the number of blocks.

    Returns
    -------
    G : NetworkX Graph
       Returns the complete multipartite graph with the specified blocks.

       For each node, the node attribute 'block' is an integer
       indicating which block contains the node.

    Examples
    --------
    Creating a complete tripartite graph, with blocks of one, two, and three
    vertices, respectively.

        >>> import networkx as nx
        >>> G = nx.complete_multipartite_graph(1, 2, 3)
        >>> [G.node[u]['block'] for u in G]
        [0, 1, 1, 2, 2, 2]
        >>> list(G.edges(0))
        [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]
        >>> list(G.edges(2))
        [(2, 0), (2, 3), (2, 4), (2, 5)]
        >>> list(G.edges(4))
        [(4, 0), (4, 1), (4, 2)]

        >>> G = nx.complete_multipartite_graph('a', 'bc', 'def')
        >>> [G.node[u]['block'] for u in sorted(G)]
        [0, 1, 1, 2, 2, 2]

    Notes
    -----
    This function generalizes several other graph generator functions.

    - If no block sizes are given, this returns the null graph.
    - If a single block size `n` is given, this returns the empty graph on
      `n` nodes.
    - If two block sizes `m` and `n` are given, this returns the complete
      bipartite graph on `m + n` nodes.
    - If block sizes `1` and `n` are given, this returns the star graph on
      `n + 1` nodes.

    See also
    --------
    complete_bipartite_graph
    """
    # The complete multipartite graph is an undirected simple graph.
    G = nx.Graph()
    G.name = 'complete_multiparite_graph{}'.format(block_sizes)

    if len(block_sizes) == 0:
        return G

    # set up blocks of nodes
    try:
        extents = pairwise(accumulate((0,) + block_sizes))
        blocks = [range(start, end) for start, end in extents]
    except TypeError:
        blocks = block_sizes

    # add nodes with block attribute
    # while checking that ints are not mixed with iterables
    try:
        for (i, block) in enumerate(blocks):
            G.add_nodes_from(block, block=i)
    except TypeError:
        raise nx.NetworkXError("Arguments must be all ints or all iterables")

    # Across blocks, all vertices should be adjacent.
    # We can use itertools.combinations() because undirected.
    for block1, block2 in itertools.combinations(blocks, 2):
        G.add_edges_from(itertools.product(block1, block2))
    return G
