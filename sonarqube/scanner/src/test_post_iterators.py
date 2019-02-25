#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 11:05:11 2018

@author: liujin
"""
import unittest
import numpy as np
import post_iterators as it

class Test_post_iterators(unittest.TestCase):
    """
    test post_iterators
    """
    priority = 4
    goals = [51020.40816326531, 102040.81632653062, 204081.63265306124]
    goal_priority = [1, 2, 3]
    years = [5, 10, 15]
    ir_per_goal = [0.06, 0.06, 0.06]
    sigma = [0.10, 0.20, 0.40]
    frontend_fee = [0.02, 0.02, 0.02]
    backend_fee = [0.02, 0.02, 0.02]
    manage_fee = [0.02, 0.02, 0.02]
    shortfall_list_org = [0.0000, 0.0000, 113523.5535]
    target_met = [1, 1, 0]

    initial_investment = 20000
    annual_investment = 12000

    def test_adjusting_goals_iter(self):
        """
        test adjusting_goals_iter function
        """
        shortfall_list = [0.0000, 0.0000, 113523.5535]
        target_met = [1, 1, 0]
        goals_adjusted = [50000.0, 100000.0, 88746.91756895816]

        target_met, shortfall_list, surplus_list, probs_list, goals_list, goals_adjusted_test = \
            it.adjusting_goals_iter(
                self.priority, self.goals, self.goal_priority,
                self.years, self.initial_investment,
                self.annual_investment, self.ir_per_goal,
                self.sigma, self.frontend_fee, self.backend_fee, target_met, shortfall_list)

        for i in range(len(goals_adjusted)):
            self.assertEqual(round(goals_adjusted[i], 4), round(goals_adjusted_test[i], 4))

    def test_adjusting_years_iter(self):
        """
        test adjusting_years_iter
        """
        priority = 4
        goals = [51020.40816326531, 102040.81632653062, 204081.63265306124]
        goal_priority = [1, 2, 3]
        years = [5, 10, 15]
        ir_per_goal = [0.06, 0.06, 0.06]
        sigma = [0.10, 0.20, 0.40]
        frontend_fee = [0.02, 0.02, 0.02]

        shortfall_list_org = [0.0000, 0.0000, 113523.5535]
        target_met = [1, 1, 0]

        initial_investment = 20000
        annual_investment = 12000
        years_adjusted = [5, 10, 21]

        years_adjusted_test = []

        target_met, shortfall_list, surplus_list, probs_list, goals_list, years_adjusted_test = \
            it.adjusting_years_iter(
                priority, goals, goal_priority,
                years, initial_investment,
                annual_investment, ir_per_goal,
                sigma, frontend_fee, target_met, shortfall_list_org)

        self.assertListEqual(years_adjusted, years_adjusted_test)

    def test_adjusting_irs_iter(self):
        """
        test adjusting_irs_iter
        """
        target_met = [1, 1, 0]
        shortfall_list = [0.0000, 0.0000, 113523.5535]
        surplus_list = [4148.8451, 8200.2321, 0.0000]
        ir_adjusted = [0.0800, 0.0800, 0.3509]
        ir_adjusted_test = np.array(len(ir_adjusted), dtype=float)

        ir_adjusted_test, goals_list, target_met, shortfall_list, \
            surplus_list, probs_list, annual_investment = it.adjusting_irs_iter(\
                self.priority, self.goals, self.goal_priority,\
                self.years, self.ir_per_goal,\
                target_met, shortfall_list, surplus_list,\
                self.annual_investment, self.initial_investment,\
                self.frontend_fee, self.manage_fee, self.sigma)

        for i in range(len(ir_adjusted)):
            self.assertEqual(round(ir_adjusted_test[i], 4), ir_adjusted[i])

    def test_adjusting_annual_investment(self):
        """
        test adjusting_annual_investment
        """
        target_met = [1, 1, 0]
        shortfall_list = [0.0000, 0.0000, 113523.5535]
        #surplus_list = [3914.0048, 7736.0681, 0.0000]

        adjusted_annual_investment = 16879.2849
        target_met, shortfall_list, surplus_list, probs_list, goals_list, annual_investment = \
            it.adjusting_annual_investment(
                self.priority, self.goals, self.goal_priority,
                self.years, self.initial_investment,
                self.annual_investment, self.ir_per_goal, self.sigma,
                self.frontend_fee, target_met, shortfall_list)

        self.assertEqual(round(annual_investment, 4), adjusted_annual_investment)

    def test_adjusting_initial_investment(self):
        """
        test adjusting_initial_investment
        """
        priority = 4
        target_met = [1, 1, 0]
        shortfall_list = [0.0000, 0.0000, 113523.5535]
        #surplus_list = [3914.0048, 7736.0681, 0.0000]
        adjusted_initial_investment = 67373.7482
        target_met, shortfall_list, surplus_list, probs_list, goals_list, initial_investment = \
            it.adjusting_initial_investment(
                priority, self.goals, self.goal_priority,
                self.years, self.initial_investment,
                self.annual_investment, self.ir_per_goal,
                self.sigma, self.frontend_fee, target_met, shortfall_list)

        self.assertEqual(round(initial_investment, 4), adjusted_initial_investment)

    def test_adjusting_goal_priority(self):
        """
        test adjusting_goal_priority
        """
        priority = 4
        target_met = [1, 1, 0]
        shortfall_list = [0.0000, 0.0000, 113523.5535]
        surplus_list = [4148.8451, 8200.2321, 0.0000]
        probs_list = [0.934808, 0.894431, 0.5506]

        adjusted_goal_priority = [1, 3, 2]

        goal_priority_adjusted, goals_list, target_met, shortfall_list, \
        surplus_list, probs_list, annual_investment = it.adjusting_goal_priority(\
                priority, self.goals, \
                self.years, target_met, self.annual_investment,\
                self.initial_investment,\
                self.ir_per_goal,\
                self.sigma, self.frontend_fee,\
                shortfall_list, surplus_list, probs_list)

        self.assertListEqual(adjusted_goal_priority, goal_priority_adjusted)

if __name__ == '__main__':
    unittest.main()
