import __init__

from utils import db_utils


# the idea is  the following:
# user wants to redir or provide smth like this: localhost  /select/Sys_Services, where in Harvested_Routes
# you will find only /select/<*>. Having in mind we could potentially have /selec or whatever, we need to find as close
# match to what user wants (as close?) as possible

# Note: this function returns strict similarity. Meaning, if Fuse has .../select/aboba/from/petals (4 levels)
# and user searches for /select, then he will get nothing. The length of levels is compared. Dynamic values from
# endpoints are saved as '<*>' in DB, basically meaning here: could match to anything
def find_valid_route(users_route):
    users_route_segmented = str(users_route).split('/')
    users_route_len = len(users_route_segmented)
    routes_from_db = db_utils.select_from_table('Harvested_Routes')
    routes_from_db_processed = []
    similar_routes = []
    for route in routes_from_db:
        segmented_route = str(route['route']).split('/')
        routes_from_db_processed.append({'service_name': route['service_name'], 'service_saved_route': route['route'],
                                         'service_segmented_route': segmented_route,
                                         'function_name': route['function_name']})

    for route in routes_from_db_processed:
        #     first there is sense to compare lengths and ignore non matching
        if users_route_len == len(route['service_segmented_route']):
            #         next, we need to compare sections that are not <*>
            all_sections_match = True
            for section_from_list, users_section in zip(route['service_segmented_route'], users_route_segmented):
                if section_from_list != '<*>':
                    if section_from_list != users_section:
                        all_sections_match = False
            #       if all sections match, add route to result list
            if all_sections_match:
                similar_routes.append(route)
    return similar_routes
