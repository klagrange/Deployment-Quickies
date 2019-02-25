"""this is the main for health-check
"""
import core as cal
import post_processor as pp

def main(input_data: dict):
    """ Main function for health-check """
    priority = input_data.get('priority', 3)
    annual_investment = float(input_data['annualInvestment'])
    initial_investment = float(input_data['initialInvestment'])

    # Process data and run algorithm
    goals_org, goal_priority, goal_id, years, frontend_fee, backend_fee, manage_fee = (
        [] for i in range(7))
    ir_per_goal_org, ir_per_goal, sigma, goals = ([] for i in range(4))

    for i in range(len(input_data['goals'])):
        goals_org.append(float(input_data['goals'][i]['goalValue']))
        goal_priority.append(int(input_data['goals'][i]['goalPriority']))
        goal_id.append(input_data['goals'][i]['goalID'])
        years.append(int(input_data['goals'][i]['goalDuration']))
        frontend_fee.append(float(input_data['goals'][i]['frontendFee']))
        backend_fee.append(float(input_data['goals'][i]['backendFee']))
        manage_fee.append(float(input_data['goals'][i]['manageFee']))
        ir_per_goal_org.append(
            float(input_data['goals'][i]['discreteExpectedReturn']))
        sigma.append(float(input_data['goals'][i]
                           ['discreteStandardDeviation']))

    goals = [a / (1 - b) for a, b in zip(goals_org, backend_fee)]

    if len(set(goal_id)) < len(goals):
        return (False, {
            'error': 'goals can not have same id, please try again',
            'status_code': 400
        })

    if len(set(goal_priority)) < len(goals):
        return (False, {
            'error': 'goals can not have same priority, please try again',
            'status_code': 400
        })

    ir_per_goal = [a - b for a, b in zip(ir_per_goal_org, manage_fee)]
    years, goal_priority, goals, ir_per_goal, frontend_fee, backend_fee, manage_fee, sigma = \
        (list(t) for t in zip(*sorted(zip(years, goal_priority, goals, ir_per_goal, \
            frontend_fee, backend_fee, manage_fee, sigma))))

    if priority == 1:
        target_met, shortfall_list, surplus_list, prob_list, goals_list = cal.calculator_ai_equal(
            goals, years, annual_investment, ir_per_goal, frontend_fee, sigma)
    elif priority == 2:
        target_met, shortfall_list, surplus_list, prob_list, goals_list = \
            cal.calculator_ai_priority(
                goals, goal_priority, years, annual_investment, ir_per_goal, frontend_fee, sigma)
        # print('surplus_list',surplus_list)
    elif priority == 3:
        target_met, shortfall_list, surplus_list, prob_list, goals_list = \
            cal.calculator_ii_ai_equal(goals, years, initial_investment, \
                annual_investment, ir_per_goal, frontend_fee, sigma)
        # print('surplus_list',surplus_list)
    elif priority == 4:
        target_met, shortfall_list, surplus_list, prob_list, goals_list = \
            cal.calculator_ii_ai_priority(goals, goal_priority, years, \
                initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
    elif priority == 5:
        target_met, shortfall_list, surplus_list, prob_list, goals_list = \
            cal.calculator_ii_equal_ai_priority(goals, goal_priority, years, \
                initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
    elif priority == 6:
        target_met, shortfall_list, surplus_list, prob_list, goals_list = \
            cal.calculator_ii_priority_ai_equal(goals, goal_priority, years, \
                initial_investment, annual_investment, ir_per_goal, frontend_fee, sigma)
    # else: abort(400, "Invalid priority number, please try again!")

    output_dict = pp.output_for_json(
        goals_org,
        goal_id,
        goal_priority,
        years,
        annual_investment,
        initial_investment,
        ir_per_goal_org,
        backend_fee,
        frontend_fee,
        manage_fee,
        sigma,
        goals_list,
        shortfall_list,
        surplus_list,
        prob_list,
        target_met)

    return (True, output_dict)
