# -*- coding: utf-8 -*-

"""
Swarm Operation Backend

This module abstracts various operations in the swarm such as updating
the personal best, finding neighbors, etc. You can use these methods
to specify how the swarm will behave.
"""

<<<<<<< HEAD
=======
# Import from stdlib
import logging

>>>>>>> f0e6a49... [WIP-operator] Add update_gbest_neighborhood to operators
# Import modules
import logging
import numpy as np
from scipy.spatial import cKDTree

# Create a logger
logger = logging.getLogger(__name__)

def update_pbest(swarm):
    """Takes a swarm instance and updates the personal best scores
    
    You can use this method to update your personal best positions.

    ..code-block :: python

        import pyswarms.backend as P
        from pyswarms.backend.swarms import Swarm

        my_swarm = P.create_swarm(n_particles, dimensions)

        # Inside the for-loop...
        for i in range(iters):
            # It updates the swarm internally
            my_swarm.pbest_pos, my_swarm.pbest_cost = P.update_pbest(my_swarm)

    It updates your :code:`current_pbest` with the personal bests acquired by
    comparing the (1) cost of the current positions and the (2) personal
    bests your swarm has attained.
    
    If the cost of the current position is less than the cost of the personal
    best, then the current position replaces the previous personal best
    position.

    Parameters
    ----------
    swarm : pyswarms.backend.swarm.Swarm
        a Swarm instance

    Returns
    -------
    numpy.ndarray
        New personal best positions of shape :code:`(n_particles, n_dimensions)`
    numpy.ndarray
        New personal best costs of shape :code:`(n_particles,)`
    """
    try:
        # Infer dimensions from positions
        dimensions = swarm.dimensions
        # Create a 1-D and 2-D mask based from comparisons
        mask_cost = (swarm.current_cost < swarm.pbest_cost)
        mask_pos = np.repeat(mask_cost[:, np.newaxis], swarm.dimensions, axis=1)
        # Apply masks
        new_pbest_pos = np.where(~mask_pos, swarm.pbest_pos, swarm.position)
        new_pbest_cost = np.where(~mask_cost, swarm.pbest_cost, swarm.current_cost)
    except AttributeError:
        msg = 'Please pass a Swarm class. You passed {}'.format(type(swarm))
        logger.error(msg)
        raise
    else:
        return (new_pbest_pos, new_pbest_cost)

def update_gbest(swarm):
    """Updates the global best given the cost and the position

    This method takes the current pbest_pos and pbest_cost, then returns
    the minimum cost and position from the matrix. It should be used in
    tandem with an if statement

    .. code-block:: python

        import pyswarms.backend as P
        from pyswarms.backend.swarms import Swarm

        my_swarm = P.create_swarm(n_particles, dimensions)

        # If the minima of the pbest_cost is less than the best_cost
        if np.min(pbest_cost) < best_cost:
            # Update best_cost and position
            swarm.best_pos, swarm.best_cost = P.update_gbest(my_swarm)

    Parameters
    ----------
    swarm : pyswarms.backend.swarm.Swarm
        a Swarm instance

    Returns
    -------
    numpy.ndarray
        Best position of shape :code:`(n_dimensions, )`
    float
        Best cost
    """
    try:
        best_pos = swarm.pbest_pos[np.argmin(swarm.pbest_cost)]
        best_cost = np.min(swarm.pbest_cost)
    except AttributeError:
        msg = 'Please pass a Swarm class. You passed {}'.format(type(swarm))
        logger.error(msg)
        raise
    else:
        return (best_pos, best_cost)

