#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intended workflow for mortars:
    1) Create a full grid bucket of all objects to be included.
    2) Somehow create new grids for (some of) the nodes in the bucket.
    3) Find relation between new grid and neighboring grids.
    4) Replace nodes in the bucket
    5) Replace projection operators located on grid_bucket edges.

Implementation needs:
    1) Initialize identity (whatever that means) projections when a grid
       bucket is created.
    2) Create a framework for modifying grids. In the first stage this will
       involve perturbing nodes (not on the boundary). Second stage shoud be
       refinements of simplex grids. Partial remeshing with other parameters
       should also be on the list.
       -> Partly solved by grids.refinement.
    3) Methods to match cells and faces from different grids.
       -> First attempt in relate_1d_and_2d_grids()
    4) Creation of general projection matrices. Closely related to
    5) Numerical methods that can handle general projections.

Created on Sat Nov 11 16:22:36 2017

@author: Eirik Keilegavlen
"""

import numpy as np

from porepy.fracs import non_conforming
from porepy.utils.matrix_compression import rldecode


def match_grids_1d(new_1d, old_1d):
     """ Obtain mappings between the cells of non-matching 1d grids.

     The function constructs an refined 1d grid that consists of all nodes
     of at least one of the input grids.

     It is asumed that the two grids are aligned, with common start and
     endpoints.

     Implementation note: It should be possible to avoid old_1d, by extracting
     points from a 2D grid that lie along the line defined by g_1d.
     However, if g_2d is split along a fracture, the nodes will be
     duplicated. We should then return two grids, probably based on the
     coordinates of the cell centers. sounds cool.

     Parameters:
          new_1d (grid): First grid to be matched
          old_1d (grid): Second grid to be matched.

     Returns:
          np.array: Cell volume in the common grid.
          np.array: Mapping between cell numbers in common and first input
               grid.
          np.array: Mapping between cell numbers in common and second input
               grid.

     """

     # Create a grid that contains all nodes of both the old and new grids.
     combined, _, new_ind, old_ind, _, _ = \
          non_conforming.merge_1d_grids(new_1d, old_1d)
     combined.compute_geometry()

     weights = combined.cell_volumes

     switch_new = new_ind[0] > new_ind[-1]
     if switch_new:
          new_ind = new_ind[::-1]
     switch_old = old_ind[0] > old_ind[-1]
     if switch_old:
          old_ind = old_ind[::-1]

     diff_new = np.diff(new_ind)
     diff_old = np.diff(old_ind)
     new_in_full = rldecode(np.arange(diff_new.size), diff_new)
     old_in_full = rldecode(np.arange(diff_old.size), diff_old)

     if switch_new:
          new_in_full = new_in_full.max() - new_in_full
     if switch_old:
          old_in_full = old_in_full.max() - old_in_full


     return weights, new_in_full, old_in_full

