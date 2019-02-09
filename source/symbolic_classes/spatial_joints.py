# -*- coding: utf-8 -*-
"""
Created on Tue Jan  1 11:11:10 2019

@author: khale
"""

import sympy as sm


from source.symbolic_classes.abstract_matrices import (reference_frame, vector,
                                                       zero_matrix)

from source.symbolic_classes.algebraic_constraints import (algebraic_constraints,
                                                           joint_constructor,
                                                           joint_actuator,
                                   spehrical_constraint, dot_product_1, dot_product_2,
                                   angle_constraint, coordinate_constraint,
                                   absolute_actuator)


class fixed(algebraic_constraints,metaclass=joint_constructor):
    def_axis = 1
    def_locs = 1
    vector_equations = [spehrical_constraint(),
                        dot_product_1('i','k'),
                        dot_product_1('j','k'),
                        dot_product_1('i','j')]

class spherical(algebraic_constraints,metaclass=joint_constructor):
    def_axis = 1
    def_locs = 1
    vector_equations = [spehrical_constraint()]

class revolute(algebraic_constraints,metaclass=joint_constructor):
    def_axis = 1
    def_locs = 1
    vector_equations = [spehrical_constraint(),
                        dot_product_1('i','k'),
                        dot_product_1('j','k')]

class cylinderical(algebraic_constraints,metaclass=joint_constructor):
    def_axis = 1
    def_locs = 1
    vector_equations = [dot_product_1('i','k'),
                        dot_product_1('j','k'),
                        dot_product_2('i'),
                        dot_product_2('j')]
    
class translational(algebraic_constraints,metaclass=joint_constructor):
    def_axis = 1
    def_locs = 1
    vector_equations = [dot_product_1('i','k'),
                        dot_product_1('j','k'),
                        dot_product_2('i'),
                        dot_product_2('j'),
                        dot_product_1('i','j')]

class universal(algebraic_constraints,metaclass=joint_constructor):
    def_axis = 2
    def_locs = 1
    vector_equations = [spehrical_constraint(),
                        dot_product_1('i','i')]
    
        


class rotational_actuator(joint_actuator,metaclass=joint_constructor):
    def_axis = 1
    def_locs = 0
    vector_equations = [angle_constraint()]
    
    @property
    def pos_level_equations(self):
        return sm.BlockMatrix(self._pos_level_equations)


class absolute_locator(absolute_actuator,metaclass=joint_constructor):
    def_axis = 0
    def_locs = 0
    vector_equations = [coordinate_constraint()]

class dummy_cylinderical(algebraic_constraints,metaclass=joint_constructor):
    def_axis = 1
    def_locs = 2
    vector_equations = [dot_product_1('i','k'),
                        dot_product_1('j','k'),
                        dot_product_2('i'),
                        dot_product_2('j')]
    
