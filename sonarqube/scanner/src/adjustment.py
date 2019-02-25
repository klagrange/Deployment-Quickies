"""this is the main for adjustment
"""
import post_iterators as it
import post_processor as pp
"""module doing iteration for the adjustment and post processing
"""

def main(input_data: dict):
    """ Main function for adjustment """
    priority = input_data['priority']
    adjustment = input_data['adjustment']
    annual_investment = input_data['annualInvestment']
    initial_investment = input_data['initialInvestment']

    frontend_fee, backend_fee, manage_fee, shortfall_list, surplus_list, ir_per_goal_org, sigma = ([
    ] for i in range(7))
    goals_org, goals, goal_id, goal_priority, years, target_met = (
        [] for i in range(6))

    for i in range(len(input_data['goals'])):
        goals_org.append(float(input_data['goals'][i]['goalValue']))
        years.append(int(input_data['goals'][i]['goalDuration']))
        frontend_fee.append(float(input_data['goals'][i]['frontendFee']))
        backend_fee.append(float(input_data['goals'][i]['backendFee']))
        manage_fee.append(float(input_data['goals'][i]['manageFee']))
        ir_per_goal_org.append(
            float(input_data['goals'][i]['discreteExpectedReturn']))
        sigma.append(float(input_data['goals'][i]
                           ['discreteStandardDeviation']))
        shortfall_list.append(float(input_data['goals'][i]['shortfall']))
        surplus_list.append(float(input_data['goals'][i]['surplus']))
        goal_id.append(input_data['goals'][i]['goalID'])
        goal_priority.append(input_data['goals'][i]['goalPriority'])
        
        if float(input_data['goals'][i]['shortfall'])>0.01:
            if input_data['goals'][i]['isAchieved'] == True:
                return (False, {
                        'data': {
                                'error': 'there is shortfall, please check the "isAchieved" value'
                                },
                        'status_code': 400})
        if float(input_data['goals'][i]['shortfall'])<0.01:
            if input_data['goals'][i]['isAchieved'] == False:
                return (False, {
                        'data': {
                                'error': 'there is no shortfall, please check the "isAchieved" value'
                                },
                        'status_code': 400})    
    
        if input_data['goals'][i]['isAchieved']:
            target_met.append(1)
        else:
            target_met.append(0)
        #temp = input_data['goals'][i]['annualBreakdown']
        #j = input_data['goals'][i]['goalDuration'] - 1
        #ai_last.append(float(temp[j]['actualInvestment']))

    goals = [a / (1 - b) for a, b in zip(goals_org, backend_fee)]
    ir_per_goal = [a - b for a, b in zip(ir_per_goal_org, manage_fee)]

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

    # main body for the adjustment
    output_dict = {}
    if adjustment == 1:
        target_met, shortfall_list, surplus_list, probs_list, goals_list, goals_adjusted = \
            it.adjusting_goals_iter(priority, goals, goal_priority, years, initial_investment, \
                annual_investment, ir_per_goal, sigma, frontend_fee, backend_fee, \
                target_met, shortfall_list)
        output_dict = pp.output_for_json(
            goals_adjusted,
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
            probs_list,
            target_met)

    elif adjustment == 2:
        target_met, shortfall_list, surplus_list, probs_list, goals_list, years_adjusted = \
            it.adjusting_years_iter(priority, goals, goal_priority, years, initial_investment, \
                annual_investment, ir_per_goal, sigma, frontend_fee, target_met, shortfall_list)
        output_dict = pp.output_for_json(
            goals_org,
            goal_id,
            goal_priority,
            years_adjusted,
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
            probs_list,
            target_met)

    elif adjustment == 3:
        ir_adjusted, goals_list, target_met, shortfall_list, \
        surplus_list, probs_list, annual_investment = \
            it.adjusting_irs_iter(priority, goals, goal_priority, years, ir_per_goal, \
                target_met, shortfall_list, surplus_list, annual_investment, initial_investment, \
                frontend_fee, manage_fee, sigma)
        output_dict = pp.output_for_json(
            goals_org,
            goal_id,
            goal_priority,
            years,
            annual_investment,
            initial_investment,
            ir_adjusted,
            backend_fee,
            frontend_fee,
            manage_fee,
            sigma,
            goals_list,
            shortfall_list,
            surplus_list,
            probs_list,
            target_met)

    elif adjustment == 4:
        target_met, shortfall_list, surplus_list, probs_list, goals_list, annual_investment = \
            it.adjusting_annual_investment(priority, goals, goal_priority, years, \
                initial_investment, annual_investment, ir_per_goal, sigma, \
                frontend_fee, target_met, shortfall_list)
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
            probs_list,
            target_met)

    elif adjustment == 5:
        if priority == 1 or priority == 2:
            return (False, {
                'error': 'This priority does not have the adjustment method of 5',
                'status_code': 400
            })
        else:
            target_met, shortfall_list, surplus_list, probs_list, goals_list, initial_investment = \
                it.adjusting_initial_investment(priority, goals, goal_priority, years, \
                initial_investment, annual_investment, ir_per_goal, sigma, \
                frontend_fee, target_met, shortfall_list)
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
                probs_list,
                target_met)

    elif adjustment == 6:
        if priority in (1, 3):
            return (False, {
                'error': 'This priority does not have the adjustment method of 6',
                'status_code': 400
            })

        goal_priority_adjusted, goals_list, target_met, shortfall_list, \
        surplus_list, probs_list, annual_investment = \
            it.adjusting_goal_priority(priority, goals, goal_priority, years, target_met, \
                annual_investment, initial_investment, ir_per_goal, sigma, \
                frontend_fee, shortfall_list, surplus_list)

        output_dict = pp.output_for_json(
            goals_org,
            goal_id,
            goal_priority_adjusted,
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
            probs_list,
            target_met)

    return (True, output_dict)