def update_gbest_neighborhood(swarm, p, k):
    """Updates the global best using a neighborhood approach

    This uses the cKDTree method from :code:`scipy` to obtain the nearest
    neighbours

    Parameters
    ----------
    swarm : pyswarms.backend.swarms.Swarm
        a Swarm instance
    k : int
        number of neighbors to be considered. Must be a
        positive integer less than :code:`n_particles`
    p: int {1,2}
        the Minkowski p-norm to use. 1 is the
        sum-of-absolute values (or L1 distance) while 2 is
        the Euclidean (or L2) distance.

    Returns
    -------
    numpy.ndarray
        Best position of shape :code:`(n_dimensions, )`
    float
        Best cost
    """
    try:
        # Obtain the nearest-neighbors for each particle
        tree = cKDTree(swarm.position)
        _, idx = tree.query(swarm.position, p=p, k=k)

        # Map the computed costs to the neighbour indices and take the
        # argmin. If k-neighbors is equal to 1, then the swarm acts
        # independently of each other.
        if k == 1:
            # The minimum index is itself, no mapping needed.
            best_neighbor = swarm.pbest_cost[idx][:, np.newaxis].argmin(axis=1)
        else:
            idx_min = swarm.pbest_cost[idx].argmin(axis=1)
            best_neighbor = idx[np.arange(len(idx)), idx_min]
        # Obtain best cost and position
        best_cost = np.min(swarm.pbest_cost[best_neighbor])
        best_pos = swarm.pbest_pos[np.argmin(swarm.pbest_cost[best_neighbor])]
    except AttributeError:
        msg = 'Please pass a Swarm class. You passed {}'.format(type(swarm))
        logger.error(msg)
        raise
    else:
        return (best_pos, best_cost)

def update_velocity(swarm, clamp):
    """Updates the velocity matrix

    This method updates the velocity matrix using the best and current
    positions of the swarm. The velocity matrix is computed using the
    cognitive and social terms of the swarm.
    
    A sample usage can be seen with the following:

    .. code-block :: python

        import pyswarms.backend as P
        from pyswarms.swarms.backend import Swarm

        my_swarm = P.create_swarm(n_particles, dimensions)

        for i in range(iters):
            # Inside the for-loop
            my_swarm.velocity = update_velocity(my_swarm, clamp)

    Parameters
    ----------
    swarm : pyswarms.backend.swarms.Swarm
        a Swarm instance
    clamp : tuple of floats (default is :code:`None`)
        a tuple of size 2 where the first entry is the minimum velocity
        and the second entry is the maximum velocity. It
        sets the limits for velocity clamping.

    Returns
    -------
    numpy.ndarray
        Updated velocity matrix
    """
    try:
        # Prepare parameters
        swarm_size = swarm.position.shape
        c1 = swarm.behavior['c1']
        c2 = swarm.behavior['c2']
        w = swarm.behavior['w']
        # Compute for cognitive and social terms
        cognitive = (c1 * np.random.uniform(0,1, swarm_size) * (swarm.pbest_pos - swarm.position))
        social = (c2 * np.random.uniform(0, 1, swarm_size) * (swarm.best_pos - swarm.position))
        # Compute temp velocity (subject to clamping if possible)
        temp_velocity = (w * swarm.velocity) + cognitive + social

        if clamp is None:
            updated_velocity = temp_velocity
        else:
            min_velocity, max_velocity = clamp
            mask = np.logical_and(temp_velocity >= min_velocity,
                                temp_velocity <= max_velocity)
            updated_velocity = np.where(~mask, swarm.velocity, temp_velocity)
    except AttributeError:
        msg = 'Please pass a Swarm class. You passed {}'.format(type(swarm))
        logger.error(msg)
        raise
    except KeyError:
        msg = 'Missing keyword in swarm.behavior'
        logger.error(msg)
        raise
    else:
        return updated_velocity

def update_position(swarm, bounds):
    """Updates the position matrix

    This method updates the position matrix given the current position and
    the velocity. If bounded, it waives updating the position.

    Parameters
    ----------
    swarm : pyswarms.backend.swarms.Swarm
        a Swarm instance
    bounds : tuple of :code:`np.ndarray` or list (default is :code:`None`)
        a tuple of size 2 where the first entry is the minimum bound while
        the second entry is the maximum bound. Each array must be of shape
        :code:`(dimensions,)`.

    Returns
    -------
    numpy.ndarray
        New position-matrix
    """
    try:
        temp_position = swarm.position.copy()
        temp_position += swarm.velocity

        if bounds is not None:
            lb, ub = bounds
            min_bounds = np.repeat(np.array(lb)[np.newaxis, :], swarm.n_particles, axis=0)
            max_bounds = np.repeat(np.array(ub)[np.newaxis, :], swarm.n_particles, axis=0)
            mask = (np.all(min_bounds <= temp_position, axis=1)
                * np.all(temp_position <= max_bounds, axis=1))
            mask = np.repeat(mask[:, np.newaxis], swarm.dimensions, axis=1)
            temp_position = np.where(~mask, swarm.position, temp_position)
        position = temp_position
    except AttributeError:
        msg = 'Please pass a Swarm class. You passed {}'.format(type(swarm))
        logger.error(msg)
        raise
    else:
        return position
