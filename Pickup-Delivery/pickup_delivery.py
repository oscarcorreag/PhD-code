def demand_exists(schedule):
    for customers in schedule['demand'].values():
        if len(customers) > 0:
            return True
    return False


class PickupDelivery:
    def __init__(self, graph, depots):
        self.graph = graph.copy()
        self.depots = depots.copy()

    def compute_schedules(self, drivers, customers):
        schedules_per_driver = dict()
        demand = dict()
        # customer[0] corresponds to node
        # customer[1] corresponds to product
        for node, product in customers:
            if product in demand:
                demand[product].add(node)
            else:
                demand[product] = {node}
        for driver in drivers:
            driver_info = {'demand': demand, 'schedule': list(), 'products': set()}
            schedules_per_driver[driver] = self.spawn_schedules(driver_info)
        print schedules_per_driver

    def spawn_schedules(self, current_driver_info):
        new_branches_driver_info = list()
        if not demand_exists(current_driver_info):
            return [current_driver_info['schedule']]
        for product in current_driver_info['products']:
            for customer in current_driver_info['demand'][product]:
                new_branch_driver_info = current_driver_info.copy()
                new_branch_driver_info['schedule'].append(customer[0])  # customer[0] corresponds to node
                new_branch_driver_info['demand'][product].remove(customer)
                if len(current_driver_info['demand'][product]) == 1:
                    new_branch_driver_info['products'].remove(product)
                new_branches_driver_info.append(new_branch_driver_info)
        for product in current_driver_info['demand']:
            if product not in current_driver_info['products']:
                depot = self.depots[product]  # One depot per product
                new_branch_driver_info = current_driver_info.copy()
                new_branch_driver_info['schedule'].append(depot[0])  # depot[0] corresponds to node
                new_branch_driver_info['products'].add(product)
                new_branches_driver_info.append(new_branch_driver_info)
        schedules = list()
        for new_branch in new_branches_driver_info:
            temp = self.spawn_schedules(new_branch)
            schedules.extend(temp)
        return schedules
