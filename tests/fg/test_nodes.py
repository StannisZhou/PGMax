import re

import numpy as np
import pytest

from pgmax.factors import enumeration, logical
from pgmax.fg import nodes


def test_enumeration_factor():
    variable = nodes.Variable(3)

    with pytest.raises(
        NotImplementedError, match="Please implement compile_wiring in for your factor"
    ):
        nodes.Factor(
            variables=(variable,),
            log_potentials=np.array([0.0]),
        )

    with pytest.raises(ValueError, match="Configurations should be integers. Got"):
        enumeration.EnumerationFactor(
            variables=(variable,),
            factor_configs=np.array([[1.0]]),
            log_potentials=np.array([0.0]),
        )

    with pytest.raises(ValueError, match="Potential should be floats. Got"):
        enumeration.EnumerationFactor(
            variables=(variable,),
            factor_configs=np.array([[1]]),
            log_potentials=np.array([0]),
        )

    with pytest.raises(ValueError, match="factor_configs should be a 2D array"):
        enumeration.EnumerationFactor(
            variables=(variable,),
            factor_configs=np.array([1]),
            log_potentials=np.array([0.0]),
        )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Number of variables 1 doesn't match given configurations (1, 2)"
        ),
    ):
        enumeration.EnumerationFactor(
            variables=(variable,),
            factor_configs=np.array([[1, 2]]),
            log_potentials=np.array([0.0]),
        )

    with pytest.raises(
        ValueError, match=re.escape("Expected log potentials of shape (1,)")
    ):
        enumeration.EnumerationFactor(
            variables=(variable,),
            factor_configs=np.array([[1]]),
            log_potentials=np.array([0.0, 1.0]),
        )

    with pytest.raises(ValueError, match="Invalid configurations for given variables"):
        enumeration.EnumerationFactor(
            variables=(variable,),
            factor_configs=np.array([[10]]),
            log_potentials=np.array([0.0]),
        )


def test_logical_factor():
    child = nodes.Variable(2)
    wrong_parent = nodes.Variable(3)
    parent = nodes.Variable(2)

    with pytest.raises(
        ValueError,
        match="At least one parent variable and one child variable is required",
    ):
        logical.LogicalFactor(
            variables=(child,),
        )

    with pytest.raises(ValueError, match="All variables should all be binary"):
        logical.LogicalFactor(
            variables=(wrong_parent, child),
        )

    logical_factor = logical.LogicalFactor(
        variables=(parent, child),
    )
    num_parents = len(logical_factor.variables) - 1
    parents_edge_states = np.vstack(
        [
            np.zeros(num_parents, dtype=int),
            np.arange(0, 2 * num_parents, 2, dtype=int),
        ],
    ).T
    child_edge_state = np.array([2 * num_parents], dtype=int)

    with pytest.raises(ValueError, match="The highest LogicalFactor index must be 0"):
        logical.LogicalWiring(
            edges_num_states=logical_factor.edges_num_states,
            var_states_for_edges=None,
            parents_edge_states=parents_edge_states + np.array([[1, 0]]),
            children_edge_states=child_edge_state,
            edge_states_offset=1,
        )

    with pytest.raises(
        ValueError,
        match="The LogicalWiring must have 1 different LogicalFactor indices",
    ):
        logical.LogicalWiring(
            edges_num_states=logical_factor.edges_num_states,
            var_states_for_edges=None,
            parents_edge_states=parents_edge_states + np.array([[0], [1]]),
            children_edge_states=child_edge_state,
            edge_states_offset=1,
        )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "The LogicalWiring's edge_states_offset must be 1 (for OR) and -1 (for AND), but is 0"
        ),
    ):
        logical.LogicalWiring(
            edges_num_states=logical_factor.edges_num_states,
            var_states_for_edges=None,
            parents_edge_states=parents_edge_states,
            children_edge_states=child_edge_state,
            edge_states_offset=0,
        )
